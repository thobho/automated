"""Generator test set (US-11.2, D12, D57): synthetic artist material packages with checkable
expectations.

    packages()                                  # every apps/quality/testset/*/package.json
    check_package(package)                      # list of problems (empty: valid)
    load_package("teatr-lalek-bogaty")          # creates or updates the synthetic artist
    check_expectations(package, profile_json)   # list of `Result`

A package is plain JSON checked against `testset/package.schema.json` and a few rules in
`check_package`. No binary files: photos are drawn deterministically with Pillow from their spec at
load time. `origin: synthetic` packages must hold no real contact data and no real site; the
loader refuses `origin: consented` until the service has a consent record for the test set.

Deterministic and without AI. Loading makes no network request (link titles come from the
package). Every function that creates rows needs `QUALITY_LAB_ENABLED` (dev, test and pirx only).
"""

import hashlib
import io
import json
import logging
import random
import re
import urllib.parse
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import transaction
from django.utils import timezone
from jsonschema import Draft202012Validator
from PIL import Image, ImageDraw, ImageFont

from apps.accounts import services as accounts
from apps.artists import checks, materials
from apps.artists import services as artist_services
from apps.artists.models import (
    Artist,
    ImportStatus,
    Material,
    MaterialKind,
    ScanStatus,
    TextStatus,
    WebsiteImport,
)
from apps.core.regions import Voivodeship
from apps.core.uploads import UploadRejected
from apps.profiles import inputs
from apps.profiles.ai.scrub import scrub
from apps.profiles.validation import profile_schema
from apps.profiles.validator import public_texts
from apps.trust import services as trust
from apps.trust.models import LegalDocument

from .models import TestsetLoad

logger = logging.getLogger("apps.quality.testset")

TESTSET_DIR = Path(__file__).resolve().parent / "testset"
SCHEMA_FILE = TESTSET_DIR / "package.schema.json"
PACKAGE_FILE = "package.json"
EMAIL_DOMAIN = "example.invalid"  # RFC 2606: can never be a real address or site
LEVELS = ("weak", "medium", "rich")
LEVEL_LABELS = {"weak": "słabe", "medium": "średnie", "rich": "bogate"}
EXPECTATION_KINDS = (
    "field_empty",
    "field_not_empty",
    "text_absent",
    "text_present",
    "no_price",
    "gap_reported",
)
# Width, height of a drawn photo by kind when the spec gives no size.
PHOTO_SIZES = {
    "normal": (1600, 1067),
    "low_resolution": (800, 533),
    "poster": (800, 1100),
    "screenshot": (1920, 1080),
}
NOISE_CELL = 10  # px of one random colour cell before smoothing: photo-like blobs


class LabDisabled(Exception):
    """`QUALITY_LAB_ENABLED` is off: test artists must not appear here."""


class PackageError(Exception):
    """A package is missing, invalid or cannot be loaded. The message names the package."""


def require_enabled() -> None:
    if not settings.QUALITY_LAB_ENABLED:
        raise LabDisabled(
            "QUALITY_LAB_ENABLED is off: the generator test set runs only in dev, test and "
            "pirx settings (synthetic data only, D57)."
        )


# --- reading packages ---------------------------------------------------------------------------


@cache
def _schema() -> dict:
    return json.loads(SCHEMA_FILE.read_text(encoding="utf-8"))


def _folders(root: Path | None) -> list[Path]:
    root = Path(root) if root else TESTSET_DIR
    return sorted(p for p in root.iterdir() if p.is_dir() and not p.name.startswith((".", "_")))


def _read(folder: Path) -> dict:
    path = folder / PACKAGE_FILE
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise PackageError(f"{folder.name}: no {PACKAGE_FILE}") from None
    except (OSError, ValueError) as exc:
        raise PackageError(f"{folder.name}: {PACKAGE_FILE} is not valid JSON ({exc})") from None
    if not isinstance(data, dict):
        raise PackageError(f"{folder.name}: {PACKAGE_FILE} must hold a JSON object")
    return data


def packages(root: Path | None = None) -> list[dict]:
    """Every package, ordered by folder name. Raises `PackageError` for an unreadable file;
    `check_package` finds the other problems."""
    return [_read(folder) for folder in _folders(root)]


def get_package(slug: str, root: Path | None = None) -> dict:
    for folder in _folders(root):
        if folder.name == slug:
            return _read(folder)
    raise PackageError(f"{slug}: no such package")


