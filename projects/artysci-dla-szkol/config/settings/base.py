"""Settings shared by every environment. Nothing here needs a secret.

Environment-specific modules (dev, test, prod) set SECRET_KEY, DEBUG, ALLOWED_HOSTS and
DATABASES, reading them from environment variables.
"""

from pathlib import Path

from .env import env, scanner_from_env
from .storage import build_storages

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Apps -----------------------------------------------------------------------------------

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "procrastinate.contrib.django",  # job queue on PostgreSQL; read-only jobs admin
]

# One app per concern. accounts owns AUTH_USER_MODEL.
LOCAL_APPS = [
    "apps.accounts",
    "apps.core",
    "apps.artists",
    "apps.institutions",
    "apps.profiles",
    "apps.catalog",
    "apps.inquiries",
    "apps.notices",
    "apps.notifications",
    "apps.trust",
    "apps.adminpanel",
    "apps.analytics",
    "apps.quality",
]

INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS

AUTH_USER_MODEL = "accounts.User"

MIDDLEWARE = [
    "apps.core.logs.RequestIdMiddleware",  # first: every response gets a request id + access log
    "django.middleware.security.SecurityMiddleware",
    "apps.core.security.SecurityHeadersMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "apps.trust.middleware.LegalAcceptanceMiddleware",  # re-acceptance gate (US-8.1)
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "apps.analytics.middleware.VisitMiddleware",  # cookie-free page-view counts
]

ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.template.context_processors.i18n",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.core.security.csp_nonce",
            ],
        },
    },
]

# Per-environment modules build DATABASES; this is applied to all of them.
DATABASE_CONN_MAX_AGE = env.int("DATABASE_CONN_MAX_AGE", default=60)

# SMTP target used when the SMTP backend is selected (Mailpit locally); prod sets the backend.
EMAIL_HOST = env.str("EMAIL_HOST", default="localhost")
EMAIL_PORT = env.int("EMAIL_PORT", default=25)

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Auth -----------------------------------------------------------------------------------

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# E-mail login (US-1.3, D1): no passwords; a link + 6-digit code, single use.
LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"
LOGIN_CHALLENGE_TTL = env.int("LOGIN_CHALLENGE_TTL", default=900)  # seconds
DEFAULT_FROM_EMAIL = env.str("DEFAULT_FROM_EMAIL", default="Artyści dla szkół <no-reply@localhost>")

# Limits (apps/accounts/throttling.py), counted in PostgreSQL so all workers share them (D96).
LOGIN_THROTTLE_LIMIT = env.int("LOGIN_THROTTLE_LIMIT", default=5)  # failed codes per e-mail
LOGIN_THROTTLE_WINDOW = env.int("LOGIN_THROTTLE_WINDOW", default=900)  # seconds (lock time)
LOGIN_EMAIL_LIMIT_PER_ADDRESS = env.int("LOGIN_EMAIL_LIMIT_PER_ADDRESS", default=5)
LOGIN_EMAIL_LIMIT_PER_IP = env.int("LOGIN_EMAIL_LIMIT_PER_IP", default=20)
LOGIN_EMAIL_WINDOW = env.int("LOGIN_EMAIL_WINDOW", default=3600)  # seconds
# E-mail change requests per user (US-1.6) within LOGIN_EMAIL_WINDOW; the per-IP limit is shared.
EMAIL_CHANGE_LIMIT_PER_USER = env.int("EMAIL_CHANGE_LIMIT_PER_USER", default=5)

# Sessions in the database (django.contrib.sessions default), 30 days of inactivity: every
# request re-saves the session, which moves its expiry 30 days ahead.
SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_AGE = env.int("SESSION_COOKIE_AGE", default=30 * 24 * 3600)
SESSION_SAVE_EVERY_REQUEST = True

# Security headers (SECURITY.md) ----------------------------------------------------------
# HSTS, SSL redirect and Secure cookies are prod-only (prod.py).

SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
SECURE_CROSS_ORIGIN_OPENER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"  # legacy twin of frame-ancestors 'none'

