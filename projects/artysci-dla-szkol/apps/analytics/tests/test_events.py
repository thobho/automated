import pytest

from apps.analytics import services
from apps.analytics.catalog import EVENT_CATALOG
from apps.analytics.models import Event

pytestmark = pytest.mark.django_db

# Event name -> dotted path of the code that emits it. Filled in as features land (E1+);
# an entry listed in PENDING is a known gap, anything else must have an emitter test.
EMITTERS: dict[str, str] = {
    "artist_registered": "apps.artists.services.register_artist",
    "institution_registered": "apps.institutions.services.register_institution",
    "account_confirmed": "apps.accounts.services.confirm_email",
    "institution_verified": "apps.institutions.services.verify",
    "website_import_started": "apps.artists.website_import.start_import",
    "website_import_finished": "apps.artists.website_import._finish",
    "profile_published": "apps.profiles.publication.publish",
    "profile_withdrawn": "apps.profiles.publication.withdraw",
    "catalog_searched": "apps.catalog.filters.record_search",
    "catalog_no_results": "apps.catalog.filters.record_search",
    "catalog_notice_cta_clicked": "apps.catalog.filters.record_notice_click",
}
PENDING = set(EVENT_CATALOG) - set(EMITTERS)


def test_catalog_has_the_agreed_events():
    assert set(EVENT_CATALOG) == {
        "artist_registered",
        "institution_registered",
        "account_confirmed",
        "institution_verified",
        "website_import_started",
        "website_import_finished",
        "profile_generated",
        "profile_published",
        "profile_withdrawn",
        "inquiry_sent",
        "inquiry_answered",
        "offer_accepted",
        "performance_confirmed",
        "notice_published",
        "notice_applied",
        "catalog_searched",
        "catalog_no_results",
        "catalog_notice_cta_clicked",
    }


@pytest.mark.parametrize("name", sorted(EVENT_CATALOG))
def test_catalog_entry_is_valid(name):
    props = EVENT_CATALOG[name]
    assert name == name.lower() and " " not in name
    for forbidden in ("email", "name", "phone", "ip", "message", "text"):
        assert forbidden not in props


@pytest.mark.parametrize("name", sorted(EVENT_CATALOG))
def test_every_catalog_entry_has_emitter_or_is_pending(name):
    """Contract scaffold: once a feature emits the event, move it from PENDING to EMITTERS."""
    assert name in EMITTERS or name in PENDING


@pytest.mark.parametrize("name", sorted(EMITTERS))
def test_emitter_exists_and_mentions_the_event(name):
    """The listed emitter is real code that records this event (behaviour is tested in the
    owning app: apps/artists/tests, apps/accounts/tests)."""
    import importlib
    import inspect

    module_path, func_name = EMITTERS[name].rsplit(".", 1)
    func = getattr(importlib.import_module(module_path), func_name)
    assert f'"{name}"' in inspect.getsource(func)


def test_track_records_event():
    event = services.track("inquiry_sent", inquiry_id=7, artist_count=2)
    event.refresh_from_db()
    assert event.name == "inquiry_sent"
    assert event.properties == {"inquiry_id": 7, "artist_count": 2}
    assert event.actor == "" and event.object_type == "" and event.created_at


def test_track_rejects_email_property():
    with pytest.raises(services.DisallowedProperty):
        services.track("inquiry_sent", email="a@example.invalid")
    assert Event.objects.count() == 0


def test_track_rejects_unknown_event():
    with pytest.raises(services.UnknownEvent):
        services.track("page_exploded")
    assert Event.objects.count() == 0


def test_track_pseudonymises_actor_and_stores_object(django_user_model):
    user = django_user_model.objects.create_user(email="x@example.invalid", password="pw-12345678")
    event = services.track("artist_registered", actor=user, obj=user, source="form")
    assert event.object_type == "accounts.user" and event.object_id == str(user.pk)
    assert len(event.actor) == 32 and str(user.pk) != event.actor
    assert event.actor == services.actor_id(user)
    assert "x@example.invalid" not in repr(event.__dict__)


def test_institution_verified_contract():
    """`institution_verified` takes only `method` (an enum value), nothing personal (D39)."""
    from apps.institutions.models import VerificationMethod

    assert EVENT_CATALOG["institution_verified"] == frozenset({"method"})
    for method in VerificationMethod.values:
        services.track("institution_verified", method=method)
    with pytest.raises(services.DisallowedProperty):
        services.track("institution_verified", method="manual", institution_name="SP 5")


def test_website_import_events_contract():
    """US-2.2: counts, a status code and a duration only; never the URL or contact data."""
    assert EVENT_CATALOG["website_import_started"] == frozenset()
    assert EVENT_CATALOG["website_import_finished"] == frozenset(
        {"status", "page_count", "photo_count", "duration_ms"}
    )
    services.track(
        "website_import_finished", status="done", page_count=3, photo_count=2, duration_ms=900
    )
    for name, props in (
        ("website_import_started", {"url": "https://example.invalid/"}),
        ("website_import_finished", {"url": "https://example.invalid/"}),
        ("website_import_finished", {"host": "example.invalid"}),
    ):
        with pytest.raises(services.DisallowedProperty):
            services.track(name, **props)


def test_actor_id_anonymous_is_empty():
    assert services.actor_id(None) == ""


def test_profile_publication_events_contract():
    """US-2.8: ids and a percentage only; never the name, slug, e-mail or text."""
    assert EVENT_CATALOG["profile_published"] == frozenset({"profile_id", "completeness_percent"})
    assert EVENT_CATALOG["profile_withdrawn"] == frozenset({"profile_id"})
    services.track("profile_published", profile_id=1, completeness_percent=80)
    services.track("profile_withdrawn", profile_id=1)
    for name, props in (
        ("profile_published", {"slug": "teatr"}),
        ("profile_withdrawn", {"artist_name": "Teatr"}),
        ("profile_withdrawn", {"email": "a@example.invalid"}),
    ):
        with pytest.raises(services.DisallowedProperty):
            services.track(name, **props)