def check_all(root: Path | None = None) -> list[tuple[str, dict | None, list[str]]]:
    """(folder name, package or None, problems) for every folder; never raises on a bad file."""
    report = []
    for folder in _folders(root):
        try:
            package = _read(folder)
        except PackageError as exc:
            report.append((folder.name, None, [str(exc).split(": ", 1)[1]]))
            continue
        report.append((folder.name, package, check_package(package, folder=folder.name)))
    return report


# --- checking a package ---------------------------------------------------------------------


def _json_path(parts) -> str:
    return "$" + "".join(f"[{p}]" if isinstance(p, int) else f".{p}" for p in parts)


def schema_path_known(path: str) -> bool:
    """`hero.main_photo_id`, `seo.title`, `gaps`: a dotted path of properties of the profile
    schema (arrays are leaves)."""
    node = profile_schema()
    for part in path.split("."):
        properties = node.get("properties") if node.get("type") == "object" else None
        if not properties or part not in properties:
            return False
        node = properties[part]
    return True


def _strings(value):
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for item in value.values():
            yield from _strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _strings(item)


_URL = re.compile(r"https?://[^\s\"'<>)]+", re.I)
_BARE_SITE = re.compile(r"\b(?:www\.[\w-]+|[\w-]+\.(?:pl|com|eu|net|org|info|edu))\b", re.I)
_VIDEO_HOSTS = materials.YOUTUBE_HOSTS | materials.VIMEO_HOSTS | {"youtu.be"}


def _expectation_problems(index: int, item: dict) -> list[str]:
    kind = item.get("kind")
    where = f"expectations[{index}] ({kind})"
    needs = {
        "field_empty": "path",
        "field_not_empty": "path",
        "text_absent": "text",
        "text_present": "text",
        "gap_reported": "code",
    }
    problems = []
    if kind not in EXPECTATION_KINDS:
        return [
            f"expectations[{index}]: unknown kind {kind!r}, allowed: {', '.join(EXPECTATION_KINDS)}"
        ]
    required = needs.get(kind)
    for key in ("path", "text", "code"):
        if key == required and not item.get(key):
            problems.append(f"{where}: needs {key!r}")
        elif key != required and key in item:
            problems.append(f"{where}: {key!r} is not used by this kind")
    path = item.get("path")
    if required == "path" and path and not schema_path_known(path):
        problems.append(f"{where}: path {path!r} is not in the profile schema")
    return problems


def check_package(package: dict, *, folder: str | None = None) -> list[str]:
    """Every problem of `package` as a short sentence (empty list: valid). `folder` is the
    name of its directory, which must equal the slug."""
    problems = []
    validator = Draft202012Validator(_schema())
    for error in sorted(validator.iter_errors(package), key=lambda e: list(map(str, e.path))):
        problems.append(f"{_json_path(error.absolute_path)}: {error.message[:200]}")
    if problems:  # the rules below assume the shape
        return problems
    if folder is not None and folder != package["slug"]:
        problems.append(f"slug {package['slug']!r} differs from the folder name {folder!r}")
    for value in package["artist"]["voivodeships"]:
        if value not in Voivodeship.values:
            problems.append(f"artist.voivodeships: unknown voivodeship {value!r}")
    for key, message in materials.questionnaire_errors(package["questionnaire"]).items():
        problems.append(f"questionnaire.{key}: {message}")
    for i, offer in enumerate(package["offers"]):
        for key, message in artist_services.offer_errors(_offer_data(offer)).items():
            problems.append(f"offers[{i}].{key}: {message}")
    seen = set()
    for i, video in enumerate(package["videos"]):
        ref = materials.parse_video_url(video["url"])
        if ref is None:
            problems.append(f"videos[{i}].url: not a YouTube or Vimeo link")
        elif (ref.provider, ref.video_id) in seen:
            problems.append(f"videos[{i}].url: the same video twice")
        else:
            seen.add((ref.provider, ref.video_id))
    for i, item in enumerate(package["expectations"]):
        problems += _expectation_problems(i, item)
    for key, kind in (("photos", MaterialKind.PHOTO), ("documents", MaterialKind.PDF)):
        if len(package[key]) > materials.limit_for(kind):
            problems.append(
                f"{key}: {len(package[key])} items, the limit is {materials.limit_for(kind)}"
            )
    if len(package["videos"]) > materials.limit_for(MaterialKind.VIDEO):
        problems.append(
            f"videos: {len(package['videos'])} items, "
            f"the limit is {materials.limit_for(MaterialKind.VIDEO)}"
        )
    if package["origin"] == "synthetic":
        problems += _synthetic_problems(package)
    return problems


