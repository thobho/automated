"""Publication and withdrawal of the public page (US-2.8)."""

import re

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from apps.accounts.tests.conftest import make_artist, make_institution_member
from apps.analytics.models import Event
from apps.artists.models import (
    Artist,
    ArtistAudience,
    ArtistVoivodeship,
    Material,
    MaterialKind,
    Offer,
    PublicationStatus,
    ScanStatus,
)
from apps.profiles import generation, pages, publication
from apps.profiles.contact import contacts_in
from apps.profiles.models import PublishedPage
from apps.quality import services as quality
from apps.quality.models import Generation
from apps.trust import services as trust
from apps.trust.models import LegalDocument

from .factories import add_material, allow_materials, make_seed_artist, valid_profile

pytestmark = pytest.mark.django_db


def make_ready(email="gotowy@example.invalid", name=None, *, consent=True) -> Artist:
    """An artist that meets the whole D6 minimum, with a current page version."""
    artist = make_seed_artist(email, consent=consent)
    if name:
        artist.name = name
        artist.save()
    ArtistVoivodeship.objects.create(artist=artist, voivodeship="dolnoslaskie")
    ArtistAudience.objects.create(artist=artist, audience="kindergarten")
    if trust.current(LegalDocument.Kind.CHILD_PROTECTION) is None:
        trust.publish(LegalDocument.Kind.CHILD_PROTECTION, "Treść testowa", material=False)
    trust.make_statement(artist, LegalDocument.Kind.CHILD_PROTECTION)
    record = quality.start_generation(artist, "manual", generation.COMPONENTS)
    pages.record_generated(
        quality.finish_generation(
            record,
            valid_profile(description={"paragraphs": ["Stary opis testowy."]}),
            [],
            0,
            Generation.Status.READY,
        )
    )
    return artist


def keys(artist):
    return [b.key for b in publication.publication_blockers(artist)]


def client_for(artist, **kwargs) -> Client:
    client = Client(**kwargs)
    client.force_login(artist.user)
    return client


# --- blockers ------------------------------------------------------------------------------------


def test_ready_artist_has_no_blockers():
    assert keys(make_ready()) == []


def test_empty_artist_lists_every_reason_in_polish():
    artist = Artist.objects.get(user=make_artist("pusty@example.invalid"))
    artist.name = ""
    artist.save()
    assert set(keys(artist)) == {"name", "region", "generation", "offer", "child_protection"}
    assert all(str(b.text) for b in publication.publication_blockers(artist))


def test_blocker_urls_resolve():
    artist = Artist.objects.get(user=make_artist("pusty@example.invalid"))
    artist.name = ""
    for blocker in publication.publication_blockers(artist):
        assert reverse(blocker.url_name)


def test_missing_offer_refuses_and_stays_draft():
    artist = make_ready()
    Offer.objects.filter(artist=artist).delete()
    with pytest.raises(publication.PublicationRefused) as refused:
        publication.publish(artist)
    assert [b.key for b in refused.value.blockers] == ["offer"]
    assert "ofert" in str(refused.value.blockers[0].text)
    artist.refresh_from_db()
    assert artist.publication_status == PublicationStatus.DRAFT
    assert artist.published_at is None and artist.slug is None


def test_empty_about_in_current_version_blocks():
    artist = make_ready()
    pages.edit_field(artist, "about", "x")
    version = pages.current_version(artist)
    version.content["about"] = "  "
    version.save()
    assert keys(artist) == ["about"]


def test_missing_region_blocks():
    artist = make_ready()
    ArtistVoivodeship.objects.filter(artist=artist).delete()
    assert keys(artist) == ["region"]


def test_missing_child_protection_statement_blocks():
    artist = make_ready()
    trust.withdraw_statement(artist, LegalDocument.Kind.CHILD_PROTECTION)
    assert keys(artist) == ["child_protection"]
    with pytest.raises(publication.PublicationRefused):
        publication.publish(artist)


# --- contact data (D9) ---------------------------------------------------------------------------