# Strict CSP: no inline script or style, no eval; "{nonce}" adds the per-request nonce
# (`{{ csp_nonce }}` in templates). User files will come from a separate origin (D62, T06):
# add that origin to img-src/media-src then.
CSP_DIRECTIVES = {
    "default-src": ["'self'"],
    "script-src": ["'self'", "{nonce}"],
    "style-src": ["'self'"],
    "img-src": ["'self'", "data:"],
    "font-src": ["'self'"],
    "connect-src": ["'self'"],
    "object-src": ["'none'"],
    "base-uri": ["'none'"],
    "form-action": ["'self'"],
    "frame-ancestors": ["'none'"],
}
# Browser features nobody on this site needs; each is sent as `feature=()`.
PERMISSIONS_POLICY = [
    "camera",
    "microphone",
    "geolocation",
    "payment",
    "usb",
    "accelerometer",
    "gyroscope",
    "magnetometer",
    "browsing-topics",
]

# Cookies: HttpOnly + SameSite=Lax everywhere; Secure and __Host- names in prod.
# The CSRF token reaches HTMX through the template (hx-headers), so its cookie is HttpOnly too.
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_HEADER_NAME = "HTTP_X_CSRFTOKEN"  # HTMX sends X-CSRFToken (templates/base.html)
# Only essential cookies (D32, apps/core/cookies.py): flash messages live in the session, not in
# a `messages` cookie. There is no language cookie either (Polish only: no set_language view).
MESSAGE_STORAGE = "django.contrib.messages.storage.session.SessionStorage"

# Logging: one JSON line per event on stdout, same config everywhere (apps/core/logs.py) ----
# The host collects stdout. django.server (runserver) is muted: its lines carry query strings;
# the access logger (RequestIdMiddleware) replaces it.

LOG_LEVEL = env.str("LOG_LEVEL", default="INFO")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"request_context": {"()": "apps.core.logs.RequestContextFilter"}},
    "formatters": {"json": {"()": "apps.core.logs.JsonFormatter"}},
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "json",
            "filters": ["request_context"],
        },
        "null": {"class": "logging.NullHandler"},
    },
    "root": {"handlers": ["console"], "level": LOG_LEVEL},
    "loggers": {
        "django": {"handlers": ["console"], "level": LOG_LEVEL, "propagate": False},
        "django.server": {"handlers": ["null"], "propagate": False},
    },
}

# AI adapter (apps/profiles/ai, T07: D46, D59, D60, D63) ----------------------------------
# "fake" is deterministic and offline (tests, CI, local); prod defaults to "openrouter".
AI_CLIENT = env.str("AI_CLIENT", default="fake")
OPENROUTER_API_KEY = env.str("OPENROUTER_API_KEY", default="")  # env only, never logged
AI_KILL_SWITCH = env.bool("AI_KILL_SWITCH", default=False)
AI_DAILY_CAP_USD = env.str("AI_DAILY_CAP_USD", default="1.00")
AI_PER_CALL_CAP_USD = env.str("AI_PER_CALL_CAP_USD", default="0.05")
# Pinned model and the only providers OpenRouter may route to (all with ZDR endpoints).
AI_MODEL = env.str("AI_MODEL", default="anthropic/claude-haiku-5.5")
AI_PROVIDERS = env.list("AI_PROVIDERS", default=["google-vertex", "amazon-bedrock"])
# Price ceiling of the pinned model, USD per million tokens (cost estimate + max_price).
AI_PRICE_PROMPT_USD_PER_MTOK = env.str("AI_PRICE_PROMPT_USD_PER_MTOK", default="0.11")
AI_PRICE_COMPLETION_USD_PER_MTOK = env.str("AI_PRICE_COMPLETION_USD_PER_MTOK", default="0.55")
AI_MAX_TOKENS = env.int("AI_MAX_TOKENS", default=2048)
AI_TIMEOUT_SECONDS = env.float("AI_TIMEOUT_SECONDS", default=60.0)
# Names removed from every prompt (D59), e.g. staff or test persons; comma-separated.
AI_SCRUB_NAMES = env.list("AI_SCRUB_NAMES", default=[])

# Locale: Polish only, Warsaw time --------------------------------------------------------