def _synthetic_problems(package: dict) -> list[str]:
    """The synthetic-only rule (D12, D57): no contact data, account numbers or real sites."""
    problems = []
    for text in _strings(package):
        if scrub(text) != text:
            problems.append(f"contact or personal data in a text: {text[:60]!r}…")
        for url in _URL.findall(text):
            try:
                host = (urllib.parse.urlsplit(url.rstrip(".,;:!?")).hostname or "").lower()
            except ValueError:
                problems.append(f"malformed URL in a text: {url[:60]!r}")
                continue
            if (
                host != EMAIL_DOMAIN
                and not host.endswith("." + EMAIL_DOMAIN)
                and host not in _VIDEO_HOSTS
            ):
                problems.append(
                    f"URL with a real host {host!r}: only {EMAIL_DOMAIN} and YouTube/Vimeo"
                )
        for site in _BARE_SITE.findall(_URL.sub(" ", text)):
            if not site.lower().endswith(EMAIL_DOMAIN):
                problems.append(f"possible real site {site!r}: use a host under {EMAIL_DOMAIN}")
    return problems


# --- expectations -------------------------------------------------------------------------------


@dataclass(frozen=True)
class Result:
    kind: str
    detail: str
    passed: bool
    message: str


_CURRENCY = r"(?:zł|zl|pln|złotych|złote|złoty|zloty)"
_PRICE = re.compile(
    # a number, an optional multiplier and a currency after it: "500 zł", "2 tys. zł"
    rf"\d[\d\s.,]*(?:\s*(?:tys|mln)\.?)?\s*{_CURRENCY}(?!\w)"
    r"|(?<!\w)\d[\d\s.]*,-"  # "500,-"
    rf"|(?<!\w){_CURRENCY}\s*\d"  # "PLN 500"
    # a price word, optional "to/od/do/wynosi/:", then a number that is not a measure
    r"|(?<!\w)(?:cen[aęyieą]|cenach|cennik\w*|koszt\w*)(?!\w)"
    r"(?:\s*(?::|to\b|od\b|do\b|wynosi\b|około\b|ok\.))*\s*"
    r"\d+(?:[ .,]\d+)*(?!\d)"
    r"(?!\s*(?:minut|min\b|dzieci|osób|osoby|km\b|lat\b|godzin|godz\b|uczni|sekund))",
    re.I,
)