@pytest.mark.parametrize("value", ["pisz: probe@example.invalid", "tel. 600 700 800"])
@pytest.mark.parametrize("path", ["tagline", "about", "for_schools", "faq.0.answer"])
def test_contact_data_in_a_text_blocks_publish_and_update(path, value):
    artist = make_ready()
    publication.publish(artist)
    pages.edit_field(artist, path, value)
    (blocker,) = publication.publication_blockers(artist)
    assert blocker.key == "contact_texts" and blocker.url_name == "profiles:preview"
    assert value.split(" ", 1)[1] in str(blocker.text)
    with pytest.raises(publication.PublicationRefused):
        publication.update_published(artist)
    publication.withdraw(artist)
    with pytest.raises(publication.PublicationRefused):
        publication.publish(artist)
    assert Artist.objects.get(pk=artist.pk).publication_status == PublicationStatus.WITHDRAWN


@pytest.mark.parametrize("field", ["title", "description"])
@pytest.mark.parametrize("value", ["Pisz probe@example.invalid", "Dzwoń +48 600-700-800"])
def test_contact_data_in_an_offer_blocks(field, value):
    artist = make_ready()
    Offer.objects.filter(artist=artist).update(**{field: value})
    (blocker,) = publication.publication_blockers(artist)
    assert blocker.key == "contact_offers" and blocker.url_name == "artists:offers"
    with pytest.raises(publication.PublicationRefused):
        publication.publish(artist)


def test_contact_data_in_the_name_or_city_blocks():
    artist = make_ready(name="Teatr 600 700 800")
    assert keys(artist) == ["contact_name"]
    artist.name, artist.city = "Teatr", "Opole, biuro@example.invalid"
    artist.save()
    assert keys(artist) == ["contact_city"]


@pytest.mark.parametrize(
    "text",
    [
        "Cena 1200 zł, czas 45 min",
        "Cena: 10 000 - 12 000 zł",
        "od 800 do 1 200 zł",
        "wiek 4–9 lat, do 120 widzów",
        "13-15.11.2026, godz. 10:00–11:30",
        "W latach 2019-2026 zagraliśmy 350 razy",
    ],
)
def test_prices_durations_and_dates_are_not_contact_data(text):
    assert contacts_in(text) == []
    artist = make_ready()
    Offer.objects.filter(artist=artist).update(description=text)
    pages.edit_field(artist, "about", text)
    assert keys(artist) == []


@pytest.mark.parametrize(
    ("text", "found"),
    [
        ("600–700–800", ["600-700-800"]),
        ("Dzwoń 600\xa0700\xa0800: zawsze", ["600 700 800"]),
        ("Cena 900 zł, tel.600700800", ["600700800"]),
        ("13.11.2026 600 700 800", ["600 700 800"]),
        ("a@b.pl i c@d.pl", ["a@b.pl", "c@d.pl"]),
        ("", []),
    ],
)
def test_contacts_in(text, found):
    assert contacts_in(text) == found


TWO_PHONES = [
    f"600 700 800{separator}601 700 800" for separator in ("\n", "\r\n", " ", " - ", " – ", ". ")
]


@pytest.mark.parametrize("text", TWO_PHONES)
def test_two_phones_in_a_row_are_both_found(text):
    assert contacts_in(text) == ["600 700 800", "601 700 800"]


@pytest.mark.parametrize(
    ("text", "found"),
    [
        ("600700800 601700800 602700800", ["600700800", "601700800", "602700800"]),
        ("+48 600 700 800 - 0048 601 700 800", ["+48 600 700 800", "0048 601 700 800"]),
        ("48 600 700 800 48 601 700 800", ["48 600 700 800", "48 601 700 800"]),
        ("22 123 45 67\n22 123 45 68", ["22 123 45 67", "22 123 45 68"]),
        ("600\n700 800", ["600 700 800"]),
        ("600\n700 800\n601 700 800", ["600 700 800", "601 700 800"]),
        ("tel600700800, 601 700 800zł", ["600700800", "601 700 800"]),
        ("+49 170 123 456", ["+49 170 123 456"]),
        ("konto 61 1090 1014 0000 0712 1981 2874", []),
        ("2026-11-13 2026-11-14", []),
        ("Ceny:\n1200 zł\n1500 zł\n10 000 zł", []),
    ],
)
def test_phones_next_to_each_other_and_numbers_that_are_not_phones(text, found):
    assert sorted(contacts_in(text)) == sorted(found)


