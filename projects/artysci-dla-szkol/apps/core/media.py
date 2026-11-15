"""One storage API for user files, whatever the backend (filesystem now, S3-compatible later).

- `public_url(key)`: URL on the separate media origin (MEDIA_PUBLIC_BASE_URL).
- `signed_url(key, expires=...)`: short-lived URL for a private file. S3: a presigned URL
  straight from the bucket. Filesystem: a signed token served by `core:private-media`.
"""

import time

from django.conf import settings
from django.core import signing
from django.core.files.storage import storages
from django.urls import reverse

PRIVATE_SALT = "core.media.private"


class SignedURLInvalid(Exception):
    """The token is forged, malformed or expired."""


def private_storage():
    return storages["private"]


def public_storage():
    return storages["public"]


def is_s3() -> bool:
    return settings.STORAGE_BACKEND == "s3"


def public_url(key: str) -> str:
    return public_storage().url(key)


def signed_url(key: str, *, expires: int | None = None) -> str:
    """Short-lived URL for a private file; `expires` in seconds (default MEDIA_SIGNED_URL_TTL)."""
    ttl = settings.MEDIA_SIGNED_URL_TTL if expires is None else expires
    if is_s3():
        return private_storage().url(
            key,
            expire=ttl,
            parameters={"ResponseContentDisposition": "attachment"},
        )
    token = signing.dumps({"key": key, "exp": time.time() + ttl}, salt=PRIVATE_SALT, compress=True)
    return reverse("core:private-media", args=[token])


def resolve_token(token: str) -> str:
    """Return the storage key behind a filesystem signed token, or raise SignedURLInvalid."""
    try:
        payload = signing.loads(token, salt=PRIVATE_SALT)
        key, exp = payload["key"], float(payload["exp"])
    except (signing.BadSignature, KeyError, TypeError, ValueError) as exc:
        raise SignedURLInvalid from exc
    if time.time() >= exp:
        raise SignedURLInvalid("expired")
    return key
