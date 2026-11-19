"""Import from the artist's own website (US-2.2, D4, D8, D9, D59, D104, D105).

`start_import()` (web request) records the rights confirmation (`material_rights` statement
through the trust service, reused when one counts) and queues `run_import()` as a job on the
``media`` queue. The job fetches pages only through `apps.core.safefetch` (public addresses
only, pinned connections, re-checked redirects) within the limits:

- at most `WEBSITE_IMPORT_MAX_PAGES` pages of the site's host (``www.`` ignored), found
  through links on fetched pages; links to other hosts are never requested;
- `WEBSITE_IMPORT_PAGE_TIMEOUT` seconds per request, `WEBSITE_IMPORT_MAX_BYTES` in total
  (pages and photos together);
- only HTML is parsed (stdlib `html.parser`); JavaScript is never run.

From the pages it keeps the visible text (scripts, styles, navigation dropped), scrubbed
(e-mails, phones, accounts, PESEL, ID card numbers, postal addresses) before it is stored;
photos through the normal upload path (`materials.add_file`: sniffed type, EXIF stripped,
private storage, malware scan, 40-photo limit) marked as imported; YouTube and Vimeo links
through the oEmbed check (`materials.add_link`); general contact data stored separately on
the import for the artist only (never published, never sent to AI).

Logs carry the import id, a pseudonymised user, counts and error codes: never the URL.
"""

import io
import logging
import re
import time
import urllib.parse
from dataclasses import dataclass, field
from datetime import timedelta
from html.parser import HTMLParser

from django.conf import settings
from django.db import transaction
from django.utils import timezone
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _

from apps.analytics import services as analytics
from apps.core import jobs, safefetch, uploads
from apps.core.logs import pseudonymise_user
from apps.core.safefetch import FetchError
from apps.profiles.ai import scrub as scrubber
from apps.trust import services as trust

from . import materials
from .models import Artist, ImportStatus, Material, MaterialKind, WebsiteImport

logger = logging.getLogger("apps.artists.website_import")

ACTIVE = (ImportStatus.QUEUED, ImportStatus.RUNNING)
STALE_AFTER = timedelta(hours=1)  # an import "trwa" this long was lost by a crashed worker
MAX_PER_DAY = 10  # imports an artist may start per day
MAX_IMAGES = 60  # image URLs considered per import (the photo limit applies on top)
MAX_VIDEOS = 20
MAX_CONTACTS = 10
MAX_JOB_SECONDS = 600  # the whole job: pages and photos
PHOTO_MAX_BYTES = uploads.KINDS["photo"][0]
HTML_TYPES = ("text/html", "application/xhtml+xml")
SKIPPED_EXTENSIONS = (
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".ico", ".bmp", ".pdf", ".zip", ".rar",
    ".mp3", ".mp4", ".mov", ".avi", ".doc", ".docx", ".xls", ".xlsx", ".css", ".js", ".xml",
)  # fmt: skip
IMAGE_SKIPPED_EXTENSIONS = (".svg", ".gif", ".ico", ".bmp")
ADDRESS = "[address]"
# Polish postal code with the place name after it, and the street part before it if any.
_ADDRESS = re.compile(
    r"(?:(?:ul\.|al\.|os\.|pl\.)\s*[^\n,;]{1,60}?\s*\d+[A-Za-z]?(?:/\d+)?[,\s]+)?"
    r"(?<!\d)\d{2}-\d{3}(?!\d)\s+[A-ZĄĆĘŁŃÓŚŹŻ][\wąćęłńóśźżĄĆĘŁŃÓŚŹŻ-]+"
    r"(?:\s+[A-ZĄĆĘŁŃÓŚŹŻ][\wąćęłńóśźżĄĆĘŁŃÓŚŹŻ-]+)?"
)

NOT_AVAILABLE = _("Oświadczenie o prawach do materiałów nie jest jeszcze dostępne.")
ALREADY_RUNNING = _("Import Twojej strony już trwa. Poczekaj na wynik.")
TOO_MANY = _("Dziś uruchomiono już %(n)d importów. Spróbuj jutro albo uzupełnij dane ręcznie.")
NO_TEXT = _(
    "Na stronie nie znaleźliśmy tekstu do odczytania. Strona może wymagać JavaScriptu, którego "
    "nie uruchamiamy. Uzupełnij dane ręcznie."
)
UNEXPECTED = _("Import nie powiódł się z powodu błędu po naszej stronie. Spróbuj później.")


