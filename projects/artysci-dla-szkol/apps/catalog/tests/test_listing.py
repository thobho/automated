"""The public catalog (US-4.1): read model rows from the snapshot, and the list of cards."""

import re
from datetime import timedelta
from io import StringIO

import pytest
from django.core.management import call_command
from django.test import Client
from django.urls import reverse
from django.utils import timezone

from apps.accounts.tests.conftest import make_artist
from apps.artists.models import (
    Artist,
    ArtistAudience,
    MaterialKind,
    Offer,
    PublicationStatus,
)
from apps.catalog import listing, services
from apps.catalog.models import CatalogEntry, EntryKind
from apps.profiles import publication
from apps.profiles.tests.factories import add_material
from apps.profiles.tests.test_publication import make_ready
from apps.trust import services as trust
from apps.trust.models import LegalDocument

pytestmark = pytest.mark.django_db

URL = "/artysci/"


def fake_published(number: int) -> Artist:
    """A visible artist with a catalog row, made directly (for the pagination tests)."""
    artist = Artist.objects.get(user=make_artist(f"katalog{number}@example.invalid"))
    artist.name = f"Artysta {number:02d}"
    artist.slug = f"artysta-{number:02d}"
    artist.publication_status = PublicationStatus.PUBLISHED
    artist.save()
    CatalogEntry.objects.create(
        artist=artist,
        slug=artist.slug,
        name=artist.name,
        published_at=timezone.now() - timedelta(minutes=100 - number),
    )
    return artist


def published(email, name=None) -> Artist:
    return publication.publish(make_ready(email, name))  # the returned row has the slug


def entry_of(artist) -> CatalogEntry:
    return CatalogEntry.objects.get(artist=artist)


# --- rows -------------------------------------------------------------------------------------


def test_publish_writes_a_row_from_the_snapshot():
    artist = make_ready("a@example.invalid")
    ArtistAudience.objects.create(artist=artist, audience="grades_0_3")
    topic = services.add_entry(EntryKind.TOPIC, "Testowa tematyka")
    services.set_artist_entries(artist, EntryKind.TOPIC, [topic])
    artist = publication.publish(artist)
    row = entry_of(artist)
    assert row.slug == artist.slug == "teatr-kwiatki"
    assert row.name == "Teatr Kwiatki"
    assert row.artist_type == "theatre"
    assert row.voivodeships == ["dolnoslaskie"]
    assert row.age_groups == ["grades_0_3", "kindergarten"]
    assert row.topics == [{"slug": "testowa-tematyka", "name": "Testowa tematyka"}]
    assert row.forms == []
    assert row.price_from == 1200
    assert row.offers == [{"price": 1200, "duration": None}]
    assert row.main_photo_id is None


def test_lowest_price_ignores_on_request_offers():
    artist = make_ready("b@example.invalid")
    Offer.objects.create(artist=artist, title="B", description="x", price_pln=800, position=1)
    Offer.objects.create(artist=artist, title="C", description="x", price_on_request=True)
    publication.publish(artist)
    row = entry_of(artist)
    assert row.price_from == 800
    assert len(row.offers) == 3


def test_only_on_request_offers_give_no_price():
    artist = make_ready("c@example.invalid")
    Offer.objects.all().delete()
    Offer.objects.create(artist=artist, title="C", description="x", price_on_request=True)
    publication.publish(artist)
    assert entry_of(artist).price_from is None


def test_main_photo_is_the_first_published_photo():
    artist = make_ready("d@example.invalid")
    add_material(artist, MaterialKind.LINK, canonical_url="https://youtu.be/x")
    photo = add_material(artist, MaterialKind.PHOTO, storage_key="p/1.jpg", alt_text="Scena")
    publication.publish(artist)
    row = entry_of(artist)
    assert (row.main_photo_id, row.main_photo_alt) == (photo.pk, "Scena")


