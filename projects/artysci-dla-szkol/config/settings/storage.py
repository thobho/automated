"""Media storage settings (D58, D62).

Two storages behind one interface:
- "private": originals and documents; reachable only through short-lived signed URLs.
- "public": processed images/video; served from a SEPARATE origin (MEDIA_PUBLIC_BASE_URL), so
  user content never runs on the app origin.

STORAGE_BACKEND=filesystem (lean pirx, default) or s3 (MinIO locally/CI, any S3 service later).
"""

from pathlib import Path
from urllib.parse import urlsplit

from django.core.exceptions import ImproperlyConfigured

from .env import env


def build_storages(
    backend: str,
    *,
    public_base_url: str,
    private_root: str | Path,
    public_root: str | Path,
    signed_url_ttl: int = 300,
) -> dict:
    """Return the STORAGES setting for `backend` ("filesystem" or "s3")."""
    base = {
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    }
    if backend == "filesystem":
        private = {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
            "OPTIONS": {"location": str(private_root)},
        }
        return {
            **base,
            "default": private,
            "private": private,
            "public": {
                "BACKEND": "django.core.files.storage.FileSystemStorage",
                "OPTIONS": {
                    "location": str(public_root),
                    "base_url": public_base_url.rstrip("/") + "/",
                },
            },
        }
    if backend == "s3":
        common = {
            "endpoint_url": env.str("S3_ENDPOINT_URL", default="") or None,
            "access_key": env.str("S3_ACCESS_KEY_ID", default=""),
            "secret_key": env.str("S3_SECRET_ACCESS_KEY", default=""),
            "region_name": env.str("S3_REGION", default="us-east-1"),
            "signature_version": "s3v4",
            "addressing_style": env.str("S3_ADDRESSING_STYLE", default="path"),
            "file_overwrite": False,
            "default_acl": None,
        }
        parts = urlsplit(public_base_url)
        private = {
            "BACKEND": "storages.backends.s3.S3Storage",
            "OPTIONS": {
                **common,
                "bucket_name": env.str("S3_PRIVATE_BUCKET", default="private"),
                "querystring_auth": True,
                "querystring_expire": signed_url_ttl,
            },
        }
        return {
            **base,
            "default": private,
            "private": private,
            "public": {
                "BACKEND": "storages.backends.s3.S3Storage",
                "OPTIONS": {
                    **common,
                    "bucket_name": env.str("S3_PUBLIC_BUCKET", default="public"),
                    "querystring_auth": False,
                    # MEDIA_PUBLIC_BASE_URL is the public bucket's origin (path included).
                    "custom_domain": parts.netloc + parts.path.rstrip("/"),
                    "url_protocol": (parts.scheme or "https") + ":",
                },
            },
        }
    raise ImproperlyConfigured(f"STORAGE_BACKEND must be 'filesystem' or 's3', got {backend!r}.")