class ImportRefused(Exception):
    """The import cannot start. `message` is Polish, for the form."""

    def __init__(self, code: str, message):
        super().__init__(code)
        self.code = code
        self.message = message


def _log(event: str, record: WebsiteImport, *, level=logging.INFO, **extra) -> None:
    logger.log(
        level,
        event.replace("_", " "),
        extra={
            "event": event,
            "user": pseudonymise_user(record.artist.user_id),
            "website_import": record.pk,
            **extra,
        },
    )


# --- queries -----------------------------------------------------------------------------------


def imports_for(artist: Artist):
    return WebsiteImport.objects.filter(artist=artist).order_by("-created_at", "-pk")


def get_import(artist: Artist, import_id) -> WebsiteImport:
    """The artist's own import; `WebsiteImport.DoesNotExist` for another artist's id."""
    return WebsiteImport.objects.get(artist=artist, pk=import_id)


def latest_import(artist: Artist | None) -> WebsiteImport | None:
    return imports_for(artist).first() if artist is not None else None


def has_finished_import(artist: Artist | None) -> bool:
    if artist is None:
        return False
    return imports_for(artist).filter(status__in=(ImportStatus.DONE, ImportStatus.PARTIAL)).exists()


def import_text(artist: Artist | None) -> str:
    """Scrubbed text of the newest import that has text (source material for US-2.5a)."""
    if artist is None:
        return ""
    record = imports_for(artist).exclude(text="").first()
    return record.text if record else ""


def _active(artist: Artist):
    return imports_for(artist).filter(
        status__in=ACTIVE, created_at__gte=timezone.now() - STALE_AFTER
    )


# --- start (web request) -----------------------------------------------------------------------


def _rights_statement(artist: Artist):
    """The counting `material_rights` statement, made now if there is none (D104)."""
    kind = trust.Kind.MATERIAL_RIGHTS
    for statement in trust.current_statements(artist):
        if statement.kind == kind:
            return statement
    try:
        return trust.make_statement(artist, kind)
    except trust.NoPublishedVersion as exc:
        raise ImportRefused("statement_unavailable", NOT_AVAILABLE) from exc


def start_import(artist: Artist, url: str, *, rights_confirmed: bool) -> WebsiteImport:
    """Record the rights confirmation and queue an import of `url`.

    Raises `ImportRefused` (no confirmation, statement wording missing, an import already
    running, daily limit). A URL the fetcher refuses without network access (scheme, user-info,
    port, a non-public IP literal) gives a ``nieudany`` import at once and queues nothing.
    """
    if not rights_confirmed:
        raise ImportRefused(
            "no_rights", _("Zaznacz, że strona jest Twoja i masz prawa do jej treści i zdjęć.")
        )
    url = (url or "").strip()
    with transaction.atomic():
        Artist.objects.select_for_update().filter(pk=artist.pk).first()
        if _active(artist).exists():
            raise ImportRefused("running", ALREADY_RUNNING)
        today = imports_for(artist).filter(created_at__gte=timezone.now() - timedelta(days=1))
        if today.count() >= MAX_PER_DAY:
            raise ImportRefused("limit", TOO_MANY % {"n": MAX_PER_DAY})
        statement = _rights_statement(artist)
        record = WebsiteImport.objects.create(
            artist=artist,
            url=url[:2000],
            rights_confirmed_at=timezone.now(),
            rights_statement=statement,
        )
        analytics.track("website_import_started", actor=artist.user, obj=record)
        refusal = _offline_refusal(url)
        if refusal is None:
            from . import tasks  # tasks import this module

            jobs.enqueue(
                tasks.run_website_import,
                idempotency_key=f"artists.run_website_import:{record.pk}",
                import_id=record.pk,
            )
    if refusal is not None:
        record.started_at = record.created_at
        _finish(record, ImportStatus.FAILED, str(refusal.message), code=refusal.code)
        return record
    _log("website_import_queued", record)
    return record