def _norm(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip().casefold()


def all_public_texts(profile: dict) -> list[tuple[str, str]]:
    """(path, text) of every text of the public page, testimonial quotes included."""
    texts = list(public_texts(profile))
    for i, item in enumerate(profile.get("testimonials") or []):
        texts.append((f"$.testimonials[{i}].quote", item.get("quote") or ""))
    return texts


def _value_at(profile: dict, path: str):
    node = profile
    for part in path.split("."):
        if not isinstance(node, dict):
            return None
        node = node.get(part)
    return node


def _empty(value) -> bool:
    return value is None or value == "" or value == [] or value == {}


def _check_one(item: dict, profile: dict) -> Result:
    kind = item["kind"]
    if kind in ("field_empty", "field_not_empty"):
        path = item["path"]
        empty = _empty(_value_at(profile, path))
        passed = empty if kind == "field_empty" else not empty
        state = "empty" if empty else "not empty"
        wanted = "empty" if kind == "field_empty" else "not empty"
        return Result(kind, path, passed, f"{path} is {state}, expected {wanted}")
    if kind in ("text_present", "text_absent"):
        phrase = item["text"]
        found = [p for p, text in all_public_texts(profile) if _norm(phrase) in _norm(text)]
        passed = bool(found) if kind == "text_present" else not found
        if kind == "text_present":
            message = "found" if passed else "not found in the public texts"
        else:
            message = "absent" if passed else f"found at {', '.join(found)}"
        return Result(kind, phrase, passed, f"{phrase!r} {message}")
    if kind == "gap_reported":
        code = item["code"]
        codes = [gap.get("code") for gap in profile.get("gaps") or []]
        passed = code in codes
        return Result(
            kind, code, passed, f"gap {code!r} " + ("reported" if passed else "not reported")
        )
    texts = all_public_texts(profile)
    for i, fact in enumerate(profile.get("facts") or []):  # a label and its value read together
        texts.append(
            (f"$.facts[{i}].value", f"{fact.get('label') or ''} {fact.get('value') or ''}")
        )
    found = list(dict.fromkeys(p for p, text in texts if _PRICE.search(text)))  # no_price
    message = "no price in the public texts" if not found else f"price found at {', '.join(found)}"
    return Result(kind, ", ".join(found), not found, message)


def check_expectations(package: dict, profile_json: dict) -> list[Result]:
    """Every expectation of `package` against `profile_json`. An unknown kind or path is an
    error (`PackageError`), never a silent pass."""
    results = []
    for i, item in enumerate(package.get("expectations") or []):
        problems = _expectation_problems(i, item)
        if problems:
            raise PackageError(f"{package.get('slug', '?')}: {problems[0]}")
        results.append(_check_one(item, profile_json))
    return results


# --- drawing photos -------------------------------------------------------------------------


def draw_photo(spec: dict, seed: str) -> bytes:
    """JPEG bytes of a photo drawn from `spec` (`kind`, optional `width` and `height`).
    The same spec and seed give the same pixels."""
    kind = spec["kind"]
    default_width, default_height = PHOTO_SIZES[kind]
    width, height = spec.get("width", default_width), spec.get("height", default_height)
    if kind == "poster":
        image = Image.new("RGB", (width, height), (250, 220, 40))
        draw = ImageDraw.Draw(image)
        font = ImageFont.load_default(size=max(40, width // 4))
        step = max(60, height // 3)
        for line, word in enumerate(("KON", "CERT")):
            draw.text((width // 25, height // 14 + line * step), word, fill=(20, 20, 20), font=font)
    else:  # random coloured blobs: like a photo, not like a flat graphic
        rng = random.Random(seed)  # noqa: S311 - a reproducible picture, not a secret
        cells = (max(1, width // NOISE_CELL), max(1, height // NOISE_CELL))
        raw = bytes(rng.randrange(256) for _ in range(3 * cells[0] * cells[1]))
        image = Image.frombytes("RGB", cells, raw).resize((width, height), Image.Resampling.BICUBIC)
    out = io.BytesIO()
    image.save(out, "JPEG", quality=92)
    return out.getvalue()


# --- loading a package ----------------------------------------------------------------------------


@dataclass(frozen=True)
class LoadResult:
    artist: Artist
    changed: bool  # False: the package was already loaded unchanged


def package_digest(package: dict) -> str:
    canonical = json.dumps(package, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(canonical.encode()).hexdigest()


def artist_email(slug: str) -> str:
    return f"testset-{slug}@{EMAIL_DOMAIN}"


def _offer_data(offer: dict) -> dict:
    return {
        "age_from": None, "age_to": None, "duration_minutes": None, "price_pln": None,
        "price_on_request": False, **offer,
    }  # fmt: skip


def _ensure_rights(artist: Artist) -> None:
    """The artist's current "Prawa do materiałów" statement (without it no material counts)."""
    if trust.current(LegalDocument.Kind.MATERIAL_RIGHTS) is None:
        trust.seed_placeholders()  # dev and pirx only: the lab switch is checked before
    if not inputs.materials_allowed(artist):
        trust.make_statement(artist, LegalDocument.Kind.MATERIAL_RIGHTS)


def _rights_statement(artist: Artist):
    return next(
        s for s in trust.current_statements(artist) if s.kind == LegalDocument.Kind.MATERIAL_RIGHTS
    )


def _replace_content(artist: Artist, package: dict) -> None:
    """Drop the artist's old materials, offers and imports and store the package's text content.
    Generations stay untouched (append-only registry)."""
    slug = package["slug"]
    TestsetLoad.objects.filter(artist=artist).delete()  # half-loaded until the end
    for material in list(Material.objects.filter(artist=artist)):
        materials.delete_material(artist, material.pk)
    for offer in list(artist_services.offers_for(artist)):
        artist_services.delete_offer(artist, offer.pk)
    WebsiteImport.objects.filter(artist=artist).delete()
    basics = package["artist"]
    artist_services.save_basics(
        artist.user,
        {
            "artist_type": basics["type"], "name": basics["name"], "city": basics["city"],
            "voivodeships": basics["voivodeships"], "audiences": basics["audiences"],
        },
    )  # fmt: skip
    artist.refresh_from_db()
    materials.save_questionnaire(artist, package["questionnaire"])
    for offer in package["offers"]:
        artist_services.create_offer(artist, _offer_data(offer))
    now = timezone.now()
    if package["site_text"].strip():
        WebsiteImport.objects.create(
            artist=artist,
            url=f"https://{slug}.{EMAIL_DOMAIN}/",
            status=ImportStatus.DONE,
            rights_confirmed_at=now,
            rights_statement=_rights_statement(artist),
            page_count=1,
            pages=[{"url": f"https://{slug}.{EMAIL_DOMAIN}/", "title": basics["name"]}],
            text=package["site_text"],
            started_at=now,
            finished_at=now,
        )
    for document in package["documents"]:
        Material.objects.create(
            artist=artist,
            kind=MaterialKind.PDF,
            status=ScanStatus.READY,
            original_name=document["name"],
            content_type="application/pdf",
            text=document["text"],
            text_status=TextStatus.DONE,
        )  # fmt: skip  (no file: the text is what the generator reads)
    for video in package["videos"]:
        ref = materials.parse_video_url(video["url"])
        Material.objects.create(
            artist=artist,
            kind=MaterialKind.LINK,
            status=ScanStatus.READY,
            provider=ref.provider,
            video_id=ref.video_id,
            canonical_url=ref.canonical_url,
            title=video["title"],
        )  # fmt: skip  (the title comes from the package: no oEmbed request)


def _add_photos(artist: Artist, package: dict) -> None:
    """Draw and upload the photos through the real upload path, then scan and check them at
    once (the jobs queued by the upload find nothing left to do)."""
    for index, spec in enumerate(package["photos"], start=1):
        data = draw_photo(spec, f"{package['slug']}:{index}")
        upload = SimpleUploadedFile(f"{package['slug']}-{index}.jpg", data, "image/jpeg")
        try:
            material = materials.add_file(artist, MaterialKind.PHOTO, upload)
            materials.scan_material(material.pk)
            checks.check_material(material.pk)
        except (
            materials.MaterialRejected,
            UploadRejected,
            materials.ScanNotFinished,
        ) as error:
            raise PackageError(
                f"{package['slug']}: photo {index} was rejected: {type(error).__name__}"
            ) from error
        material.refresh_from_db()
        if material.status != ScanStatus.READY or material.checks_version < 1:
            raise PackageError(f"{package['slug']}: photo {index} is not ready after the checks")


def load(slug: str, *, root: Path | None = None) -> LoadResult:
    """Create or update the synthetic artist of one package. Loading an unchanged package
    again changes nothing; a changed one replaces the artist's materials and offers."""
    require_enabled()
    package = get_package(slug, root)
    if package.get("origin") == "consented":
        raise PackageError(
            f"{slug}: origin 'consented' is not loadable yet: the service has no consent record "
            "for the test set (D12)"
        )
    problems = check_package(package, folder=slug)
    if problems:
        raise PackageError(
            f"{slug}: {problems[0]}"
            + (f" (+{len(problems) - 1} more)" if len(problems) > 1 else "")
        )
    digest = package_digest(package)
    user, _ = accounts.get_or_create_unconfirmed_user(artist_email(slug))
    artist, _ = Artist.objects.get_or_create(
        user=user, defaults={"name": package["artist"]["name"]}
    )
    _ensure_rights(artist)
    existing = TestsetLoad.objects.filter(slug=slug).first()
    if existing and existing.artist_id == artist.pk and existing.digest == digest:
        return LoadResult(artist, changed=False)
    with transaction.atomic():
        _replace_content(artist, package)
    _add_photos(artist, package)
    TestsetLoad.objects.create(slug=slug, artist=artist, digest=digest, loaded_at=timezone.now())
    logger.info("test set package loaded", extra={"event": "testset_loaded", "package": slug})
    artist.refresh_from_db()
    return LoadResult(artist, changed=True)


def load_package(slug: str, *, root: Path | None = None) -> Artist:
    """The synthetic artist of the package `slug` (created or updated). Raises `LabDisabled`
    or `PackageError` (invalid, unknown, `origin: consented`) before any row is created."""
    return load(slug, root=root).artist
