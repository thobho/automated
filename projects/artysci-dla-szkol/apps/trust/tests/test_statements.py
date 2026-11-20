"""Artist statements (US-8.2, D104): services with an explicit `now`, the OC expiry job and
the "Oświadczenie artysty" badges."""

import logging
from datetime import UTC, date, datetime, timedelta

import pytest
from django.core import mail
from django.template import Context, Template

from apps.accounts.tests.conftest import make_artist, run_worker
from apps.artists.models import Artist
from apps.core.testing import in_memory_queue
from apps.trust import services, tasks
from apps.trust.errors import (
    DocumentImmutable,
    InvalidStatement,
    NoPublishedVersion,
    StaleWording,
    UnknownKind,
)
from apps.trust.models import STATEMENT_KINDS, ArtistStatement, LegalDocument, StatementReminder
from apps.trust.services import Status

pytestmark = pytest.mark.django_db

EMAIL = "rola.artysta@example.invalid"
# 10:00 UTC = 11:00 in Warsaw on 2026-11-19
NOW = datetime(2026, 11, 19, 10, 0, tzinfo=UTC)
TODAY = date(2026, 11, 19)
YESTERDAY = TODAY - timedelta(days=1)

K = LegalDocument.Kind


@pytest.fixture
def artist():
    return Artist.objects.get(user=make_artist(EMAIL))


@pytest.fixture
def wordings():
    """Placeholder v1 of every statement kind (as `make seed` publishes them)."""
    services.seed_placeholders()
    return {kind: services.current(kind) for kind in STATEMENT_KINDS}


@pytest.fixture
def queue():
    with in_memory_queue() as connector:
        yield connector


def make_all(artist, *, valid_until=None, now=NOW):
    for kind in STATEMENT_KINDS:
        services.make_statement(
            artist,
            kind,
            billing_form="rachunek" if kind == K.BILLING_FORM else "",
            valid_until=valid_until if kind == K.INSURANCE else None,
            now=now,
        )


def state_of(artist, kind, now=NOW):
    return next(s for s in services.statement_overview(artist, now=now) if s.kind == kind)


def counted_kinds(artist, now=NOW):
    return [s.kind for s in services.current_statements(artist, now=now)]


def reminder_jobs(queue):
    return [j for j in queue.jobs.values() if j["task_name"] == "trust.send_insurance_reminder"]


# --- wordings --------------------------------------------------------------------------------


def test_seed_publishes_placeholder_wordings_for_every_statement(wordings):
    for kind, document in wordings.items():
        assert document.version == 1, kind
        assert document.body.startswith("PROJEKT – tekst zastępczy")
    assert services.seed_placeholders() == 0  # idempotent


# --- making statements -----------------------------------------------------------------------


def test_child_protection_statement_stores_version_and_time(artist, wordings):
    assert services.has_child_protection_statement(artist, now=NOW) is False
    row = services.make_statement(artist, K.CHILD_PROTECTION, now=NOW)
    stored = ArtistStatement.objects.get()
    assert stored == row
    assert stored.document == wordings[K.CHILD_PROTECTION]
    assert stored.made_at == NOW and stored.made_at.tzinfo is not None
    assert stored.withdrawn is False
    assert services.has_child_protection_statement(artist, now=NOW) is True
    assert state_of(artist, K.CHILD_PROTECTION).status is Status.CURRENT


def test_no_published_wording_cannot_be_made(artist):
    services.publish(K.CHILD_PROTECTION, "Treść testowa", material=True)
    state = state_of(artist, K.MATERIAL_RIGHTS)
    assert state.status is Status.UNAVAILABLE and state.document is None
    with pytest.raises(NoPublishedVersion):
        services.make_statement(artist, K.MATERIAL_RIGHTS, now=NOW)
    assert not ArtistStatement.objects.exists()