def test_unpublished_changes_stay_private_until_publish_changes():
    artist = published("e@example.invalid")
    artist.name = "Nowa Nazwa"
    artist.artist_type = "music"
    artist.save()
    ArtistAudience.objects.create(artist=artist, audience="secondary")
    assert entry_of(artist).name == "Teatr Kwiatki"
    assert entry_of(artist).artist_type == "theatre"
    assert entry_of(artist).age_groups == ["kindergarten"]
    publication.update_published(artist)
    row = entry_of(artist)
    assert (row.name, row.artist_type) == ("Nowa Nazwa", "music")
    assert row.age_groups == ["kindergarten", "secondary"]
    assert row.slug == "teatr-kwiatki"  # the address does not change


def test_withdrawal_removes_the_row_at_once():
    artist = published("f@example.invalid")
    publication.withdraw(artist)
    assert not CatalogEntry.objects.filter(artist=artist).exists()


def test_republication_gives_the_row_again():
    artist = published("g@example.invalid")
    publication.withdraw(artist)
    publication.publish(artist)
    assert entry_of(artist).slug == "teatr-kwiatki"


def test_sync_removes_the_row_of_a_deactivated_account():
    artist = published("h@example.invalid")
    artist.user.is_active = False
    artist.user.save()
    assert listing.sync(artist) is False
    assert not CatalogEntry.objects.exists()


def test_an_older_snapshot_gives_a_row_without_the_new_lists():
    artist = published("i@example.invalid")
    page = artist.published_page
    for key in ("age_groups", "topics", "forms"):
        page.data.pop(key)
    for offer in page.data["offers"]:
        offer.pop("price_pln"), offer.pop("duration_minutes")
    page.save()
    listing.sync(artist)
    row = entry_of(artist)
    assert (row.age_groups, row.topics, row.forms) == ([], [], [])
    assert row.price_from is None


def test_rebuild_is_idempotent_and_drops_stale_rows():
    kept = published("j@example.invalid")
    gone = published("k@example.invalid", "Inny Artysta")
    CatalogEntry.objects.filter(artist=kept).update(name="Zepsuta")
    Artist.objects.filter(pk=gone.pk).update(publication_status=PublicationStatus.WITHDRAWN)

    def snapshot():
        return list(CatalogEntry.objects.order_by("pk").values())

    out = StringIO()
    call_command("rebuild_catalog", stdout=out)
    first = snapshot()
    call_command("rebuild_catalog", stdout=out)
    assert snapshot() == first
    assert [row["name"] for row in first] == ["Teatr Kwiatki"]
    assert "1 rows" in out.getvalue()


# --- the page ---------------------------------------------------------------------------------


def cards(html: str) -> int:
    return html.count("data-catalog-card")


def test_empty_catalog_shows_a_message():
    response = Client().get(URL)
    assert response.status_code == 200
    assert "Nie ma jeszcze żadnych opublikowanych artystów" in response.content.decode()


def test_pagination_24_per_page_and_hidden_states():
    for number in range(1, 26):
        fake_published(number)
    draft = Artist.objects.get(user=make_artist("szkic@example.invalid"))
    draft.name = "Szkic"
    draft.save()
    withdrawn = fake_published(26)
    Artist.objects.filter(pk=withdrawn.pk).update(publication_status=PublicationStatus.WITHDRAWN)
    client = Client()
    first = client.get(URL)
    assert first.status_code == 200
    assert first["Cache-Control"] == "no-cache"
    html = first.content.decode()
    assert cards(html) == 24
    assert "Szkic" not in html and "Artysta 26" not in html
    assert 'href="/artysci/?strona=2"' in html and "Następna" in html
    second = client.get(URL, {"strona": 2}).content.decode()
    assert cards(second) == 1
    assert "Artysta 01" in second  # the oldest publication is last
    assert 'href="/artysci/"' in second and "Poprzednia" in second


def test_order_is_latest_first_then_id():
    first, second = fake_published(1), fake_published(2)
    same = timezone.now()
    CatalogEntry.objects.update(published_at=same)
    html = Client().get(URL).content.decode()
    assert html.index(second.name) < html.index(first.name)


