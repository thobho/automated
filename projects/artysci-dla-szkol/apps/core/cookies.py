"""The one list of cookies this site may set (US-8.8, D32): session and CSRF, nothing else.

SECURITY.md "Cookies" documents them; `apps/core/tests/test_cookies.py` fails when any view
sets another one. Names come from settings, so prod's `__Host-` names are covered.
"""

from django.conf import settings


def essential_cookie_names() -> frozenset[str]:
    return frozenset({settings.SESSION_COOKIE_NAME, settings.CSRF_COOKIE_NAME})