def test_new_wording_version_requires_renewal(artist, wordings):
    v1_row = services.make_statement(artist, K.CHILD_PROTECTION, now=NOW)
    v2 = services.publish(K.CHILD_PROTECTION, "Treść testowa v2", material=False)
    later = NOW + timedelta(days=3)
    state = state_of(artist, K.CHILD_PROTECTION, later)
    assert state.status is Status.OUTDATED and state.latest == v1_row
    assert services.has_child_protection_statement(artist, now=later) is False
    assert K.CHILD_PROTECTION not in counted_kinds(artist, later)

    v2_row = services.make_statement(artist, K.CHILD_PROTECTION, now=later)
    assert v2_row.document == v2 and v2_row.pk != v1_row.pk
    v1_again = ArtistStatement.objects.get(pk=v1_row.pk)
    assert v1_again.document == wordings[K.CHILD_PROTECTION] and v1_again.made_at == NOW
    assert services.has_child_protection_statement(artist, now=later) is True


def test_stale_shown_version_is_refused(artist, wordings):
    shown = wordings[K.CHILD_PROTECTION].pk
    services.publish(K.CHILD_PROTECTION, "Treść testowa v2", material=False)
    with pytest.raises(StaleWording):
        services.make_statement(artist, K.CHILD_PROTECTION, shown_document_id=shown, now=NOW)
    assert not ArtistStatement.objects.exists()
    current = services.current(K.CHILD_PROTECTION).pk
    services.make_statement(artist, K.CHILD_PROTECTION, shown_document_id=current, now=NOW)


def test_billing_form_rachunek_is_stored_with_date_and_version(artist, wordings):
    row = services.make_statement(artist, K.BILLING_FORM, billing_form="rachunek", now=NOW)
    row.refresh_from_db()
    assert row.billing_form == "rachunek"
    assert row.made_at == NOW and row.document.version == 1


@pytest.mark.parametrize("value", ["", "paragon", "FAKTURA", None])
def test_billing_form_outside_the_two_values_is_refused(artist, wordings, value):
    with pytest.raises(InvalidStatement):
        services.make_statement(artist, K.BILLING_FORM, billing_form=value, now=NOW)
    assert not ArtistStatement.objects.exists()


def test_extra_data_on_other_kinds_is_refused(artist, wordings):
    with pytest.raises(InvalidStatement):
        services.make_statement(artist, K.CHILD_PROTECTION, billing_form="faktura", now=NOW)
    with pytest.raises(InvalidStatement):
        services.make_statement(artist, K.MATERIAL_RIGHTS, valid_until=TODAY, now=NOW)
    with pytest.raises(InvalidStatement):
        services.make_statement(artist, K.INSURANCE, valid_until="2026-12-01", now=NOW)
    with pytest.raises(UnknownKind):
        services.make_statement(artist, K.TERMS, now=NOW)
    assert not ArtistStatement.objects.exists()


def test_billing_form_change_is_a_new_row(artist, wordings):
    services.make_statement(artist, K.BILLING_FORM, billing_form="faktura", now=NOW)
    services.make_statement(
        artist, K.BILLING_FORM, billing_form="rachunek", now=NOW + timedelta(hours=1)
    )
    assert ArtistStatement.objects.count() == 2
    assert state_of(artist, K.BILLING_FORM).latest.billing_form == "rachunek"


def test_image_consents_are_separate_statements(artist, wordings):
    services.make_statement(artist, K.IMAGE_ADULTS, now=NOW)
    assert counted_kinds(artist) == [K.IMAGE_ADULTS]
    other = Artist.objects.get(user=make_artist("drugi@example.invalid"))
    services.make_statement(other, K.IMAGE_CHILDREN, now=NOW)
    assert counted_kinds(other) == [K.IMAGE_CHILDREN]
    assert state_of(other, K.IMAGE_ADULTS).status is Status.NOT_MADE


def test_withdrawal_is_a_row_and_stops_counting(artist, wordings):
    made = services.make_statement(artist, K.CHILD_PROTECTION, now=NOW)
    withdrawal = services.withdraw_statement(artist, K.CHILD_PROTECTION, now=NOW)
    assert withdrawal.withdrawn and withdrawal.pk != made.pk
    assert ArtistStatement.objects.count() == 2
    assert services.has_child_protection_statement(artist, now=NOW) is False
    assert state_of(artist, K.CHILD_PROTECTION).status is Status.NOT_MADE
    assert services.withdraw_statement(artist, K.CHILD_PROTECTION, now=NOW) is None
    assert services.withdraw_statement(artist, K.MATERIAL_RIGHTS, now=NOW) is None