def _offline_refusal(url: str) -> FetchError | None:
    """What the fetcher refuses without DNS or a connection: the import fails at once."""
    try:
        safefetch.check_offline(url)
    except FetchError as exc:
        return exc
    return None  # a host name is resolved and checked in the job


# --- HTML parsing ------------------------------------------------------------------------------

DROPPED_TAGS = {
    "script", "style", "noscript", "template", "svg", "nav", "iframe", "object", "canvas",
    "head", "select", "button", "form",
}  # fmt: skip
VOID_TAGS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source",
    "track", "wbr",
}  # fmt: skip
BLOCK_TAGS = {
    "p", "div", "section", "article", "main", "header", "footer", "aside", "li", "ul", "ol",
    "h1", "h2", "h3", "h4", "h5", "h6", "table", "tr", "td", "th", "br", "blockquote", "dd",
    "dt", "figcaption", "address", "pre", "hr",
}  # fmt: skip


@dataclass
class Page:
    title: str = ""
    text: str = ""
    links: list[str] = field(default_factory=list)
    images: list[str] = field(default_factory=list)
    videos: list[str] = field(default_factory=list)
    emails: list[str] = field(default_factory=list)
    phones: list[str] = field(default_factory=list)


class _PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.page = Page()
        self._skip_depth = 0
        self._stack: list[str] = []
        self._in_title = False
        self._title: list[str] = []
        self._chunks: list[str] = []

    def handle_starttag(self, tag, attrs):
        attrs = {k: (v or "") for k, v in attrs}
        if tag == "title":
            self._in_title = True
        if tag == "a" and attrs.get("href"):
            href = attrs["href"].strip()
            lower = href.lower()
            if lower.startswith("mailto:"):
                self.page.emails.append(urllib.parse.unquote(href[7:].split("?", 1)[0]))
            elif lower.startswith("tel:"):
                self.page.phones.append(urllib.parse.unquote(href[4:]))
            else:
                self.page.links.append(href)
        if tag == "img":
            src = attrs.get("src") or attrs.get("data-src") or ""
            if not src and attrs.get("srcset"):
                src = attrs["srcset"].split(",")[0].strip().split(" ")[0]
            if src:
                self.page.images.append(src.strip())
        if tag in ("iframe", "embed") and attrs.get("src"):
            self.page.videos.append(attrs["src"].strip())
        role = attrs.get("role", "").lower()
        if tag in VOID_TAGS:
            if tag in BLOCK_TAGS and not self._skip_depth:
                self._chunks.append("\n")
            return
        self._stack.append(tag)
        if self._skip_depth or tag in DROPPED_TAGS or role in ("navigation", "menu"):
            self._skip_depth += 1
        elif tag in BLOCK_TAGS:
            self._chunks.append("\n")

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        if tag in VOID_TAGS or tag not in self._stack:
            return
        while self._stack:  # close unclosed children too (tolerant like browsers)
            open_tag = self._stack.pop()
            if self._skip_depth:
                self._skip_depth -= 1
            if open_tag == tag:
                break
        if tag in BLOCK_TAGS and not self._skip_depth:
            self._chunks.append("\n")

    def handle_data(self, data):
        if self._in_title:
            self._title.append(data)
            return
        if not self._skip_depth:
            self._chunks.append(data)

    def result(self) -> Page:
        self.page.title = " ".join("".join(self._title).split())[:200]
        lines = (" ".join(line.split()) for line in "".join(self._chunks).split("\n"))
        self.page.text = "\n".join(line for line in lines if line)
        return self.page


def parse_page(html: str) -> Page:
    """Visible text, title, links, images, embedded videos and mailto/tel contacts."""
    parser = _PageParser()
    try:
        parser.feed(html)
        parser.close()
    except (AssertionError, ValueError):  # broken markup: keep what was parsed so far
        pass
    return parser.result()


def decode(body: bytes, charset: str) -> str:
    for candidate in (charset, "utf-8"):
        if candidate:
            try:
                return body.decode(candidate)
            except (LookupError, UnicodeDecodeError):
                continue
    head = body[:2048].decode("ascii", "ignore")
    match = re.search(r"charset=[\"']?([A-Za-z0-9_-]+)", head)
    if match:
        try:
            return body.decode(match.group(1), "replace")
        except LookupError:
            pass
    return body.decode("utf-8", "replace")