@pytest.mark.parametrize("text", TWO_PHONES)
def test_two_phones_in_a_row_block_publish_and_update(text):
    artist = make_ready()
    publication.publish(artist)
    pages.edit_field(artist, "about", f"Telefon:\n{text}")
    (blocker,) = publication.publication_blockers(artist)
    assert blocker.key == "contact_texts"
    assert "600 700 800" in str(blocker.text) and "601 700 800" in str(blocker.text)
    with pytest.raises(publication.PublicationRefused):
        publication.update_published(artist)
    html = Client().get(public_url(Artist.objects.get(pk=artist.pk).slug)).content.decode()
    assert "600 700 800" not in html and "601 700 800" not in html
    publication.withdraw(artist)
    with pytest.raises(publication.PublicationRefused):
        publication.publish(artist)


def test_contact_data_in_a_photo_alt_text_blocks():
    artist = make_ready()
    photo = add_photos(artist)[0]
    publication.publish(artist)
    Material.objects.filter(pk=photo.pk).update(alt_text="Plakat, tel. 600 700 800")
    (blocker,) = publication.publication_blockers(artist)
    assert blocker.key == "contact_photos" and reverse(blocker.url_name)
    with pytest.raises(publication.PublicationRefused):
        publication.update_published(artist)
    assert "600 700 800" not in repr(live(artist).photos)


def test_a_price_after_a_phone_does_not_hide_it():
    assert "600 700 800" in contacts_in("tel. 600 700 800 - 900 zł")[0]


def test_the_artists_own_address_is_found_in_any_spelling():
    assert contacts_in("pisz na Biuro@Łąka.Example", "biuro@łąka.example")


# --- slug ----------------------------------------------------------------------------------------


@pytest.mark.parametrize(
    ("name", "slug"),
    [
        ("Teatr Kwiatki", "teatr-kwiatki"),
        ("Zażółć Gęślą Jaźń!", "zazolc-gesla-jazn"),
        ("  Łódź  &  Co. ", "lodz-co"),
        ("!!!", "artysta"),
    ],
)
def test_slugify_name(name, slug):
    assert publication.slugify_name(name) == slug


def test_collision_gets_a_numeric_suffix():
    first, second = make_ready("a@example.invalid"), make_ready("b@example.invalid")
    publication.publish(first)
    publication.publish(second)
    first.refresh_from_db()
    second.refresh_from_db()
    assert first.slug == "teatr-kwiatki" and second.slug == "teatr-kwiatki-2"


@pytest.mark.parametrize("name", ["Admin", "API", "Panel", "Static"])
def test_reserved_words_are_not_slugs(name):
    artist = make_ready(name=name)
    publication.publish(artist)
    artist.refresh_from_db()
    assert artist.slug == f"{name.lower()}-2"
    assert artist.slug not in publication.RESERVED_SLUGS


def test_slug_survives_rename_and_withdrawal():
    artist = make_ready()
    publication.publish(artist)
    slug = Artist.objects.get(pk=artist.pk).slug
    artist.refresh_from_db()
    artist.name = "Całkiem inna nazwa"
    artist.save()
    publication.withdraw(artist)
    publication.publish(artist)
    assert Artist.objects.get(pk=artist.pk).slug == slug
    other = make_ready("c@example.invalid")
    publication.publish(other)  # same name as the original: the withdrawn slug is not reused
    assert Artist.objects.get(pk=other.pk).slug != slug


# --- state, snapshot, published() ----------------------------------------------------------------


def test_publish_sets_state_snapshot_and_event():
    artist = make_ready()
    publication.publish(artist, actor=artist.user)
    artist.refresh_from_db()
    assert artist.publication_status == PublicationStatus.PUBLISHED
    assert artist.published_at is not None and artist.withdrawn_at is None
    assert PublishedPage.objects.get(artist=artist).content["about"] == "Stary opis testowy."
    event = Event.objects.get(name="profile_published")
    assert event.properties["profile_id"] == artist.pk
    assert 0 <= event.properties["completeness_percent"] <= 100
    assert "Kwiatki" not in repr(event.__dict__)


def test_publishing_twice_is_refused():
    artist = make_ready()
    publication.publish(artist)
    with pytest.raises(publication.PublicationRefused):
        publication.publish(artist)
    assert Event.objects.filter(name="profile_published").count() == 1


