from procrastinate.contrib.django import app

from apps.core.jobs import QUEUE_DEFAULT, QUEUE_EMAIL, default_retry

from . import services


@app.task(name="accounts.send_login_email", queue=QUEUE_EMAIL, retry=default_retry())
def send_login_email(user_id: int, link_base: str, next_path: str = "") -> None:
    """Create a login challenge and e-mail it. Only the user id, the site origin and a local
    path are job arguments: the code and token never reach the jobs table."""
    services.send_login_email(user_id, link_base, next_path)


@app.task(name="accounts.send_email_change_email", queue=QUEUE_EMAIL, retry=default_retry())
def send_email_change_email(change_id: int, link_base: str) -> None:
    """Confirmation link and code to the new address, notice to the old one (US-1.6). Only the
    request id and the site origin are job arguments: no address, code or token."""
    services.send_email_change_email(change_id, link_base)


@app.task(name="accounts.send_email_change_notice", queue=QUEUE_EMAIL, retry=default_retry())
def send_email_change_notice(user_id: int) -> None:
    """Only the notice to the current address (the requested one is in use)."""
    services.send_email_change_notice(user_id)


@app.periodic(cron="15 4 * * *")
@app.task(
    name="accounts.purge_expired", queue=QUEUE_DEFAULT, queueing_lock="accounts.purge_expired"
)
def purge_expired(timestamp: int) -> None:
    """Daily: drop old login challenges, throttle events and expired sessions."""
    services.purge_expired()
