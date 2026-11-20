"""Institution verification (US-1.4): domain rule, manual approval, badge, event."""

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from apps.accounts import services as accounts
from apps.analytics.models import Event
from apps.institutions import services
from apps.institutions.models import Institution, InstitutionMember, VerificationStatus

from .rspo_fixture import ROWS, build

pytestmark = pytest.mark.django_db

RSPO = 990001
CHANGELIST = reverse("admin:institutions_institution_changelist")


def make_member(email, *, rspo_domain="sp5.example.invalid", rspo_number=RSPO, confirmed=False):
    if rspo_number is not None:
        services.add_rspo_entry(
            rspo_number, "SP 5", "primary_school", "Wrocław", "dolnoslaskie", rspo_domain
        )
    institution, _ = Institution.objects.get_or_create(
        rspo_number=rspo_number,
        defaults={
            "institution_type": "primary_school",
            "name": "SP 5",
            "locality": "Wrocław",
            "voivodeship": "dolnoslaskie",
        },
    )
    user = get_user_model().objects.create_user(email=email)
    if confirmed:
        accounts.confirm_email(user)
    InstitutionMember.objects.create(user=user, institution=institution, function="director")
    return user, institution


def verified_events():
    return Event.objects.filter(name="institution_verified")


# --- domain rule -----------------------------------------------------------------------------


def test_member_on_the_rspo_domain_verifies_on_confirmation():
    user, institution = make_member("dyrektor@sp5.example.invalid")
    accounts.confirm_email(user)
    institution.refresh_from_db()
    assert institution.verification_status == VerificationStatus.VERIFIED
    assert institution.verification_method == "domain"
    assert institution.verified_at is not None and institution.verified_by is None
    assert services.is_verified(institution)
    assert verified_events().count() == 1
    event = verified_events().get()
    assert event.properties == {"method": "domain"}
    assert event.object_id == str(institution.pk)


def test_domain_match_ignores_case():
    user, institution = make_member(
        "Dyrektor@SP5.Example.Invalid", rspo_domain="sp5.example.invalid"
    )
    accounts.confirm_email(user)
    institution.refresh_from_db()
    assert services.is_verified(institution)


def test_public_mailbox_domain_never_verifies():
    user, institution = make_member("szkola.sp5@gmail.com", rspo_domain="gmail.com")
    accounts.confirm_email(user)
    institution.refresh_from_db()
    assert institution.verification_status == VerificationStatus.UNVERIFIED
    assert not verified_events().exists()


def test_other_domain_does_not_verify():
    user, institution = make_member(
        "dyrektor@sp5.example.invalid", rspo_domain="sp6.example.invalid"
    )
    accounts.confirm_email(user)
    institution.refresh_from_db()
    assert institution.verification_status == VerificationStatus.UNVERIFIED


@pytest.mark.parametrize(
    "email", ["a@mail.sp5.example.invalid", "a@example.invalid", "a@sp5.example.invalid.pl"]
)
def test_no_subdomain_or_parent_domain_guessing(email):
    user, institution = make_member(email)
    accounts.confirm_email(user)
    institution.refresh_from_db()
    assert not services.is_verified(institution)


def test_no_rspo_number_or_no_rspo_domain_does_not_verify():
    user, institution = make_member("a@sp5.example.invalid", rspo_number=None)
    accounts.confirm_email(user)
    assert not services.check_domain(institution)
    user2, institution2 = make_member("b@sp5.example.invalid", rspo_number=990002, rspo_domain="")
    accounts.confirm_email(user2)
    institution2.refresh_from_db()
    assert not services.is_verified(institution2)


def test_unconfirmed_member_does_not_verify_after_import():
    _, institution = make_member("dyrektor@sp5.example.invalid", rspo_domain="")
    report = services.import_rspo(build())  # 990001 gets sp5.example.invalid
    institution.refresh_from_db()
    assert report.verified == 0 and not services.is_verified(institution)


def test_import_verifies_institutions_of_confirmed_members():
    _, institution = make_member("dyrektor@sp5.example.invalid", rspo_domain="", confirmed=True)
    institution.refresh_from_db()
    assert not services.is_verified(institution)  # RSPO had no domain yet
    first = services.import_rspo(build())
    second = services.import_rspo(build())
    institution.refresh_from_db()
    assert (first.verified, second.verified) == (1, 0)
    assert institution.verification_method == "domain"
    assert verified_events().count() == 1


