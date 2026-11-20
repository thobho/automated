"""Signals other apps may listen to, so `accounts` never imports them.

`email_confirmed(sender=User, user=user)`: sent once, the first time a user proves access to
their mailbox (`services.confirm_email()`). Receivers only call their own app's service.
"""

from django.dispatch import Signal

email_confirmed = Signal()