@pytest.mark.parametrize("value", ["3", "0", "-1", "abc", "", "1.5", "²", "9" * 40])
def test_invalid_or_out_of_range_page_is_404(value):
    for number in range(1, 26):
        fake_published(number)
    response = Client().get(URL, {"strona": value})
    assert response.status_code == 404
    assert "Brak dostępu" not in response.content.decode()


def test_post_is_refused():
    assert Client().post(URL).status_code == 405


def test_card_shows_the_lowest_price_and_labels():
    artist = published("l@example.invalid")
    Offer.objects.create(artist=artist, title="B", description="x", price_pln=800, position=1)
    Offer.objects.create(artist=artist, title="C", description="x", price_on_request=True)
    publication.update_published(artist)
    html = Client().get(URL).content.decode()
    assert "od 800 zł" in html
    assert "teatr" in html and "dolnośląskie" in html and "przedszkola" in html
    assert 'href="/artysci/teatr-kwiatki/"' in html


def test_card_without_price_shows_none():
    artist = make_ready("m@example.invalid")
    Offer.objects.all().delete()
    Offer.objects.create(artist=artist, title="C", description="x", price_on_request=True)
    publication.publish(artist)
    assert "zł" not in Client().get(URL).content.decode()


def test_card_without_a_photo_shows_the_initial_and_no_img():
    published("n@example.invalid")
    html = Client().get(URL).content.decode()
    assert "<img" not in html
    assert re.search(r'catalog-card__initial"[^>]*>T<', html)


def test_card_with_a_photo_has_alt_size_and_lazy_loading():
    artist = make_ready("o@example.invalid")
    add_material(
        artist, MaterialKind.PHOTO, storage_key="p/2.jpg", alt_text="Scena z lalkami",
        width=960, height=720,
    )  # fmt: skip
    publication.publish(artist)
    html = Client().get(URL).content.decode()
    tag = re.search(r"<img[^>]*>", html).group(0)
    assert 'alt="Scena z lalkami"' in tag
    assert 'width="480"' in tag and 'height="360"' in tag
    assert 'loading="lazy"' in tag


def test_photo_is_hidden_when_the_rights_statement_is_gone():
    artist = make_ready("p@example.invalid")
    add_material(artist, MaterialKind.PHOTO, storage_key="p/3.jpg", alt_text="Scena")
    publication.publish(artist)
    assert "<img" in Client().get(URL).content.decode()
    trust.withdraw_statement(artist, LegalDocument.Kind.MATERIAL_RIGHTS)
    assert "<img" not in Client().get(URL).content.decode()


def test_deactivated_account_disappears_at_once():
    artist = published("q@example.invalid")
    artist.user.is_active = False
    artist.user.save()
    assert cards(Client().get(URL).content.decode()) == 0


def test_badge_follows_the_verification_function(monkeypatch):
    first = published("r@example.invalid")
    published("s@example.invalid", "Drugi Artysta")
    html = Client().get(URL).content.decode()
    assert "zweryfikowany" not in html
    monkeypatch.setattr(listing, "is_verified", lambda artist_id: artist_id == first.pk)
    html = Client().get(URL).content.decode()
    assert html.count("zweryfikowany") == 1
    card = html.split("data-catalog-card")[1:]
    assert sum("zweryfikowany" in c for c in card) == 1
    assert "zweryfikowany" in next(c for c in card if "Teatr Kwiatki" in c and "Drugi" not in c)


def test_no_contact_data_and_no_inline_code():
    published("t@example.invalid")
    response = Client().get(URL)
    html = response.content.decode()
    assert "mailto:" not in html and "tel:" not in html and "@" not in html
    assert "<script>" not in html and " style=" not in html and "<style" not in html
    assert "example.invalid" not in html


def test_header_links_to_the_catalog():
    html = Client().get(reverse("accounts:login")).content.decode()
    assert 'href="/artysci/"' in html