LANGUAGE_CODE = "pl"
LANGUAGES = [("pl", "Polski")]
TIME_ZONE = "Europe/Warsaw"
USE_I18N = True
USE_TZ = True
LOCALE_PATHS = [BASE_DIR / "locale"]

# Static files (HTMX is vendored under static/vendor, never loaded from a CDN: D11) ---------

STATIC_URL = env.str("DJANGO_STATIC_URL", default="/static/")
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = env.path("DJANGO_STATIC_ROOT", default=BASE_DIR / "staticfiles")

# Media (see storage.py): private = signed URLs only; public = separate origin ---------------

STORAGE_BACKEND = env.str("STORAGE_BACKEND", default="filesystem")
MEDIA_PUBLIC_BASE_URL = env.str("MEDIA_PUBLIC_BASE_URL", default="http://localhost:8101/")
MEDIA_PRIVATE_ROOT = Path(env.str("MEDIA_PRIVATE_ROOT", default=str(BASE_DIR / "media/private")))
MEDIA_PUBLIC_ROOT = Path(env.str("MEDIA_PUBLIC_ROOT", default=str(BASE_DIR / "media/public")))
MEDIA_SIGNED_URL_TTL = env.int("MEDIA_SIGNED_URL_TTL", default=300)  # seconds
STORAGES = build_storages(
    STORAGE_BACKEND,
    public_base_url=MEDIA_PUBLIC_BASE_URL,
    private_root=MEDIA_PRIVATE_ROOT,
    public_root=MEDIA_PUBLIC_ROOT,
    signed_url_ttl=MEDIA_SIGNED_URL_TTL,
)

# Malware scanning of uploads (apps/core/scanning.py, US-2.3A) -------------------------------
# clamd = ClamAV daemon (prod accepts only this); none = unscanned, logged (dev, pirx: D87).
MALWARE_SCANNER = scanner_from_env(("clamd", "none"), default="none", module="config.settings")
CLAMD_HOST = env.str("CLAMD_HOST", default="")
CLAMD_PORT = env.int("CLAMD_PORT", default=3310)
CLAMD_SOCKET = env.str("CLAMD_SOCKET", default="")  # Unix socket path; wins over host/port
CLAMD_TIMEOUT = env.float("CLAMD_TIMEOUT", default=30.0)  # seconds

# Artist materials (US-2.3A, D8): per-artist counts; size limits are in apps/core/uploads.py.
MATERIAL_MAX_PHOTOS = 40
MATERIAL_MAX_PDFS = 10
# PDF text extraction limits (the job stops at the first one reached).
PDF_TEXT_MAX_PAGES = env.int("PDF_TEXT_MAX_PAGES", default=100)
PDF_TEXT_MAX_CHARS = env.int("PDF_TEXT_MAX_CHARS", default=100_000)
PDF_TEXT_MAX_SECONDS = env.float("PDF_TEXT_MAX_SECONDS", default=30.0)
# YouTube / Vimeo oEmbed lookups (fixed public endpoints only)
OEMBED_TIMEOUT_SECONDS = env.float("OEMBED_TIMEOUT_SECONDS", default=5.0)

# Import from the artist's own website (US-2.2, apps/core/safefetch.py) ----------------------
WEBSITE_IMPORT_MAX_PAGES = env.int("WEBSITE_IMPORT_MAX_PAGES", default=10)
WEBSITE_IMPORT_MAX_BYTES = env.int("WEBSITE_IMPORT_MAX_BYTES", default=20 * 1024 * 1024)
WEBSITE_IMPORT_PAGE_TIMEOUT = env.float("WEBSITE_IMPORT_PAGE_TIMEOUT", default=30.0)  # seconds
WEBSITE_IMPORT_MAX_REDIRECTS = env.int("WEBSITE_IMPORT_MAX_REDIRECTS", default=3)
WEBSITE_IMPORT_MAX_TEXT_CHARS = env.int("WEBSITE_IMPORT_MAX_TEXT_CHARS", default=200_000)
# Test only: lets the fetcher reach loopback addresses on any port, so a synthetic site served
# locally can be imported in dev. Hosted settings (prod, pirx) refuse to start with it on.
SAFE_FETCH_ALLOW_LOOPBACK = env.bool("SAFE_FETCH_ALLOW_LOOPBACK", default=False)