def test_edits_stay_private_until_update():
    artist = make_ready()
    publication.publish(artist)
    assert not publication.has_unpublished_changes(artist)
    pages.edit_field(artist, "about", "Nowy opis.")
    assert publication.has_unpublished_changes(artist)
    assert publication.public_page(Artist.objects.get(pk=artist.pk).slug).about == (
        "Stary opis testowy."
    )
    publication.update_published(artist)
    assert publication.public_page(Artist.objects.get(pk=artist.pk).slug).about == "Nowy opis."
    assert not publication.has_unpublished_changes(artist)


def add_photos(artist, count=4):
    return [
        add_material(artist, MaterialKind.PHOTO, storage_key=f"private/pub-{artist.pk}-{i}.jpg")
        for i in range(count)
    ]


def add_video(artist, **fields):
    return add_material(
        artist,
        MaterialKind.VIDEO,
        converted_key="private/v.mp4",
        thumbnail_key="private/v.jpg",
        original_name="Jan_Kowalski_prywatne.mov",
        **fields,
    )


def add_link(artist, title="Film"):
    return add_material(
        artist,
        MaterialKind.LINK,
        provider="youtube",
        video_id="abcdefghijk",
        canonical_url="https://www.youtube.com/watch?v=abcdefghijk",
        title=title,
    )


def live(artist):
    return publication.public_page(Artist.objects.get(pk=artist.pk).slug)


def _new_offer(artist):
    Offer.objects.create(artist=artist, title="Nowa", description="x", price_pln=5, position=9)


def _edit_offer(artist):
    Offer.objects.filter(artist=artist).update(title="Nowa", price_pln=7)


def _delete_offer(artist):
    Offer.objects.filter(artist=artist, title="Druga").delete()


def _rename(artist):
    Artist.objects.filter(pk=artist.pk).update(name="Nowa nazwa")


def _move(artist):
    Artist.objects.filter(pk=artist.pk).update(city="Nowe Miasto")


def _choose_theme(artist):
    Artist.objects.filter(pk=artist.pk).update(theme="coral_dark")


def _new_photo(artist):
    add_photos(artist, 1)


def _new_alt_text(artist):
    Material.objects.filter(artist=artist).update(alt_text="Dzieci na scenie")


@pytest.mark.parametrize(
    "change",
    [
        _new_alt_text,
        _new_offer,
        _edit_offer,
        _delete_offer,
        _rename,
        _move,
        _choose_theme,
        _new_photo,
        add_video,
        add_link,
    ],
)
def test_every_change_stays_private_until_update(change):
    artist = make_ready()
    Offer.objects.create(artist=artist, title="Druga", description="x", price_pln=5, position=8)
    add_photos(artist)
    publication.publish(artist)
    before = live(artist)
    assert len(before.photos) == 4 and not publication.has_unpublished_changes(artist)
    change(artist)
    artist.refresh_from_db()
    assert _shown(live(artist)) == _shown(before)
    assert publication.has_unpublished_changes(artist)
    publication.update_published(artist)
    assert _shown(live(artist)) != _shown(before)
    assert not publication.has_unpublished_changes(artist)


def _shown(page):
    """The page without the signed URLs (they change over time)."""
    return (
        page.hero.name,
        page.hero.city,
        page.offers,
        page.theme,
        [p.alt for p in page.photos],
        [v.title for v in page.videos],
        page.about,
    )


def test_deleting_every_offer_leaves_the_published_page_whole():
    artist = make_ready()
    publication.publish(artist)
    Offer.objects.filter(artist=artist).delete()
    assert [o.title for o in live(artist).offers] == ["Kwiatowa opowieść"]


def test_a_deleted_or_unready_material_disappears_at_once():
    artist = make_ready()
    photos = add_photos(artist, 5)
    publication.publish(artist)
    photos[0].delete()
    assert len(live(artist).photos) == 4
    Material.objects.filter(pk=photos[1].pk).update(status=ScanStatus.REJECTED)
    assert len(live(artist).photos) == 3
    assert not publication.has_unpublished_changes(artist)  # the public page is already there


