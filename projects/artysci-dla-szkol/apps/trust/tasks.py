from procrastinate.contrib.django import app

from apps.core.jobs import QUEUE_DEFAULT, QUEUE_EMAIL, default_retry

from . import services


@app.task(name="trust.send_insurance_reminder", queue=QUEUE_EMAIL, retry=default_retry())
def send_insurance_reminder(statement_id: int) -> None:
    """The OC expiry reminder (US-8.2). Only the statement id is a job argument: no address."""
    services.send_insurance_reminder(statement_id)


@app.periodic(cron="0 7 * * *")
@app.task(
    name="trust.check_insurance_expiry",
    queue=QUEUE_DEFAULT,
    queueing_lock="trust.check_insurance_expiry",
)
def check_insurance_expiry(timestamp: int) -> None:
    """Daily: expired OC statements stop counting (by date) and get one reminder each."""
    services.queue_insurance_reminders()
