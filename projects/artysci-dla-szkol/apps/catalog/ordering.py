"""The order of the public catalog (US-4.4, D16, D130). The same for everyone on a given day.

Key, highest first:

1. match: with `q` the text-search score of D129; without `q` every listed artist matches equally
   (filters are AND, D127), so the step does nothing;
2. verified (`listing.is_verified`, False for everybody until US-8.3);
3. profile completeness in buckets of 10 percentage points, stored in the read model when the row
   is written (`CatalogEntry.completeness_bucket`), so only published state counts;
4. a daily shuffle: SHA-256 of "<Warsaw date>:<artist id>". No stored randomness, no cookie, no
   per-visitor state; it changes at midnight Warsaw time and is stable across pages.

There is deliberately no field, flag or setting that lifts one artist (D16: no paid boosts).
"""

import hashlib
from datetime import date

from django.utils import timezone

BUCKET_SIZE = 10  # completeness percent rounded down to tens: 0, 10, ..., 100


def completeness_bucket(percent: int) -> int:
    return max(0, min(100, percent)) // BUCKET_SIZE * BUCKET_SIZE


def today() -> date:
    """The calendar day in Europe/Warsaw (TIME_ZONE); the seed of the shuffle."""
    return timezone.localdate()


def shuffle_key(artist_id: int, day: date) -> int:
    digest = hashlib.sha256(f"{day.isoformat()}:{artist_id}".encode()).digest()
    return int.from_bytes(digest[:8], "big")


def order_key(*, score: int, verified: bool, bucket: int, artist_id: int, day: date) -> tuple:
    """Sort key (ascending sort puts the best first)."""
    return (-score, not verified, -bucket, shuffle_key(artist_id, day), artist_id)