def test_materials_need_the_rights_statement_never_made():
    artist = make_ready(consent=False)
    add_photos(artist)
    add_video(artist)
    add_link(artist)
    publication.publish(artist)
    html = Client().get(public_url(Artist.objects.get(pk=artist.pk).slug)).content.decode()
    assert 'id="photos"' not in html and 'id="videos"' not in html and "youtube" not in html
    assert "data-materials-hidden" in panel(artist)
    allow_materials(artist)  # the statement alone publishes nothing
    assert live(artist).photos == [] and live(artist).videos == []
    assert publication.has_unpublished_changes(artist)
    publication.update_published(artist)
    assert len(live(artist).photos) == 4 and len(live(artist).videos) == 2
    assert "data-materials-hidden" not in panel(artist)


def test_materials_disappear_when_the_rights_statement_is_withdrawn():
    artist = make_ready()
    add_photos(artist)
    add_link(artist)
    publication.publish(artist)
    url = public_url(Artist.objects.get(pk=artist.pk).slug)
    assert 'id="photos"' in Client().get(url).content.decode()
    trust.withdraw_statement(artist, LegalDocument.Kind.MATERIAL_RIGHTS)
    html = Client().get(url).content.decode()
    assert 'id="photos"' not in html and 'id="videos"' not in html and "youtube" not in html
    allow_materials(artist)  # what the artist had already published comes back
    assert len(live(artist).photos) == 4 and len(live(artist).videos) == 1


def panel(artist):
    return client_for(artist).get(reverse("profiles:publication")).content.decode()


def test_public_page_never_shows_file_names_or_contact_data_in_titles():
    artist = make_ready()
    add_video(artist)
    add_link(artist, title="Zadzwoń 600 700 800")
    publication.publish(artist)
    html = Client().get(public_url(Artist.objects.get(pk=artist.pk).slug)).content.decode()
    assert "Jan_Kowalski" not in html and "600 700 800" not in html
    assert "Nagranie 1" in html and "Nagranie 2" in html


def test_a_deactivated_account_has_no_public_page():
    artist = make_ready()
    publication.publish(artist)
    artist.user.is_active = False
    artist.user.save()
    assert not Artist.objects.published().exists() and live(artist) is None
    assert Client().get(public_url(Artist.objects.get(pk=artist.pk).slug)).status_code == 404


def test_update_needs_a_published_page():
    artist = make_ready()
    with pytest.raises(publication.PublicationRefused):
        publication.update_published(artist)


def test_update_refused_when_blockers_appeared():
    artist = make_ready()
    publication.publish(artist)
    Offer.objects.filter(artist=artist).delete()
    with pytest.raises(publication.PublicationRefused):
        publication.update_published(artist)


def test_withdraw_hides_page_and_records_event():
    artist = make_ready()
    publication.publish(artist)
    slug = Artist.objects.get(pk=artist.pk).slug
    publication.withdraw(artist, actor=artist.user)
    artist.refresh_from_db()
    assert artist.publication_status == PublicationStatus.WITHDRAWN
    assert artist.withdrawn_at is not None
    assert publication.public_page(slug) is None
    assert not Artist.objects.published().filter(pk=artist.pk).exists()
    assert Event.objects.filter(name="profile_withdrawn", properties={"profile_id": artist.pk})
    assert not PublishedPage.objects.filter(artist=artist).exists()


def test_withdraw_needs_a_published_page():
    with pytest.raises(publication.PublicationRefused):
        publication.withdraw(make_ready())


def test_republish_after_withdrawal_gives_the_same_slug_and_page():
    artist = make_ready()
    publication.publish(artist)
    slug = Artist.objects.get(pk=artist.pk).slug
    publication.withdraw(artist)
    publication.publish(artist)
    assert publication.public_page(slug) is not None


def test_published_manager_method_only_returns_published():
    draft, live, gone = make_ready("d@example.invalid"), make_ready("l@example.invalid"), None
    gone = make_ready("g@example.invalid")
    publication.publish(live)
    publication.publish(gone)
    publication.withdraw(gone)
    assert list(Artist.objects.published()) == [Artist.objects.get(pk=live.pk)]
    assert draft.publication_status == PublicationStatus.DRAFT


# --- public route --------------------------------------------------------------------------------


def public_url(slug):
    return reverse("profiles:public", args=[slug])


