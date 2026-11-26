"""Closed dictionaries (US-4.6) in a real browser: the artist ticks topics and forms on step 1,
the admin merges two topics in /django-admin/. Synthetic data in the live database."""

import uuid

import pytest
from axe_playwright_python.sync_playwright import Axe

BASICS = "/artysta/profil/dane/"
LIST = "/django-admin/catalog/dictionaryentry/"


def _login(browser, base_url, user_pk):
    from django.conf import settings
    from django.contrib.auth import get_user_model
    from django.test import Client

    client = Client()
    client.force_login(get_user_model().objects.get(pk=user_pk))
    context = browser.new_context()
    host = base_url.split("://", 1)[1].split("/")[0].split(":")[0]
    cookie = client.cookies[settings.SESSION_COOKIE_NAME].value
    context.add_cookies(
        [{"name": settings.SESSION_COOKIE_NAME, "value": cookie, "domain": host, "path": "/"}]
    )
    return context.new_page()


@pytest.fixture
def users(django_db_blocker):
    from apps.accounts import services as accounts
    from apps.accounts.tests.conftest import make_artist
    from apps.trust import services as trust

    tag = uuid.uuid4().hex[:8]
    with django_db_blocker.unblock():
        artist = make_artist(f"e2e-dict-{tag}@example.invalid")
        admin = accounts.create_admin(f"e2e-dict-admin-{tag}@example.invalid")[0]
        for user in (artist, admin):  # a database with published documents asks for acceptance
            for document in trust.pending_acceptances(user):
                trust.record_acceptance(user, [document.kind])
        yield artist.pk, admin.pk


def test_artist_picks_entries_and_admin_merges(
    browser, base_url, users, shot_dir, django_db_blocker
):
    from apps.artists.models import Artist
    from apps.catalog import services
    from apps.catalog.models import ArtistEntry

    artist_pk, admin_pk = users
    page = _login(browser, base_url, artist_pk)
    assert page.goto(base_url + BASICS).status == 200
    group = page.get_by_role("group")
    group.filter(has_text="Rodzaj").get_by_label("teatr", exact=True).check()
    page.get_by_label("Nazwa (imię i nazwisko, zespół lub firma)").fill("Teatr E2E")
    page.get_by_label("Miasto").fill("Wrocław")
    group.filter(has_text="Województwa").get_by_label("dolnośląskie").check()
    group.filter(has_text="Odbiorcy").get_by_label("przedszkola").check()
    group.filter(has_text="Tematyka").get_by_label("hejt").check()
    group.filter(has_text="Forma").get_by_label("warsztaty").check()
    page.screenshot(path=str(shot_dir / "catalog-step1.png"), full_page=True)
    assert not Axe().run(page).violations_count
    page.get_by_role("button", name="Zapisz").click()
    page.wait_for_url("**/artysta/kreator/")
    with django_db_blocker.unblock():
        mine = ArtistEntry.objects.filter(artist=Artist.objects.get(user_id=artist_pk))
        assert set(mine.values_list("entry__slug", flat=True)) == {"hejt", "warsztaty"}
        source = services.add_entry("topic", f"E2E źródło {uuid.uuid4().hex[:6]}")
        # the artist's only topic becomes the source, so the merge below moves exactly one profile
        services.set_artist_entries(mine[0].artist, "topic", [source])

    admin = _login(browser, base_url, admin_pk)
    assert admin.goto(base_url + LIST).status == 200
    admin.locator(f"input[name=_selected_action][value='{source.pk}']").check()
    admin.locator("select[name=action]").select_option("merge")
    admin.get_by_role("button", name="Wykonaj").click()
    assert admin.locator("#merge-count").inner_text() == "1"
    admin.get_by_label("Połącz z").select_option(label="hejt")
    admin.screenshot(path=str(shot_dir / "catalog-merge-confirm.png"), full_page=True)
    admin.get_by_role("button", name="Połącz").click()
    admin.wait_for_url("**/dictionaryentry/")
    with django_db_blocker.unblock():
        assert not type(source).objects.filter(pk=source.pk).exists()
        assert mine.filter(entry__slug="hejt").count() == 1
