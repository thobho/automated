"""Publication and withdrawal of the public page (US-2.8)."""

import re

import pytest
from django.test import Client
from django.urls import reverse

from apps.accounts.tests.conftest import make_artist, make_institution_member
from apps.analytics.models import Event
from apps.artists.models import Artist, ArtistAudience, ArtistVoivodeship, Offer, PublicationStatus
from apps.profiles import generation, pages, publication
from apps.profiles.models import PublishedPage
from apps.quality import services as quality
from apps.quality.models import Generation
from apps.trust import services as trust
from apps.trust.models import LegalDocument

from .factories import make_seed_artist, valid_profile

pytestmark = pytest.mark.django_db


def make_ready(email="gotowy@example.invalid", name=None) -> Artist:
    """An artist that meets the whole D6 minimum, with a current page version."""
    artist = make_seed_artist(email)
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


def test_missing_region_and_statement_block():
    artist = make_ready()
    ArtistVoivodeship.objects.filter(artist=artist).delete()
    assert keys(artist) == ["region"]


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
    assert anonymous.status_code in (302, 403, 404)
    member = make_institution_member("szkola@example.invalid")
    other = client_for_user(member).post(reverse(name))
    assert other.status_code in (302, 403, 404)
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