def test_confirming_a_user_without_institution_is_fine():
    user = get_user_model().objects.create_user(email="artysta@sp5.example.invalid")
    assert accounts.confirm_email(user)
    assert not services.check_domain_for_user(user)


def test_domain_matches_helper():
    assert services.domain_matches("x@SP5.example.invalid", "sp5.example.invalid")
    assert not services.domain_matches("x@wp.pl", "wp.pl")
    assert not services.domain_matches("brak", "sp5.example.invalid")
    assert "gmail.com" in services.PUBLIC_MAILBOX_DOMAINS


# --- manual approval -------------------------------------------------------------------------


def test_verify_twice_records_one_event(admin_user):
    _, institution = make_member("a@sp5.example.invalid")
    assert services.verify(institution, "manual", by=admin_user)
    first = institution.verified_at
    assert not services.verify(institution, "domain")
    institution.refresh_from_db()
    assert (institution.verification_method, institution.verified_at) == ("manual", first)
    assert verified_events().count() == 1


def test_staff_approve_action(staff_client, admin_user):
    _, institution = make_member("a@sp5.example.invalid")
    response = staff_client.post(
        CHANGELIST, {"action": "approve", "_selected_action": [institution.pk]}, follow=True
    )
    assert response.status_code == 200
    assert "Zatwierdzono 1 placówkę." in response.content.decode()
    institution.refresh_from_db()
    assert institution.verification_status == VerificationStatus.VERIFIED
    assert institution.verification_method == "manual"
    assert institution.verified_by == admin_user and institution.verified_at is not None
    event = verified_events().get()
    assert event.properties == {"method": "manual"} and event.actor


def test_approving_a_verified_institution_changes_nothing(staff_client, admin_user):
    _, institution = make_member("a@sp5.example.invalid", confirmed=False)
    services.verify(institution, "domain")
    before = Institution.objects.get(pk=institution.pk)
    response = staff_client.post(
        CHANGELIST, {"action": "approve", "_selected_action": [institution.pk]}, follow=True
    )
    assert "Zatwierdzono 0 placówek." in response.content.decode()
    after = Institution.objects.get(pk=institution.pk)
    assert (after.verification_method, after.verified_at, after.verified_by) == (
        before.verification_method,
        before.verified_at,
        None,
    )
    assert verified_events().count() == 1


def test_action_is_listed_for_staff(staff_client):
    make_member("a@sp5.example.invalid")
    page = staff_client.get(CHANGELIST).content.decode()
    assert 'value="approve"' in page and "Zatwierdź placówkę" in page


def test_non_staff_cannot_reach_the_action(documents):
    from apps.trust import services as trust

    member, institution = make_member("a@sp5.example.invalid")
    trust.record_acceptance(member, ["terms", "privacy"])
    client = Client()
    client.force_login(member)
    response = client.post(CHANGELIST, {"action": "approve", "_selected_action": [institution.pk]})
    assert response.status_code == 302 and "/login/" in response["Location"]
    institution.refresh_from_db()
    assert not services.is_verified(institution)
    assert not verified_events().exists()


def test_verification_fields_are_read_only_in_admin(staff_client):
    _, institution = make_member("a@sp5.example.invalid")
    url = reverse("admin:institutions_institution_change", args=[institution.pk])
    page = staff_client.get(url).content.decode()
    assert 'name="verification_status"' not in page and 'name="verified_by"' not in page


# --- badge -----------------------------------------------------------------------------------


def start_page(user):
    from apps.trust import services as trust

    trust.record_acceptance(user, ["terms", "privacy"])
    client = Client()
    client.force_login(user)
    return client.get(reverse("institutions:start"))


def test_badge_on_the_start_page_of_a_verified_institution(documents):
    user, institution = make_member("a@sp5.example.invalid")
    services.verify(institution, "manual")
    response = start_page(user)
    assert response.status_code == 200
    assert 'data-badge="institution-verified"' in response.content.decode()
    assert "Zweryfikowana placówka" in response.content.decode()


def test_no_badge_for_an_unverified_institution(documents):
    user, _ = make_member("a@sp5.example.invalid")
    response = start_page(user)
    assert response.status_code == 200
    assert 'data-badge="institution-verified"' not in response.content.decode()


def test_badge_tag_renders_nothing_for_none():
    from django.template import Context, Template

    html = Template("{% load institutions %}[{% institution_badge none %}]").render(
        Context({"none": None})
    )
    assert html.replace("\n", "") == "[]"


def test_rows_fixture_is_synthetic():
    assert all(str(row[0]).startswith("99") for row in ROWS)
