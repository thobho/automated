import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser

from apps.analytics.models import Event
from apps.institutions import services
from apps.institutions.models import Institution, InstitutionMember, RspoEntry
from apps.institutions.services import InstitutionDetails, Registration
from apps.trust import services as trust
from apps.trust.errors import NoPublishedVersion
from apps.trust.models import LegalAcceptance

from .conftest import IP, NEW_EMAIL, OPOLE, TYPED_NAME, WROCLAW, jobs_for

pytestmark = pytest.mark.django_db

BASE = "http://testserver/"
TYPED = InstitutionDetails("other", f"  {TYPED_NAME} ", " Zębowice ", "opolskie")


def _register(email=NEW_EMAIL, details=TYPED, function="director", rspo_number=None):
    return services.register_institution(
        email, details, function, IP, rspo_number=rspo_number, link_base=BASE
    )


# --- RSPO ------------------------------------------------------------------------------------


def test_normalise():
    assert services.normalise("  Szkoła   PODSTAWOWA\tŁódź ") == "szkoła podstawowa łódź"


def test_add_rspo_entry_inserts_and_updates(db):
    entry, created = services.add_rspo_entry(1, " Szkoła  A ", "other", "Łódź", "lodzkie")
    assert created and entry.name == "Szkoła A"
    assert (entry.name_search, entry.locality_search) == ("szkoła a", "łódź")
    entry, created = services.add_rspo_entry(1, "Szkoła B", "other", "Łódź", "lodzkie")
    assert not created and RspoEntry.objects.get().name == "Szkoła B"
    assert str(entry) == "Szkoła B (Łódź, RSPO 1)"


def test_suggest_narrows_by_locality(rspo):
    found = services.suggest_rspo("szkoła podstawowa nr 5", "Wrocław")
    assert [e.rspo_number for e in found] == [WROCLAW]
    both = {e.rspo_number for e in services.suggest_rspo("szkoła podstawowa nr 5")}
    assert both == {WROCLAW, OPOLE}


def test_suggest_is_case_insensitive_also_for_polish_letters(rspo):
    assert [e.rspo_number for e in services.suggest_rspo("SŁONECZKO", "ŁÓDŹ")] == [900003]
    assert [e.rspo_number for e in services.suggest_rspo("podstawowa 5", "opo")] == [OPOLE]


@pytest.mark.parametrize("query", ["", "sz", "  s ", "ab"])
def test_suggest_needs_three_characters(rspo, query):
    assert services.suggest_rspo(query) == []


def test_suggest_returns_at_most_ten(db):
    for n in range(1, 13):
        services.add_rspo_entry(n, f"Szkoła Testowa {n:02d}", "other", "Opole", "opolskie")
    assert len(services.suggest_rspo("szkoła testowa")) == 10


def test_rspo_entry(rspo):
    assert services.rspo_entry(WROCLAW) == rspo[WROCLAW]
    assert services.rspo_entry(None) is None
    assert services.rspo_entry(1) is None


def test_seed_rspo_is_idempotent(db):
    assert services.seed_rspo() == len(services.SEED_RSPO)
    assert services.seed_rspo() == 0
    assert RspoEntry.objects.count() == len(services.SEED_RSPO)


# --- registration ----------------------------------------------------------------------------


def test_register_typed_institution(documents, queue, clock):
    assert _register() is Registration.SENT
    member = InstitutionMember.objects.select_related("institution", "user").get()
    institution = member.institution
    assert (institution.name, institution.locality) == (TYPED_NAME, "Zębowice")
    assert institution.institution_type == "other" and institution.voivodeship == "opolskie"
    assert institution.rspo_number is None and institution.verification_status == "unverified"
    assert institution.get_verification_status_display() == "niezweryfikowana"
    assert member.function == "director" and not member.needs_review
    assert member.user.email == NEW_EMAIL and member.user.email_confirmed_at is None
    assert LegalAcceptance.objects.filter(user=member.user).count() == 2
    (job,) = jobs_for(queue)
    assert job["args"]["next_path"] == "/placowka/"
    event = Event.objects.get(name="institution_registered")
    assert event.properties == {
        "institution_type": "other",
        "rspo_matched": False,
        "linked_existing": False,
    }