def test_rows_are_immutable(artist, wordings):
    row = services.make_statement(artist, K.CHILD_PROTECTION, now=NOW)
    row.withdrawn = True
    with pytest.raises(DocumentImmutable):
        row.save()
    with pytest.raises(DocumentImmutable):
        row.delete()
    with pytest.raises(DocumentImmutable):
        ArtistStatement.objects.filter(pk=row.pk).update(withdrawn=True)
    with pytest.raises(DocumentImmutable):
        ArtistStatement.objects.all().delete()


def test_has_child_protection_statement_for_none():
    assert services.has_child_protection_statement(None) is False


def test_logs_carry_no_email(artist, wordings, caplog):
    with caplog.at_level(logging.INFO, logger="apps.trust.statements"):
        make_all(artist, valid_until=YESTERDAY)
        services.withdraw_statement(artist, K.IMAGE_ADULTS, now=NOW)
    assert caplog.records
    assert all(EMAIL not in r.getMessage() and "@" not in r.getMessage() for r in caplog.records)
    assert all(getattr(r, "user", "") != artist.user_id for r in caplog.records)


# --- OC expiry -------------------------------------------------------------------------------


def test_oc_valid_until_yesterday_expires_and_reminds_once(artist, wordings, queue):
    make_all(artist, valid_until=YESTERDAY, now=NOW - timedelta(days=30))
    assert K.INSURANCE in counted_kinds(artist, NOW - timedelta(days=2))
    assert K.INSURANCE not in counted_kinds(artist, NOW)
    assert state_of(artist, K.INSURANCE).status is Status.EXPIRED

    assert services.queue_insurance_reminders(now=NOW) == 1
    jobs = reminder_jobs(queue)
    assert len(jobs) == 1
    assert jobs[0]["queue_name"] == "email"
    assert jobs[0]["args"] == {"statement_id": state_of(artist, K.INSURANCE).latest.pk}
    assert EMAIL not in repr(queue.jobs)  # ids only in the job table

    assert services.queue_insurance_reminders(now=NOW) == 0
    assert services.queue_insurance_reminders(now=NOW + timedelta(days=1)) == 0
    assert len(reminder_jobs(queue)) == 1
    assert StatementReminder.objects.count() == 1


def test_oc_valid_until_today_still_counts(artist, wordings, queue):
    services.make_statement(artist, K.INSURANCE, valid_until=TODAY, now=NOW)
    assert counted_kinds(artist) == [K.INSURANCE]
    assert services.queue_insurance_reminders(now=NOW) == 0


def test_oc_without_date_counts_until_withdrawn_and_job_ignores_it(artist, wordings, queue):
    services.make_statement(artist, K.INSURANCE, now=NOW)
    far = NOW + timedelta(days=3650)
    assert counted_kinds(artist, far) == [K.INSURANCE]
    assert services.queue_insurance_reminders(now=far) == 0
    assert reminder_jobs(queue) == []
    services.withdraw_statement(artist, K.INSURANCE, now=far)
    assert counted_kinds(artist, far) == []


def test_renewed_or_withdrawn_oc_gets_no_reminder(artist, wordings, queue):
    services.make_statement(artist, K.INSURANCE, valid_until=YESTERDAY, now=NOW - timedelta(9))
    services.make_statement(artist, K.INSURANCE, valid_until=date(2027, 11, 19), now=NOW)
    assert services.queue_insurance_reminders(now=NOW) == 0
    other = Artist.objects.get(user=make_artist("drugi@example.invalid"))
    services.make_statement(other, K.INSURANCE, valid_until=YESTERDAY, now=NOW - timedelta(9))
    services.withdraw_statement(other, K.INSURANCE, now=NOW)
    assert services.queue_insurance_reminders(now=NOW) == 0


