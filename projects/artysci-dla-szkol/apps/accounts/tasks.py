from procrastinate.contrib.django import app

from apps.core.jobs import QUEUE_DEFAULT, QUEUE_EMAIL, default_retry

from . import services


@app.task(name="accounts.send_login_email", queue=QUEUE_EMAIL, retry=default_retry())
def send_login_email(user_id: int, link_base: str, next_path: str = "") -> None:
    """Create a login challenge and e-mail it. Only the user id, the site origin and a local
    path are job arguments: the code and token never reach the jobs table."""
    services.send_login_email(user_id, link_base, next_path)


@app.periodic(cron="15 4 * * *")
@app.task(
    name="accounts.purge_expired", queue=QUEUE_DEFAULT, queueing_lock="accounts.purge_expired"
)
def purge_expired(timestamp: int) -> None:
    """Daily: drop old login challenges, throttle events and expired sessions."""
    services.purge_expired()
