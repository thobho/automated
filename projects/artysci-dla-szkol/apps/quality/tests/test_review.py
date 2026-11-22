"""Manual review of generations `do przeglądu` (US-2.5C): service, audit row and admin."""

import pytest
from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse

from apps.accounts.tests.conftest import make_admin
from apps.profiles.tests.factories import make_seed_artist
from apps.quality import services
from apps.quality.models import Generation, GenerationReview, RegistryImmutable

from .fake_generator import run

pytestmark = pytest.mark.django_db

REPORT = {
    "ok": False,
    "hard": [
        {"rule": "fakty", "path": "$.facts[0].value", "message": "Bez nawiasów.", "value": ""}
    ],
    "soft": [],
    "repair": {"rounds": 2, "stopped": ""},
}


@pytest.fixture
def waiting():
    """A generation that is `do przeglądu` (the fake generator ends in review)."""
    generation = run(make_seed_artist())
    assert generation.status == Generation.Status.REVIEW
    return generation


@pytest.fixture
def staff():
    return make_admin()


def staff_client(user):
    client = Client()
    client.force_login(user)
    return client


def test_staff_marks_a_generation_ready_with_an_audit_row(waiting, staff):
    done = services.review_generation(waiting, staff, "ready", "  Sprawdzone ręcznie ")
    assert done.status == Generation.Status.READY
    entry = GenerationReview.objects.get()
    assert (entry.generation_id, entry.reviewer, entry.decision) == (waiting.pk, staff, "ready")
    assert entry.note == "Sprawdzone ręcznie" and entry.created_at is not None


def test_marking_error_gives_the_artist_a_neutral_reason(waiting, staff):
    done = services.review_generation(waiting, staff, "error", "Fałszywe liczby")
    assert done.status == Generation.Status.ERROR
    assert "Fałszywe" not in " ".join(done.warnings)


@pytest.mark.parametrize(
    "decision, note, error",
    [
        ("ready", "", services.GenerationError),
        ("ready", "   ", services.GenerationError),
        ("review", "x", services.GenerationError),
        ("running", "x", services.GenerationError),
    ],
)
def test_a_bad_decision_or_empty_note_is_refused(waiting, staff, decision, note, error):
    with pytest.raises(error):
        services.review_generation(waiting, staff, decision, note)
    assert Generation.objects.get(pk=waiting.pk).status == Generation.Status.REVIEW
    assert GenerationReview.objects.count() == 0


def test_a_non_staff_user_cannot_review(waiting):
    user = get_user_model().objects.create_user(email="zwykly@example.invalid")
    with pytest.raises(PermissionError):
        services.review_generation(waiting, user, "ready", "x")
    assert Generation.objects.get(pk=waiting.pk).status == Generation.Status.REVIEW


def test_only_a_generation_waiting_for_review_can_be_reviewed(waiting, staff):
    services.review_generation(waiting, staff, "ready", "ok")
    with pytest.raises(services.GenerationError):
        services.review_generation(waiting, staff, "error", "jeszcze raz")
    assert GenerationReview.objects.count() == 1


def test_a_reviewed_generation_stays_append_only(waiting, staff):
    done = services.review_generation(waiting, staff, "ready", "ok")
    done.warnings = ["zmiana"]
    with pytest.raises(RegistryImmutable):
        done.save()
    entry = GenerationReview.objects.get()
    entry.note = "inna"
    with pytest.raises(RegistryImmutable):
        entry.save()
    with pytest.raises(RegistryImmutable):
        entry.delete()


def test_a_finished_ready_generation_cannot_be_reviewed(staff):
    other = run(make_seed_artist("inny@example.invalid"))
    with pytest.raises(RegistryImmutable):
        other.save()  # still guarded without the review flag


# --- admin -----------------------------------------------------------------------------------

LIST = "admin:quality_reviewqueue_changelist"


def with_findings(generation):
    generation._closing_review = True  # tests only: attach a report to the waiting row
    generation.report = REPORT
    generation.save()
    return generation


def test_staff_sees_only_generations_waiting_for_review_with_findings(waiting, staff):
    with_findings(waiting)
    ready = run(make_seed_artist("gotowy@example.invalid"))
    services_ready = Generation.objects.get(pk=ready.pk)
    assert services_ready.status == Generation.Status.REVIEW  # fake generator: also in review
    page = staff_client(staff).get(reverse(LIST))
    body = page.content.decode()
    assert page.status_code == 200
    assert "$.facts[0].value" in body and "Bez nawiasów." in body


def test_the_list_hides_other_statuses(waiting, staff):
    services.review_generation(waiting, staff, "ready", "ok")
    page = staff_client(staff).get(reverse(LIST))
    assert page.status_code == 200
    assert f"/{waiting.pk}/change/" not in page.content.decode()


@pytest.mark.parametrize("action, status", [("mark_ready", "ready"), ("mark_error", "error")])
def test_the_admin_action_closes_the_generation_with_a_note(waiting, staff, action, status):
    response = staff_client(staff).post(
        reverse(LIST),
        {"action": action, "_selected_action": [waiting.pk], "note": "Sprawdzone", "index": 0},
        follow=True,
    )
    assert response.status_code == 200
    assert Generation.objects.get(pk=waiting.pk).status == status
    entry = GenerationReview.objects.get()
    assert entry.reviewer == staff and entry.note == "Sprawdzone" and entry.decision == status


def test_the_admin_action_needs_a_note(waiting, staff):
    response = staff_client(staff).post(
        reverse(LIST),
        {"action": "mark_ready", "_selected_action": [waiting.pk], "note": " ", "index": 0},
        follow=True,
    )
    assert "Podaj notatkę" in response.content.decode()
    assert Generation.objects.get(pk=waiting.pk).status == Generation.Status.REVIEW


def test_a_non_staff_user_cannot_open_the_list_or_run_the_action(waiting):
    user = get_user_model().objects.create_user(email="zwykly@example.invalid")
    client = staff_client(user)
    assert client.get(reverse(LIST)).status_code == 302  # to the admin login
    response = client.post(
        reverse(LIST), {"action": "mark_ready", "_selected_action": [waiting.pk], "note": "x"}
    )
    assert response.status_code == 302
    assert Generation.objects.get(pk=waiting.pk).status == Generation.Status.REVIEW
    assert GenerationReview.objects.count() == 0


def test_staff_without_the_permission_cannot_run_the_action(waiting):
    user = get_user_model().objects.create_user(email="personel@example.invalid", is_staff=True)
    client = staff_client(user)
    assert client.get(reverse(LIST)).status_code == 403
    client.post(reverse(LIST), {"action": "mark_ready", "_selected_action": [waiting.pk]})
    assert Generation.objects.get(pk=waiting.pk).status == Generation.Status.REVIEW


def test_the_audit_list_is_read_only(waiting, staff):
    services.review_generation(waiting, staff, "ready", "ok")
    client = staff_client(staff)
    assert client.get(reverse("admin:quality_generationreview_changelist")).status_code == 200
    assert client.get(reverse("admin:quality_generationreview_add")).status_code == 403
