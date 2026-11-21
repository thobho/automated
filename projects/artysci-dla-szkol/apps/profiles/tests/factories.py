"""Test data for the profile generator: a seed artist with ready materials (synthetic text only,
D12: no copies of real artists' materials) and a profile JSON that matches the v0.2 schema."""

from apps.accounts.tests.conftest import make_artist
from apps.artists.models import Artist, Material, Offer, ScanStatus, VideoFrame
from apps.trust import services as trust
from apps.trust.models import LegalDocument

SITE_EMAIL = "kontakt@example.invalid"


def valid_profile(**overrides) -> dict:
    profile = {
        "hero": {
            "headline": "Teatr Kwiatki",
            "subheadline": "Spektakle dla przedszkoli i klas 0–3",
            "main_photo_id": None,
            "button_label": "Sprawdź termin",
        },
        "facts": [{"label": "Czas", "value": "45 min"}],
        "description": {"paragraphs": ["Opis testowy."]},
        "schools": {
            "headline": "Dla szkół i przedszkoli",
            "points": ["Dopasowanie do wieku"],
            "age_range": "4–9 lat",
            "requirements": [],
        },
        "offers": [],
        "gallery": {"photo_ids": [], "video_ids": [], "captions": []},
        "testimonials": [],
        "faq": [{"question": "Ile trwa spektakl?", "answer": "45 minut."}],
        "theme": "cream_green",
        "seo": {"title": "Teatr Kwiatki", "description": "Spektakle dla dzieci."},
        "gaps": [],
        "claims_audit": [{"claim": "45 min", "source": "questionnaire", "source_id": None}],
    }
    profile.update(overrides)
    return profile


def allow_materials(artist: Artist) -> None:
    """The artist confirms the rights to their materials (a current statement)."""
    if trust.current(LegalDocument.Kind.MATERIAL_RIGHTS) is None:
        trust.publish(LegalDocument.Kind.MATERIAL_RIGHTS, "Treść testowa", material=True)
    trust.make_statement(artist, LegalDocument.Kind.MATERIAL_RIGHTS)


def make_seed_artist(email="artysta.seed@example.invalid", *, consent=True) -> Artist:
    user = make_artist(email)
    artist = Artist.objects.get(user=user)
    artist.name = "Teatr Kwiatki"
    artist.artist_type = "theatre"
    artist.city = "Wrocław"
    artist.q_age_from, artist.q_age_to = 4, 9
    artist.q_duration_minutes = 45
    artist.q_tech_room = f"Sala min. 20 m2, kontakt {SITE_EMAIL}"
    artist.save()
    Offer.objects.create(
        artist=artist, title="Kwiatowa opowieść", description="Spektakl interaktywny.",
        price_pln=1200,
    )  # fmt: skip
    if consent:
        allow_materials(artist)
    return artist


def add_material(artist: Artist, kind: str, **fields) -> Material:
    fields.setdefault("status", ScanStatus.READY)
    return Material.objects.create(artist=artist, kind=kind, **fields)


def add_frame(material: Material, **fields) -> VideoFrame:
    fields.setdefault("storage_key", f"private/frames/{material.pk}.jpg")
    fields.setdefault("checks_version", 1)
    return VideoFrame.objects.create(material=material, **fields)