def test_new_expiry_after_renewal_gets_its_own_reminder(artist, wordings, queue):
    services.make_statement(artist, K.INSURANCE, valid_until=YESTERDAY, now=NOW - timedelta(9))
    assert services.queue_insurance_reminders(now=NOW) == 1
    services.make_statement(artist, K.INSURANCE, valid_until=TODAY, now=NOW)
    assert services.queue_insurance_reminders(now=NOW + timedelta(days=1)) == 1
    assert len(reminder_jobs(queue)) == 2


def test_periodic_job_queues_and_email_job_sends_plain_polish_text(artist, wordings, queue, caplog):
    services.make_statement(artist, K.INSURANCE, valid_until=YESTERDAY, now=NOW - timedelta(9))
    with caplog.at_level(logging.INFO):
        tasks.check_insurance_expiry(timestamp=int(NOW.timestamp()))
        tasks.check_insurance_expiry(timestamp=int(NOW.timestamp()))
        jobs = reminder_jobs(queue)
        assert len(jobs) == 1
        tasks.send_insurance_reminder(**jobs[0]["args"])
    assert len(mail.outbox) == 1
    message = mail.outbox[0]
    assert message.to == [EMAIL]
    assert message.subject == "Twoje oświadczenie o ubezpieczeniu OC wygasło"
    assert "ważne do 18 listopada 2026" in message.body
    assert "Oświadczenia" in message.body
    assert not message.alternatives  # plain text only
    assert all(EMAIL not in r.getMessage() for r in caplog.records)


@pytest.mark.django_db(transaction=True)
def test_worker_runs_the_reminder_job(artist, wordings, queue):
    services.make_statement(artist, K.INSURANCE, valid_until=YESTERDAY, now=NOW - timedelta(9))
    assert services.queue_insurance_reminders(now=NOW) == 1
    run_worker()
    assert [j["status"] for j in reminder_jobs(queue)] == ["succeeded"]
    assert len(mail.outbox) == 1 and mail.outbox[0].to == [EMAIL]


def test_reminder_email_skips_missing_or_inactive(artist, wordings):
    assert services.send_insurance_reminder(999999) is False
    row = services.make_statement(artist, K.INSURANCE, valid_until=YESTERDAY, now=NOW)
    artist.user.is_active = False
    artist.user.save()
    assert services.send_insurance_reminder(row.pk) is False
    assert mail.outbox == []


def test_periodic_task_is_scheduled_daily():
    from procrastinate.contrib.django import app

    crons = {task.task.name: task.cron for task in app.periodic_registry.periodic_tasks.values()}
    assert crons["trust.check_insurance_expiry"] == "0 7 * * *"
    assert tasks.send_insurance_reminder.queue == "email"


# --- badges ----------------------------------------------------------------------------------


def render_badges(artist) -> str:
    template = Template("{% load statements %}{% artist_statement_badges artist %}")
    return template.render(Context({"artist": artist}))


def test_badges_show_label_and_counted_statements_only(artist, wordings, monkeypatch):
    from django.utils import timezone

    monkeypatch.setattr(timezone, "now", lambda: NOW)
    assert render_badges(artist).strip() == ""
    make_all(artist, valid_until=YESTERDAY)
    html = render_badges(artist)
    assert "Oświadczenie artysty" in html
    assert "Serwis ich nie sprawdza" in html
    assert "Forma rozliczenia: rachunek" in html
    assert 'data-kind="child_protection"' in html
    assert 'data-kind="insurance"' not in html  # expired
    for word in ("zweryfikowany", "rejestr karny"):
        assert word not in html.lower()


def test_badges_show_oc_date(artist, wordings, monkeypatch):
    from django.utils import timezone

    monkeypatch.setattr(timezone, "now", lambda: NOW)
    services.make_statement(artist, K.INSURANCE, valid_until=date(2027, 3, 1), now=NOW)
    assert "ważne do 1 marca 2027" in render_badges(artist)
    assert render_badges(None).strip() == ""


def test_statement_str(artist, wordings):
    row = services.make_statement(artist, K.INSURANCE, valid_until=YESTERDAY, now=NOW)
    reminder = StatementReminder.objects.create(statement=row, queued_at=NOW)
    assert str(row) == f"Statement {row.pk} (insurance)"
    assert str(reminder) == f"Reminder for statement {row.pk}"