# --- scrubbing and contacts --------------------------------------------------------------------


def addresses_in(text: str) -> list[str]:
    return list(dict.fromkeys(" ".join(m.group(0).split()) for m in _ADDRESS.finditer(text)))


def scrub_text(text: str) -> str:
    """What is stored and may later go to AI: no contact data, accounts, PESEL, ID cards."""
    return _ADDRESS.sub(ADDRESS, scrubber.scrub(text))


def collect_contacts(pages: list[Page]) -> dict:
    text = "\n".join(page.text for page in pages)
    emails = [e for page in pages for e in page.emails] + scrubber.emails_in(text)
    phones = [p for page in pages for p in page.phones] + scrubber.phones_in(text)

    def unique(values):
        cleaned = (" ".join(str(v).split())[:200] for v in values)
        return list(dict.fromkeys(v for v in cleaned if v))[:MAX_CONTACTS]

    return {
        "emails": unique(e.lower() for e in emails if "@" in e),
        "phones": unique(phones),
        "addresses": unique(addresses_in(text)),
    }


# --- URLs --------------------------------------------------------------------------------------


def _host(url: str) -> str:
    try:
        return (urllib.parse.urlsplit(url).hostname or "").lower()
    except ValueError:
        return ""


def same_site(url: str, site_host: str) -> bool:
    def bare(name: str) -> str:
        return name[4:] if name.startswith("www.") else name

    return bool(site_host) and bare(_host(url)) == bare(site_host)


def absolute(base: str, href: str) -> str:
    """`href` resolved against `base`, without the fragment; "" for non-http(s) links."""
    try:
        url = urllib.parse.urljoin(base, href.strip())
        parts = urllib.parse.urlsplit(url)
    except ValueError:
        return ""
    if parts.scheme not in ("http", "https") or not parts.hostname:
        return ""
    return urllib.parse.urlunsplit(parts._replace(fragment=""))


def _page_key(url: str) -> str:
    parts = urllib.parse.urlsplit(url)
    host = (parts.hostname or "").lower().removeprefix("www.")
    return f"{host}{parts.path.rstrip('/') or '/'}?{parts.query}"


_EMBEDS = (
    (re.compile(r"^https?://(?:www\.)?youtube(?:-nocookie)?\.com/embed/([A-Za-z0-9_-]{11})"),
     "https://www.youtube.com/watch?v={}"),
    (re.compile(r"^https?://player\.vimeo\.com/video/([0-9]{1,12})"), "https://vimeo.com/{}"),
)  # fmt: skip


def video_url(url: str) -> str:
    """A YouTube/Vimeo watch URL for a link or an embed; "" for anything else."""
    for pattern, template in _EMBEDS:
        match = pattern.match(url)
        if match:
            return template.format(match.group(1))
    ref = materials.parse_video_url(url)
    return ref.canonical_url if ref else ""


# --- the job -----------------------------------------------------------------------------------


@dataclass
class _Run:
    record: WebsiteImport
    started: float
    budget: int
    used: int = 0
    stopped: str = ""  # a limit that stopped fetching ("" = none)
    page_errors: int = 0
    pages: list[Page] = field(default_factory=list)
    skipped: list[dict] = field(default_factory=list)

    @property
    def remaining(self) -> int:
        return max(0, self.budget - self.used)

    def out_of_time(self) -> bool:
        return time.monotonic() - self.started > MAX_JOB_SECONDS

    def skip(self, what: str, why) -> None:
        if len(self.skipped) < 100:
            self.skipped.append({"what": what[:300], "why": str(why)})


def _limit_message() -> str:
    mb = settings.WEBSITE_IMPORT_MAX_BYTES // uploads.MB
    return gettext("Osiągnięto limit %(mb)d MB danych na import; dalsze pliki pominięto.") % {
        "mb": mb
    }


def _fetch(run: _Run, url: str, *, site_host: str, cap: int):
    return safefetch.fetch(
        url,
        max_bytes=max(1, min(cap, run.remaining)),
        timeout=settings.WEBSITE_IMPORT_PAGE_TIMEOUT,
        max_redirects=settings.WEBSITE_IMPORT_MAX_REDIRECTS,
        site_host=site_host,
    )


