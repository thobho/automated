import json

import pytest

from apps.artists.models import MaterialKind, ScanStatus, TextStatus, WebsiteImport
from apps.profiles import inputs
from apps.trust import services as trust
from apps.trust.models import LegalDocument

from .factories import SITE_EMAIL, add_frame, add_material, make_seed_artist

pytestmark = pytest.mark.django_db


def as_text(data) -> str:
    return json.dumps(data, ensure_ascii=False)


def test_collects_questionnaire_offers_and_ready_materials():
    artist = make_seed_artist()
    photo = add_material(
        artist, MaterialKind.PHOTO, width=2000, height=1200, orientation="landscape",
        flags=["low_resolution"], origin_flags=["no_camera_metadata"], checks_version=1,
        storage_key="private/photo.jpg", original_name="jan-kowalski.jpg",
    )  # fmt: skip
    pdf = add_material(
        artist, MaterialKind.PDF, text="Cennik: 1200 zł.", text_status=TextStatus.DONE
    )
    link = add_material(
        artist, MaterialKind.LINK, provider="youtube", video_id="abcdefghijk", title="Występ"
    )
    video = add_material(artist, MaterialKind.VIDEO, title="Nagranie", duration_seconds=90.0)
    frame = add_frame(video, flags=["blurry"], position_seconds=3.0)

    data = inputs.build_input(artist)

    assert data["artist"]["name"] == "Teatr Kwiatki" and data["artist"]["city"] == "Wrocław"
    assert data["questionnaire"]["q_duration_minutes"] == 45
    assert [o["title"] for o in data["offers"]] == ["Kwiatowa opowieść"]
    assert data["offers"][0]["price_pln"] == 1200
    assert data["documents"] == [{"id": pdf.pk, "text": "Cennik: 1200 zł."}]
    assert [p["id"] for p in data["photos"]] == [photo.pk]
    assert data["photos"][0]["flags"] == ["low_resolution", "no_camera_metadata"]
    assert {v["id"] for v in data["videos"]} == {link.pk, video.pk}
    frames = next(v for v in data["videos"] if v["id"] == video.pk)["frames"]
    assert frames[0]["id"] == frame.pk and frames[0]["flags"] == ["blurry"]


def test_photos_and_videos_carry_no_file_data():
    artist = make_seed_artist()
    add_material(
        artist, MaterialKind.PHOTO, storage_key="private/secret-key.jpg",
        original_name="jan-kowalski.jpg", phash="deadbeef", width=10, height=10,
    )  # fmt: skip
    video = add_material(
        artist, MaterialKind.VIDEO, storage_key="private/v.mp4", converted_key="private/v2.mp4",
        thumbnail_key="private/t.jpg", original_name="wystep.mov",
    )  # fmt: skip
    add_frame(video, storage_key="private/frames/f.jpg")
    text = as_text(inputs.build_input(artist))
    for forbidden in ("secret-key", "jan-kowalski", "v.mp4", "v2.mp4", "t.jpg", "f.jpg", "wystep"):
        assert forbidden not in text


def test_unready_materials_are_left_out():
    artist = make_seed_artist()
    add_material(artist, MaterialKind.PDF, status=ScanStatus.PENDING, text="SEKRET-PENDING",
                 text_status=TextStatus.DONE)  # fmt: skip
    add_material(artist, MaterialKind.PDF, status=ScanStatus.REJECTED, text="SEKRET-REJECTED",
                 text_status=TextStatus.DONE)  # fmt: skip
    add_material(artist, MaterialKind.PHOTO, status=ScanStatus.PENDING)
    add_material(artist, MaterialKind.LINK, status=ScanStatus.PENDING, title="SEKRET-LINK",
                 provider="youtube", video_id="aaaaaaaaaaa")  # fmt: skip
    data = inputs.build_input(artist)
    assert "SEKRET" not in as_text(data)
    assert data["photos"] == [] and data["videos"] == [] and data["documents"] == []


def test_a_pdf_without_readable_text_is_left_out():
    artist = make_seed_artist()
    add_material(artist, MaterialKind.PDF, text="", text_status=TextStatus.ENCRYPTED)
    add_material(artist, MaterialKind.PDF, text="ZALEGLY", text_status=TextStatus.PENDING)
    assert inputs.build_input(artist)["documents"] == []


def test_a_deleted_material_is_gone():
    artist = make_seed_artist()
    pdf = add_material(artist, MaterialKind.PDF, text="USUNIETY-TEKST", text_status=TextStatus.DONE)
    assert "USUNIETY-TEKST" in as_text(inputs.build_input(artist))
    pdf.delete()
    assert "USUNIETY-TEKST" not in as_text(inputs.build_input(artist))


def test_without_the_rights_statement_no_material_is_used():
    artist = make_seed_artist(consent=False)
    add_material(artist, MaterialKind.PDF, text="BEZ-ZGODY", text_status=TextStatus.DONE)
    add_material(artist, MaterialKind.PHOTO)
    WebsiteImport.objects.create(
        artist=artist, url="https://example.invalid", rights_confirmed_at=artist.created_at,
        text="TEKST-STRONY-BEZ-ZGODY", status="done",
    )  # fmt: skip
    data = inputs.build_input(artist)
    assert "BEZ-ZGODY" not in as_text(data)
    assert data["photos"] == [] and data["site_text"] == ""
    assert data["questionnaire"]["q_duration_minutes"] == 45  # their own typed answers stay


def test_a_withdrawn_statement_stops_materials():
    artist = make_seed_artist()
    add_material(artist, MaterialKind.PDF, text="TRESC", text_status=TextStatus.DONE)
    assert inputs.materials_allowed(artist)
    trust.withdraw_statement(artist, LegalDocument.Kind.MATERIAL_RIGHTS)
    assert not inputs.materials_allowed(artist)
    assert "TRESC" not in as_text(inputs.build_input(artist))


def test_site_text_is_the_newest_import_and_scrubbed():
    artist = make_seed_artist()
    WebsiteImport.objects.create(
        artist=artist, url="https://example.invalid", rights_confirmed_at=artist.created_at,
        text=f"Stary. Pisz: {SITE_EMAIL}", status="done",
    )  # fmt: skip
    newest = WebsiteImport.objects.create(
        artist=artist, url="https://example.invalid", rights_confirmed_at=artist.created_at,
        text=f"Nowy tekst. Pisz: {SITE_EMAIL} lub +48 600 700 800", status="done",
    )  # fmt: skip
    text = inputs.build_input(artist)["site_text"]
    assert text.startswith("Nowy tekst.") and newest.pk
    assert SITE_EMAIL not in text and "600 700 800" not in text


def test_text_fields_are_scrubbed():
    artist = make_seed_artist()
    data = inputs.build_input(artist)
    assert SITE_EMAIL not in as_text(data)
    assert "[email]" in data["questionnaire"]["q_tech_room"]


def test_other_artists_materials_are_not_included():
    artist = make_seed_artist()
    other = make_seed_artist("inny.artysta@example.invalid")
    add_material(other, MaterialKind.PDF, text="CUDZY-TEKST", text_status=TextStatus.DONE)
    assert "CUDZY-TEKST" not in as_text(inputs.build_input(artist))
