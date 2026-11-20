"""Production: everything from `hosted`, plus the rules only a public instance has.

Hosting is not decided (D91): nothing here assumes a provider.
"""

from .env import scanner_from_env
from .hosted import *  # noqa: F403

# Uploads from the public must be malware-scanned: `none` refuses to load (US-2.3A).
# Without CLAMD_HOST / CLAMD_SOCKET every scan is an error, so no upload ever counts as ready.
MALWARE_SCANNER = scanner_from_env(("clamd",), default="clamd", module="config.settings.prod")