def test_public_page_shows_snapshot_without_contact_data_or_inline_code():
    artist = make_ready("kontakt-tajny@example.invalid")
    publication.publish(artist)
    slug = Artist.objects.get(pk=artist.pk).slug
    response = Client().get(public_url(slug))
    assert response.status_code == 200
    html = response.content.decode()
    assert "Stary opis testowy." in html and "Kwiatowa opowieść" in html
    for forbidden in (
        "mailto:",
        "tel:",
        "kontakt-tajny@example.invalid",
        "kontakt@example.invalid",
    ):
        assert forbidden not in html
    assert not re.search(r"<script(?![^>]*\bsrc=)", html)
    assert "<style" not in html and " style=" not in html
    assert 'name="robots"' not in html
    assert "noindex" not in response.get("X-Robots-Tag", "")
    assert "no-cache" in response["Cache-Control"]
    assert (
        "Content-Security-Policy" in response or "Content-Security-Policy-Report-Only" in response
    )


def test_public_csp_header_matches_other_pages():
    artist = make_ready()
    publication.publish(artist)
    public = Client().get(public_url(Artist.objects.get(pk=artist.pk).slug))
    other = Client().get(reverse("accounts:login"))
    csp = "Content-Security-Policy"

    def plain(response):  # the nonce differs per response
        return re.sub(r"nonce-[\w-]+", "nonce-X", response[csp])

    assert plain(public) == plain(other)


def test_draft_withdrawn_and_unknown_are_indistinguishable_404s():
    draft = make_ready("d@example.invalid")
    gone = make_ready("g@example.invalid")
    publication.publish(gone)
    slug = Artist.objects.get(pk=gone.pk).slug
    publication.withdraw(gone)
    Artist.objects.filter(pk=draft.pk).update(slug="szkic")
    responses = [Client().get(public_url(s)) for s in (slug, "szkic", "nie-ma-takiej")]
    assert [r.status_code for r in responses] == [404, 404, 404]
    assert len({r.content for r in responses}) == 1
    assert len({r.get("Cache-Control") for r in responses}) == 1


def test_public_page_accepts_only_get():
    artist = make_ready()
    publication.publish(artist)
    url = public_url(Artist.objects.get(pk=artist.pk).slug)
    assert Client().post(url).status_code == 405
    head = Client().head(url)  # link checkers and uptime monitors
    assert head.status_code == 200 and head.content == b""


# --- Django admin: only `publication` writes the publication fields ------------------------------

PUBLICATION_FIELDS = ("slug", "publication_status", "published_at", "withdrawn_at")


@pytest.fixture
def admin_client():
    root = get_user_model().objects.create_superuser(email="root@example.invalid", password="x")
    return client_for_user(root)


def admin_url(artist):
    return reverse("admin:artists_artist_change", args=[artist.pk])


def load_admin_form(client, artist) -> dict:
    """The POST data of the change form as a browser would send it now, plus the values of the
    publication fields at this moment (what an editable form would send back)."""
    context = client.get(admin_url(artist)).context
    forms = [context["adminform"].form]
    for inline in context["inline_admin_formsets"]:
        forms += [inline.formset.management_form, *inline.formset.initial_forms]
    data = {}
    for form in forms:
        for field in form:
            value = field.value()
            data[field.html_name] = "" if value is None else value
    stale = Artist.objects.get(pk=artist.pk)
    for name in PUBLICATION_FIELDS:
        value = getattr(stale, name)
        data[name] = "" if value is None else str(value)
        if name.endswith("_at"):
            data[f"{name}_0"] = value.strftime("%Y-%m-%d") if value else ""
            data[f"{name}_1"] = value.strftime("%H:%M:%S") if value else ""
    # extra inline rows are left out, so the total is what was really sent
    for inline in context["inline_admin_formsets"]:
        formset = inline.formset
        data[f"{formset.prefix}-TOTAL_FORMS"] = len(formset.initial_forms)
    return data


def publication_state(artist):
    return Artist.objects.filter(pk=artist.pk).values(*PUBLICATION_FIELDS).get()


def test_admin_form_has_no_publication_fields(admin_client):
    artist = make_ready()
    response = admin_client.get(admin_url(artist))
    assert response.status_code == 200
    assert not set(PUBLICATION_FIELDS) & set(response.context["adminform"].form.fields)


