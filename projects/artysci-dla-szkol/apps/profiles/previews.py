"""Private preview links (US-3.7).

    link, token = create_link(artist)      # the token exists only in this return value
    revoke_link(artist, link_id)           # stops working at once
    artist = artist_for_token(token)       # None for unknown, expired, revoked or malformed tokens
    result = open_preview(token, ip)       # the rate-limited lookup + the read-only page
    active_links(artist)                   # status and expiry for the panel (never the token)
    purge()                                # periodic: expired/revoked links older than 30 days

What a link shows: the artist's current version (works before the D6 minimum), like the owner's
preview but read-only, with the rules of the public page for third parties: photos and videos only
with a current rights statement (D4, D7), and no e-mail or phone anywhere (D9: found ones are
replaced by "[ukryte]").

Rate limit: wrong tokens count per client IP (`accounts.throttling`, scope `preview_ip`); at the
limit every request from that IP gets 429 until the window passes. The limit is logged with an
event name only, never the token or the path.

Token: 32 random bytes from `secrets` (256 bits), URL-safe base64 (43 characters). Stored only as
SHA-256 (a random 256-bit value needs no slow hash). Lookup is by the hash through the unique
index, so no early-exit string comparison of the secret happens in Python; the equality check on
the hash is still done with `hmac.compare_digest`. Valid for 7 days. At most 3 active links.
A link works only while its artist is not withdrawn or deactivated.
"""

import enum
import hashlib
import hmac
import logging
import re
import secrets
from dataclasses import dataclass
from datetime import datetime, timedelta

from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.accounts import throttling
from apps.artists.models import Artist, PublicationStatus

from . import pages
from .contact import contacts_in
from .content import PageContent
from .inputs import materials_allowed
from .models import PreviewLink

logger = logging.getLogger(__name__)

VALIDITY = timedelta(days=7)
MAX_ACTIVE = 3
KEEP_AFTER_END = timedelta(days=30)
TOKEN_BYTES = 32
_TOKEN = re.compile(r"^[A-Za-z0-9_-]{43}$")  # urlsafe_b64 of 32 bytes, no padding


class PreviewRefused(Exception):
    def __init__(self, message):
        super().__init__(str(message))
        self.message = message


def hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def is_well_formed(token: str) -> bool:
    return bool(_TOKEN.fullmatch(token or ""))


def _active(queryset, now: datetime):
    return queryset.filter(revoked_at__isnull=True, expires_at__gt=now)


def active_links(artist: Artist, *, now: datetime | None = None) -> list[PreviewLink]:
    return list(_active(PreviewLink.objects.filter(artist=artist), now or timezone.now()))


def create_link(artist: Artist, *, now: datetime | None = None) -> tuple[PreviewLink, str]:
    """A new link; raises `PreviewRefused` with a Polish message at the limit."""
    now = now or timezone.now()
    with transaction.atomic():
        locked = Artist.objects.select_for_update().get(pk=artist.pk)  # one writer at a time
        if locked.publication_status == PublicationStatus.WITHDRAWN:
            raise PreviewRefused(_("Strona jest wycofana: link do podglądu by nie działał."))
        if _active(PreviewLink.objects.filter(artist=artist), now).count() >= MAX_ACTIVE:
            raise PreviewRefused(
                _("Masz już %(max)d aktywne linki do podglądu. Odwołaj jeden, aby utworzyć nowy.")
                % {"max": MAX_ACTIVE}
            )
        token = secrets.token_urlsafe(TOKEN_BYTES)
        link = PreviewLink.objects.create(
            artist=artist,
            token_hash=hash_token(token),
            created_at=now,
            expires_at=now + VALIDITY,
        )
    return link, token


def revoke_link(artist: Artist, link_id, *, now: datetime | None = None) -> bool:
    """Revoke one of the artist's own links; False when there is no such active link."""
    now = now or timezone.now()
    try:
        link_id = int(link_id)
    except (TypeError, ValueError):
        return False
    return bool(
        _active(PreviewLink.objects.filter(artist=artist, pk=link_id), now).update(revoked_at=now)
    )


def artist_for_token(token: str, *, now: datetime | None = None) -> Artist | None:
    """The artist whose preview the token opens; None in every other case (the caller must not be
    able to tell the cases apart)."""
    if not is_well_formed(token):
        return None
    now = now or timezone.now()
    digest = hash_token(token)
    link = (
        _active(PreviewLink.objects.filter(token_hash=digest), now)
        .select_related("artist__user")
        .first()
    )
    if link is None or not hmac.compare_digest(link.token_hash, digest):
        return None
    artist = link.artist
    if artist.publication_status == PublicationStatus.WITHDRAWN or not artist.user.is_active:
        return None
    return artist


# --- the page a link shows -----------------------------------------------------------------------

HIDDEN = "[ukryte]"


def without_contacts(text: str, also: str = "") -> str:
    """`text` with every e-mail and phone replaced by `HIDDEN`; when one cannot be cut out
    cleanly, the whole text is hidden (D9 wins over completeness)."""
    found = contacts_in(text, also) if text else []
    if not found:
        return text
    for hit in found:
        if "@" in hit:
            text = re.sub(re.escape(hit), HIDDEN, text, flags=re.IGNORECASE)
        else:
            digits = re.sub(r"\D", "", hit)
            text = re.sub(r"\+?" + r"\D{0,3}".join(digits), HIDDEN, text)
    return HIDDEN if contacts_in(text, also) else text


def preview_page(artist: Artist) -> PageContent:
    """The read-only page of a preview link (see the module docstring)."""
    page = pages.page_content(artist)
    if not materials_allowed(artist):
        page.photos, page.videos = [], []
    email = artist.user.email

    def clean(text):
        return without_contacts(text, email)

    page.hero.name, page.hero.city = clean(page.hero.name), clean(page.hero.city)
    page.hero.tagline = clean(page.hero.tagline)
    page.facts = [clean(text) for text in page.facts]
    page.about, page.for_schools = clean(page.about), clean(page.for_schools)
    for offer in page.offers:
        offer.title, offer.description = clean(offer.title), clean(offer.description)
    for item in page.faq:
        item.question, item.answer = clean(item.question), clean(item.answer)
    for photo in page.photos:
        photo.alt = clean(photo.alt)
    return page


class Outcome(enum.Enum):
    SHOWN = "shown"
    NOT_FOUND = "not_found"
    LIMITED = "limited"


@dataclass(frozen=True)
class Opened:
    outcome: Outcome
    page: PageContent | None = None


def open_preview(token: str, client_ip: str, *, now: datetime | None = None) -> Opened:
    """The public lookup behind `/podglad/<token>/`, rate limited per client IP."""
    now = now or timezone.now()
    ip_key = throttling.ip_identifier(client_ip)
    if throttling.exceeded(throttling.PREVIEW_PER_IP, ip_key, now=now):
        logger.warning("preview link rate limited", extra={"event": "preview_rate_limited"})
        return Opened(Outcome.LIMITED)
    artist = artist_for_token(token, now=now)
    if artist is None:
        throttling.hit(throttling.PREVIEW_PER_IP, ip_key, now=now)
        return Opened(Outcome.NOT_FOUND)
    return Opened(Outcome.SHOWN, preview_page(artist))


def purge(*, now: datetime | None = None) -> int:
    """Delete links that expired or were revoked more than 30 days ago."""
    limit = (now or timezone.now()) - KEEP_AFTER_END
    deleted, _by_model = PreviewLink.objects.filter(
        Q(expires_at__lte=limit) | Q(revoked_at__lte=limit)
    ).delete()
    return deleted
