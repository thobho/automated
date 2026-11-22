"""What the generator reads about an artist (US-2.5A, D59, D12).

`build_input(artist)` returns a plain dict that becomes the user message of the AI call:

- the artist's basics, questionnaire values and offers (US-2.9);
- the text of the imported website, text of PDFs, titles of video links and videos;
- photos, videos and video frames as ids with flags only: never file bytes, file names or URLs.

Only what counts goes in: materials that are ``ready`` (a deleted row is gone), and only while the
artist has a current "Prawa do materiałów" statement (D4/D7: without it no material of the artist
is used). Text is scrubbed here as well as by the AI adapter, so the input is clean on its own.
"""

from apps.artists import checks, materials
from apps.artists import services as artist_services
from apps.artists.models import Artist, Material, MaterialKind, TextStatus, WebsiteImport
from apps.trust import services as trust
from apps.trust.models import LegalDocument

from .ai.scrub import scrub

PDF_TEXT_STATUSES = (TextStatus.DONE, TextStatus.TRUNCATED)


def materials_allowed(artist: Artist) -> bool:
    """The artist currently confirms the rights to their materials."""
    return any(
        statement.kind == LegalDocument.Kind.MATERIAL_RIGHTS
        for statement in trust.current_statements(artist)
    )


def _flags(material) -> list[str]:
    return sorted({*(material.flags or []), *(getattr(material, "origin_flags", None) or [])})


def _photo(material: Material) -> dict:
    return {
        "id": material.pk,
        "width": material.width,
        "height": material.height,
        "orientation": material.orientation,
        "flags": _flags(material),
        "can_be_main": checks.can_be_main(material),
    }


def _video(material: Material) -> dict:
    return {
        "id": material.pk,
        "kind": material.kind,
        "provider": material.provider,
        "title": scrub(material.title),
        "duration_seconds": material.duration_seconds,
        "flags": _flags(material),
        "frames": [
            {
                "id": frame.pk,
                "position_seconds": frame.position_seconds,
                "orientation": frame.orientation,
                "flags": sorted(frame.flags or []),
                "can_be_main": checks.can_be_main(frame),
            }
            for frame in checks.frames_of(material)
        ],
    }


def _offer(offer) -> dict:
    return {
        "id": offer.pk,
        "title": scrub(offer.title),
        "description": scrub(offer.description),
        "age_from": offer.age_from,
        "age_to": offer.age_to,
        "duration_minutes": offer.duration_minutes,
        "price_pln": offer.price_pln,
        "price_on_request": offer.price_on_request,
    }


def _site_text(artist: Artist) -> str:
    record = (
        WebsiteImport.objects.filter(artist=artist).exclude(text="").order_by("-created_at").first()
    )
    return scrub(record.text) if record else ""


def build_input(artist: Artist) -> dict:
    basics = artist_services.basics_of(artist)
    data = {
        "artist": {
            "name": artist.name,
            "type": artist.artist_type,
            "city": artist.city,
            "voivodeships": list(basics.voivodeships),
            "audiences": list(basics.audiences),
        },
        "questionnaire": {
            key: scrub(value) if isinstance(value, str) else value
            for key, value in materials.questionnaire_of(artist).items()
        },
        "offers": [_offer(offer) for offer in artist_services.offers_for(artist)],
        "site_text": "",
        "documents": [],
        "photos": [],
        "videos": [],
        "audio": [],
    }
    if not materials_allowed(artist):
        return data
    data["site_text"] = _site_text(artist)
    for material in materials.ready_materials(artist).order_by("created_at", "pk"):
        if material.kind == MaterialKind.PDF:
            if material.text_status in PDF_TEXT_STATUSES and material.text:
                data["documents"].append({"id": material.pk, "text": scrub(material.text)})
        elif material.kind == MaterialKind.PHOTO:
            data["photos"].append(_photo(material))
        elif material.kind in (MaterialKind.LINK, MaterialKind.VIDEO):
            data["videos"].append(_video(material))
        elif material.kind == MaterialKind.AUDIO:
            data["audio"].append({"id": material.pk, "duration_seconds": material.duration_seconds})
    return data
