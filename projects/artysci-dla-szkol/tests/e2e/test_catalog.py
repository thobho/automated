"""The public catalog (US-4.1) in a real browser on a 360 px phone: open it, go to page 2, open a
profile. Synthetic data in the live database the server uses (a fresh tag per test)."""

import uuid

import pytest
from axe_playwright_python.sync_playwright import Axe


def _seed():
    from datetime import timedelta

    from django.utils import timezone

    from apps.accounts.tests.conftest import make_artist
    from apps.artists.models import Artist, ArtistAudience, ArtistVoivodeship, PublicationStatus
    from apps.catalog.models import CatalogEntry
    from apps.profiles import generation, pages, publication
    from apps.profiles.tests.factories import make_seed_artist, valid_profile
    from apps.quality import services as quality
    from apps.quality.models import Generation
    from apps.trust import services as trust
    from apps.trust.models import LegalDocument

    tag = uuid.uuid4().hex[:8]
    for number in range(25):  # enough rows for a second page, whatever else is in the database
        artist = Artist.objects.get(user=make_artist(f"e2e-cat-{tag}-{number}@example.invalid"))
        artist.name = f"Artysta {tag} {number:02d}"
        artist.slug = f"artysta-{tag}-{number:02d}"
        artist.publication_status = PublicationStatus.PUBLISHED
        artist.save()
        CatalogEntry.objects.create(
            artist=artist,
            slug=artist.slug,
            name=artist.name,
            artist_type="music",
            voivodeships=["dolnoslaskie"],
            age_groups=["kindergarten"],
            price_from=500,
            published_at=timezone.now() - timedelta(days=1, minutes=number),
        )
    real = make_seed_artist(f"e2e-cat-{tag}@example.invalid")
    real.name = f"Teatr Katalogowy {tag}"
    real.save()
    ArtistVoivodeship.objects.create(artist=real, voivodeship="dolnoslaskie")
    ArtistAudience.objects.create(artist=real, audience="kindergarten")
    if trust.current(LegalDocument.Kind.CHILD_PROTECTION) is None:
        trust.publish(LegalDocument.Kind.CHILD_PROTECTION, "Treść testowa", material=False)
    trust.make_statement(real, LegalDocument.Kind.CHILD_PROTECTION)
    record = quality.start_generation(real, Generation.Trigger.MANUAL, generation.COMPONENTS)
    pages.record_generated(
        quality.finish_generation(
            record,
            valid_profile(description={"paragraphs": ["Opis z katalogu."]}),
            [],
            0,
            Generation.Status.READY,
        )
    )
    publication.publish(real)
    return tag


@pytest.fixture
def tag(django_db_blocker):
    with django_db_blocker.unblock():
        yield _seed()


def test_browse_catalog_on_a_phone(browser, base_url, tag, shot_dir):
    context = browser.new_context(viewport={"width": 360, "height": 740})
    page = context.new_page()
    assert page.goto(base_url + "/artysci/").status == 200
    assert page.get_by_role("heading", level=1, name="Artyści").is_visible()
    assert page.locator("[data-catalog-card]").count() == 24
    assert page.locator("[style]").count() == 0
    # no sideways scrolling on a phone
    assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
    violations = Axe().run(page).response["violations"]
    assert not [v for v in violations if v["impact"] in ("critical", "serious")]
    page.screenshot(path=str(shot_dir / "catalog-page1.png"), full_page=True)

    page.get_by_role("link", name="Następna").click()
    page.wait_for_load_state()
    assert page.url.endswith("/artysci/?strona=2")
    assert page.locator("[data-catalog-card]").count() >= 1
    page.screenshot(path=str(shot_dir / "catalog-page2.png"), full_page=True)
    assert page.goto(base_url + "/artysci/?strona=999999").status == 404

    # The newest publication is the first card on page 1; its name opens the profile.
    page.goto(base_url + "/artysci/")
    name = f"Teatr Katalogowy {tag}"
    page.get_by_role("link", name=name).click()
    page.wait_for_load_state()
    assert "/artysci/teatr-katalogowy-" in page.url
    assert page.get_by_text("Opis z katalogu.").is_visible()