def _crawl(run: _Run, start_url: str) -> tuple[str, list[str], list[str]]:
    """Fetch pages; returns (failure message or "", image URLs, video URLs)."""
    max_pages = settings.WEBSITE_IMPORT_MAX_PAGES
    queue, seen = [start_url], {_page_key(start_url)}
    site_host = ""
    images: list[str] = []
    videos: list[str] = []
    while queue and len(run.pages) < max_pages:
        if run.out_of_time():
            run.stopped = gettext("Import trwał zbyt długo; pominięto dalsze podstrony.")
            break
        url = queue.pop(0)
        first = not run.pages and not site_host
        try:
            response = _fetch(run, url, site_host=site_host, cap=run.remaining)
        except FetchError as exc:
            _log("website_import_fetch_refused", run.record, code=exc.code)
            if first:
                return str(exc.message), [], []
            if exc.code == "too_large":  # the cap is what is left of the total
                run.stopped = _limit_message()
                break
            run.page_errors += 1
            run.skip(url, exc.message)
            continue
        run.used += len(response.body)
        if first:
            site_host = _host(response.url)
        seen.add(_page_key(response.url))
        if response.status != 200:
            message = gettext("Strona odpowiedziała błędem %(code)d.") % {"code": response.status}
            if first:
                return message, [], []
            run.page_errors += 1
            run.skip(url, message)
            continue
        if response.content_type not in HTML_TYPES:
            message = gettext("To nie jest strona HTML.")
            if first:
                return message, [], []
            run.skip(url, message)
            continue
        page = parse_page(decode(response.body, response.charset))
        run.pages.append(page)
        run.record.pages.append({"url": response.url[:500], "title": page.title})
        for href in page.links:
            link = absolute(response.url, href)
            if not link or not same_site(link, site_host):
                continue
            if urllib.parse.urlsplit(link).path.lower().endswith(SKIPPED_EXTENSIONS):
                continue
            key = _page_key(link)
            if key not in seen:
                seen.add(key)
                queue.append(link)
        for src in page.images:
            image = absolute(response.url, src)
            if image and image not in images:
                images.append(image)
        for candidate in page.videos + page.links:
            video = video_url(absolute(response.url, candidate))
            if video and video not in videos:
                videos.append(video)
    if queue and len(run.pages) >= max_pages:
        run.skip(
            gettext("%(n)d kolejnych podstron") % {"n": len(queue)},
            gettext("Pobieramy najwyżej %(n)d podstron.") % {"n": max_pages},
        )
    return "", images, videos


def _import_photos(run: _Run, images: list[str]) -> int:
    artist, added = run.record.artist, 0
    for url in images[:MAX_IMAGES]:
        name = materials.clean_name(urllib.parse.urlsplit(url).path) or "zdjecie"
        if urllib.parse.urlsplit(url).path.lower().endswith(IMAGE_SKIPPED_EXTENSIONS):
            run.skip(name, gettext("Ten format obrazu nie jest obsługiwany (tylko JPG, PNG, WebP)."))
            continue
        if materials.remaining(artist, MaterialKind.PHOTO) <= 0:
            run.skip(
                name,
                gettext("Osiągnięto limit %(n)d zdjęć.")
                % {"n": materials.limit_for(MaterialKind.PHOTO)},
            )
            continue
        if run.stopped or run.out_of_time():
            run.skip(name, run.stopped or gettext("Import trwał zbyt długo."))
            continue
        try:
            response = _fetch(run, url, site_host="", cap=PHOTO_MAX_BYTES)
        except FetchError as exc:
            reason = exc.message
            if exc.code == "too_large":
                if run.remaining < PHOTO_MAX_BYTES:
                    run.stopped = reason = _limit_message()
                else:
                    reason = gettext("Zdjęcie jest za duże (maksymalnie %(mb)d MB).") % {
                        "mb": PHOTO_MAX_BYTES // uploads.MB
                    }
            run.skip(name, reason)
            continue
        run.used += len(response.body)
        if response.status != 200:
            run.skip(name, gettext("Nie udało się pobrać zdjęcia."))
            continue
        file = io.BytesIO(response.body)
        file.name = name
        try:
            materials.add_file(artist, MaterialKind.PHOTO, file, source_import=run.record)
        except (uploads.UploadRejected, materials.MaterialRejected) as exc:
            run.skip(name, exc.message)
            continue
        added += 1
    for url in images[MAX_IMAGES:]:
        run.skip(materials.clean_name(url), gettext("Za dużo obrazów na stronie."))
    return added


