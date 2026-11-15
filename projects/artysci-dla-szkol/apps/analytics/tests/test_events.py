import pytest

from apps.analytics import services
from apps.analytics.catalog import EVENT_CATALOG
from apps.analytics.models import Event

pytestmark = pytest.mark.django_db

# Event name -> dotted path of the code that emits it. Filled in as features land (E1+);
# an entry listed in PENDING is a known gap, anything else must have an emitter test.
EMITTERS: dict[str, str] = {}
PENDING = set(EVENT_CATALOG) - set(EMITTERS)


def test_catalog_has_the_agreed_events():
    assert set(EVENT_CATALOG) == {
        "artist_registered",
        "profile_generated",
        "profile_published",
        "inquiry_sent",
        "inquiry_answered",
        "offer_accepted",
        "performance_confirmed",
        "notice_published",
        "notice_applied",
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


def test_actor_id_anonymous_is_empty():
    assert services.actor_id(None) == ""
