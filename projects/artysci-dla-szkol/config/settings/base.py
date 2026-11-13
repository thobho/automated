"""Settings shared by every environment. Nothing here needs a secret.

Environment-specific modules (dev, test, prod) set SECRET_KEY, DEBUG, ALLOWED_HOSTS and
DATABASES, reading them from environment variables.
"""

from pathlib import Path

from .env import env

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
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
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

# Login throttling scaffold (apps/accounts/throttling.py), wired into login by E1.
LOGIN_THROTTLE_LIMIT = env.int("LOGIN_THROTTLE_LIMIT", default=5)
LOGIN_THROTTLE_WINDOW = env.int("LOGIN_THROTTLE_WINDOW", default=900)  # seconds
LOGIN_THROTTLE_CACHE = "default"

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