def _import_videos(run: _Run, videos: list[str]) -> int:
    added = 0
    for url in videos[:MAX_VIDEOS]:
        try:
            materials.add_link(run.record.artist, url, source_import=run.record)
        except materials.MaterialRejected as exc:
            if exc.code != "duplicate":  # already on the list: nothing to report
                run.skip(url, exc.message)
            continue
        added += 1
    return added


def _finish(record: WebsiteImport, status: str, message: str, *, code: str = "") -> None:
    record.status = status
    record.message = message
    record.finished_at = timezone.now()
    started = record.started_at or record.created_at
    duration_ms = int((record.finished_at - started).total_seconds() * 1000)
    with transaction.atomic():
        record.save()
        if record.text:  # the newest text replaces older imports' text (and contacts)
            imports_for(record.artist).filter(created_at__lte=record.created_at).exclude(
                pk=record.pk
            ).update(text="", contacts={})
        analytics.track(
            "website_import_finished",
            actor=record.artist.user,
            obj=record,
            status=status,
            page_count=record.page_count,
            photo_count=record.photo_count,
            duration_ms=duration_ms,
        )
    _log(
        f"website_import_{status}",
        record,
        level=logging.WARNING if status == ImportStatus.FAILED else logging.INFO,
        code=code,
        count=record.page_count,
    )


def run_import(import_id: int) -> str:
    """Job body: fetch, parse and store. Returns the final status ("" if skipped).

    Safe to run twice: only a ``w kolejce`` import is started.
    """
    with transaction.atomic():
        record = (
            WebsiteImport.objects.select_for_update()
            .select_related("artist")
            .filter(pk=import_id, status=ImportStatus.QUEUED)
            .first()
        )
        if record is None:
            return ""
        record.status = ImportStatus.RUNNING
        record.started_at = timezone.now()
        record.save(update_fields=["status", "started_at"])
    run = _Run(record=record, started=time.monotonic(), budget=settings.WEBSITE_IMPORT_MAX_BYTES)
    try:
        failure, images, videos = _crawl(run, record.url)
        if failure:
            record.bytes_fetched = run.used
            _finish(record, ImportStatus.FAILED, failure, code="first_page")
            return record.status
        raw_text = "\n\n".join(
            f"# {page.title}\n{page.text}" if page.title else page.text
            for page in run.pages
            if page.text
        )
        record.contacts = collect_contacts(run.pages)
        record.text = scrub_text(raw_text)[: settings.WEBSITE_IMPORT_MAX_TEXT_CHARS]
        record.page_count = len(run.pages)
        record.photo_count = _import_photos(run, images)
        record.link_count = _import_videos(run, videos)
        record.bytes_fetched = run.used
        record.skipped = run.skipped
    except Exception:
        logger.exception(
            "website import crashed",
            extra={"event": "website_import_error", "website_import": record.pk},
        )
        record.bytes_fetched = run.used
        _finish(record, ImportStatus.FAILED, str(UNEXPECTED), code="error")
        return record.status
    has_text = any(page.text for page in run.pages)
    if not has_text and not record.photo_count and not record.link_count:
        _finish(record, ImportStatus.FAILED, str(NO_TEXT), code="no_text")
    elif run.stopped or run.page_errors or not has_text:
        message = run.stopped or (
            str(NO_TEXT)
            if not has_text
            else gettext("Części podstron nie udało się pobrać; pozostałe zapisaliśmy.")
        )
        _finish(record, ImportStatus.PARTIAL, message, code="partial")
    else:
        _finish(record, ImportStatus.DONE, gettext("Import zakończony."))
    return record.status


def imported_materials(record: WebsiteImport):
    return Material.objects.filter(source_import=record).order_by("created_at", "pk")