def test_register_with_rspo_ignores_typed_values(documents, queue, clock, rspo):
    assert _register(rspo_number=WROCLAW) is Registration.SENT
    institution = Institution.objects.get()
    assert (institution.name, institution.locality, institution.voivodeship) == (
        "Szkoła Podstawowa nr 5",
        "Wrocław",
        "dolnoslaskie",
    )
    assert institution.institution_type == "primary_school"
    assert institution.rspo_number == WROCLAW
    assert Event.objects.get().properties["rspo_matched"] is True


def test_second_member_is_linked_for_review(documents, queue, clock, rspo):
    _register(rspo_number=WROCLAW)
    _register(email="druga.osoba@example.invalid", function="teacher", rspo_number=WROCLAW)
    assert Institution.objects.count() == 1
    first, second = InstitutionMember.objects.order_by("pk")
    assert first.institution_id == second.institution_id
    assert (first.needs_review, second.needs_review) == (False, True)
    linked = Event.objects.filter(name="institution_registered").order_by("pk").last()
    assert linked.properties["linked_existing"] is True


def test_concurrent_rspo_registration_links(documents, queue, clock, rspo, monkeypatch):
    """Another request created the institution between the lookup and the insert."""
    other = Institution.objects.create(
        institution_type="primary_school",
        name="x",
        locality="Wrocław",
        voivodeship="dolnoslaskie",
        rspo_number=WROCLAW,
    )
    # The lookup misses it (as if it ran first); the insert then hits the unique number.
    monkeypatch.setattr(Institution.objects, "filter", lambda **kw: Institution.objects.none())
    assert _register(rspo_number=WROCLAW) is Registration.SENT
    assert InstitutionMember.objects.get().institution == other
    assert Institution.objects.count() == 1
    assert InstitutionMember.objects.get().needs_review


def test_register_existing_address_changes_nothing(documents, queue, clock):
    user = get_user_model().objects.create_user(email=NEW_EMAIL)
    assert _register() is Registration.SENT
    assert not Institution.objects.exists() and not InstitutionMember.objects.exists()
    assert not LegalAcceptance.objects.exists() and not Event.objects.exists()
    (job,) = jobs_for(queue)
    assert job["args"]["user_id"] == user.pk and job["args"]["next_path"] == ""


def test_register_unavailable_without_documents(db, queue, clock):
    trust.publish("privacy", "Polityka", material=True)
    assert _register() is Registration.UNAVAILABLE
    assert not get_user_model().objects.exists() and not Institution.objects.exists()


def test_document_withdrawn_mid_registration_rolls_back(documents, queue, clock, monkeypatch):
    def gone(user, kinds):
        raise NoPublishedVersion("terms")

    monkeypatch.setattr(trust, "record_acceptance", gone)
    assert _register() is Registration.UNAVAILABLE
    assert not get_user_model().objects.exists()
    assert not Institution.objects.exists() and not InstitutionMember.objects.exists()
    assert jobs_for(queue) == []


def test_register_rate_limited(documents, queue, clock, settings):
    settings.LOGIN_EMAIL_LIMIT_PER_ADDRESS = 0
    assert _register() is Registration.RATE_LIMITED
    assert not get_user_model().objects.exists() and not Institution.objects.exists()


def test_rate_limit_reached_between_check_and_send(documents, queue, clock, monkeypatch):
    monkeypatch.setattr(services.accounts, "request_login", lambda *a, **k: False)
    assert _register() is Registration.RATE_LIMITED


def test_member_for(documents, queue, clock):
    _register()
    user = get_user_model().objects.get()
    member = services.member_for(user)
    assert member == user.institution_member
    assert str(member) == f"InstitutionMember {member.pk}"
    assert str(member.institution) == TYPED_NAME
    assert services.member_for(AnonymousUser()) is None
