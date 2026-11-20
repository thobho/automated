"""Signal receivers: each one only calls a service (connected in `apps.py`)."""

from apps.accounts.signals import email_confirmed


def verify_on_confirmation(sender, user, **kwargs) -> None:
    from . import services

    services.check_domain_for_user(user)


def connect() -> None:
    email_confirmed.connect(verify_on_confirmation, dispatch_uid="institutions.verify_by_domain")
