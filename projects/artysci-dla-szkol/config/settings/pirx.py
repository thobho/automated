"""Dev instance on pirx (LAN, plain HTTP, no proxy, synthetic data only: D55, D57).

Prod with the TLS-only parts turned off: browsers drop `Secure` and `__Host-` cookies over plain
HTTP, so login would break. Never use this module on a public host. Everything else (required
env vars, storage, logging) is shared with prod through `hosted`.
"""

import os

# `hosted` requires SITE_URL. An instance installed before it existed has no such line in its
# pirx.env, so this module (one known LAN address) fills it in; pirx.env still wins.
os.environ.setdefault("SITE_URL", "http://192.168.68.62:8100")

from .env import env, scanner_from_env  # noqa: E402
from .hosted import *  # noqa: E402, F403

# pirx in light mode has no RAM for clamd (D87): uploads are unscanned and logged as such.
MALWARE_SCANNER = scanner_from_env(("clamd", "none"), default="none", module="config.settings.pirx")

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_NAME = "sessionid"
CSRF_COOKIE_NAME = "csrftoken"

SECURE_SSL_REDIRECT = False
SECURE_HSTS_SECONDS = 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = False

# No reverse proxy and no whitenoise here: the app serves collectstatic output itself (urls.py).
SERVE_STATIC = True

# Synthetic data only on pirx (D57): the quality lab (test set, US-11.2) is on here.
QUALITY_LAB_ENABLED = env.bool("QUALITY_LAB_ENABLED", default=True)