def test_a_stale_admin_form_does_not_undo_a_publication(admin_client):
    artist = make_ready()
    form = load_admin_form(admin_client, artist)
    publication.publish(artist)
    before = publication_state(artist)
    assert before["slug"] and before["publication_status"] == PublicationStatus.PUBLISHED
    response = admin_client.post(admin_url(artist), {**form, "name": "Poprawiona nazwa"})
    assert response.status_code == 302  # saved
    assert Artist.objects.get(pk=artist.pk).name == "Poprawiona nazwa"
    assert publication_state(artist) == before


def test_a_stale_admin_form_does_not_undo_a_withdrawal(admin_client):
    artist = make_ready()
    publication.publish(artist)
    form = load_admin_form(admin_client, artist)
    publication.withdraw(artist)
    before = publication_state(artist)
    assert before["publication_status"] == PublicationStatus.WITHDRAWN
    response = admin_client.post(admin_url(artist), {**form, "name": "Poprawiona nazwa"})
    assert response.status_code == 302  # saved
    assert Artist.objects.get(pk=artist.pk).name == "Poprawiona nazwa"
    assert publication_state(artist) == before
    assert not Artist.objects.published().filter(pk=artist.pk).exists()


# --- panel actions -------------------------------------------------------------------------------

ACTIONS = ["profiles:publish", "profiles:publish_changes", "profiles:withdraw"]


def test_panel_flow_publish_update_withdraw():
    artist = make_ready()
    client = client_for(artist)
    page = client.get(reverse("profiles:publication"))
    assert page.status_code == 200 and "Opublikuj" in page.content.decode()
    assert client.post(reverse("profiles:publish"), follow=True).status_code == 200
    artist.refresh_from_db()
    assert artist.publication_status == PublicationStatus.PUBLISHED
    page = client.get(reverse("profiles:publication"))
    assert public_url(artist.slug) in page.content.decode()
    assert "Opublikuj zmiany" in page.content.decode()
    confirm = client.get(reverse("profiles:withdraw_confirm"))
    assert confirm.status_code == 200 and "Tak, wycofaj" in confirm.content.decode()
    client.post(reverse("profiles:withdraw"))
    artist.refresh_from_db()
    assert artist.publication_status == PublicationStatus.WITHDRAWN
    assert Client().get(public_url(artist.slug)).status_code == 404


def test_panel_refusal_lists_blockers_with_links():
    artist = make_ready()
    Offer.objects.filter(artist=artist).delete()
    client = client_for(artist)
    client.post(reverse("profiles:publish"))
    artist.refresh_from_db()
    assert artist.publication_status == PublicationStatus.DRAFT
    html = client.get(reverse("profiles:publication")).content.decode()
    assert 'data-blocker="offer"' in html and reverse("artists:offers") in html
    assert "Opublikuj</button>" not in html


@pytest.mark.parametrize("name", ACTIONS)
def test_actions_reject_get(name):
    assert client_for(make_ready()).get(reverse(name)).status_code == 405


@pytest.mark.parametrize("name", ACTIONS)
def test_actions_need_csrf(name):
    artist = make_ready()
    client = client_for(artist, enforce_csrf_checks=True)
    assert client.post(reverse(name)).status_code == 403


@pytest.mark.parametrize("name", ACTIONS)
def test_actions_refuse_anonymous_and_other_roles(name):
    artist = make_ready()
    anonymous = Client().post(reverse(name))
    assert anonymous.status_code == 302 and reverse("accounts:login") in anonymous["Location"]
    member = make_institution_member("szkola@example.invalid")
    other = client_for_user(member).post(reverse(name))
    assert other.status_code == 403
    artist.refresh_from_db()
    assert artist.publication_status == PublicationStatus.DRAFT


def client_for_user(user) -> Client:
    client = Client()
    client.force_login(user)
    return client


def test_one_artist_cannot_publish_or_withdraw_another():
    mine, theirs = make_ready("moj@example.invalid"), make_ready("cudzy@example.invalid")
    publication.publish(theirs)
    client = client_for(mine)
    client.post(reverse("profiles:withdraw"))  # acts on `mine` only (no id in the URL)
    assert Artist.objects.get(pk=theirs.pk).publication_status == PublicationStatus.PUBLISHED
    assert Artist.objects.get(pk=mine.pk).publication_status == PublicationStatus.DRAFT


def test_publication_pages_need_login():
    for name in ("profiles:publication", "profiles:withdraw_confirm"):
        assert Client().get(reverse(name)).status_code in (302, 403, 404)
