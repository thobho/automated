"""Settings shared by every environment. Nothing here needs a secret.

Environment-specific modules (dev, test, prod) set SECRET_KEY, DEBUG, ALLOWED_HOSTS and
DATABASES, reading them from environment variables.
"""

from pathlib import Path

from .env import env
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
    "django.middleware.security.SecurityMiddleware",
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

# Logging: console only (the worker and web log to stdout/stderr; the host collects them) ---

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"plain": {"format": "%(asctime)s %(levelname)s %(name)s %(message)s"}},
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "plain"}},
    "loggers": {
        "procrastinate": {"handlers": ["console"], "level": "INFO"},
        "apps": {"handlers": ["console"], "level": "INFO"},
    },
}

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
MEDIA_PRIVATE_ROOT = env.path("MEDIA_PRIVATE_ROOT", default=BASE_DIR / "media" / "private")
MEDIA_PUBLIC_ROOT = env.path("MEDIA_PUBLIC_ROOT", default=BASE_DIR / "media" / "public")
MEDIA_SIGNED_URL_TTL = env.int("MEDIA_SIGNED_URL_TTL", default=300)  # seconds
STORAGES = build_storages(
    STORAGE_BACKEND,
    public_base_url=MEDIA_PUBLIC_BASE_URL,
    private_root=MEDIA_PRIVATE_ROOT,
    public_root=MEDIA_PUBLIC_ROOT,
    signed_url_ttl=MEDIA_SIGNED_URL_TTL,
)
