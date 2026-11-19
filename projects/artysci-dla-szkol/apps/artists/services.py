"""Artist services: registration (US-1.1, D1, D2, D30) and the profile wizard's step 1, the
basics (US-2.1, D102: `save_basics`, `basics_complete`, `wizard_steps`).

`register_artist()` creates an unconfirmed account, its artist record and the acceptance of the
current terms and privacy policy in one transaction, then sends the login link and code through
`accounts.services.request_login()`, so the US-1.3 validity, single use and sending limits apply
unchanged. Using the link or code confirms the account (`accounts.services.confirm_email`).

An address that already has an account gets exactly the same answer and a normal login e-mail;
nothing is created or recorded for it. Logs carry a pseudonymised user only.
"""

import enum
import logging
from dataclasses import asdict, dataclass

from django.db import transaction
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.accounts import services as accounts
from apps.analytics import services as analytics
from apps.core import media, uploads
from apps.core.logs import pseudonymise_user
from apps.core.regions import Voivodeship
from apps.trust import services as trust
from apps.trust.errors import NoPublishedVersion

from . import materials, website_import
from .models import MAX_AGE, Artist, ArtistType, Audience, Offer, ScanStatus

logger = logging.getLogger("apps.artists.registration")
profile_logger = logging.getLogger("apps.artists.profile")

REQUIRED_DOCUMENTS = (trust.Kind.TERMS, trust.Kind.PRIVACY)


class Registration(enum.Enum):
    SENT = "sent"  # same for a new and an existing address
    RATE_LIMITED = "rate_limited"
    UNAVAILABLE = "unavailable"  # no published terms or privacy version


def documents_published() -> bool:
    return all(trust.current(kind) is not None for kind in REQUIRED_DOCUMENTS)


def _create(email: str, name: str) -> Artist | None:
    """New user + artist + acceptance, all or nothing. None if the address is taken."""
    with transaction.atomic():
        user, created = accounts.get_or_create_unconfirmed_user(email)
        if not created:
            return None
        artist = Artist.objects.create(user=user, name=name.strip())
        trust.record_acceptance(user, REQUIRED_DOCUMENTS)  # raises -> rollback
    return artist


def register_artist(email: str, name: str, client_ip: str, *, link_base: str) -> Registration:
    """Register an artist and send the login e-mail. See the module docstring."""
    if not documents_published():
        logger.warning(
            "registration refused, no published legal documents",
            extra={"event": "registration_unavailable"},
        )
        return Registration.UNAVAILABLE
    if not accounts.login_email_allowed(email, client_ip):
        logger.warning("registration rate limited", extra={"event": "registration_rate_limited"})
        return Registration.RATE_LIMITED
    try:
        artist = _create(email, name)
    except NoPublishedVersion:  # withdrawn between the check and the insert
        return Registration.UNAVAILABLE

    next_path = ""
    if artist is not None:
        analytics.track("artist_registered", actor=artist.user, obj=artist, source="form")
        logger.info(
            "artist registered",
            extra={"event": "artist_registered", "user": pseudonymise_user(artist.user_id)},
        )
        next_path = reverse("artists:start")
    else:
        logger.info("registration for an existing address", extra={"event": "registration_exists"})
    if not accounts.request_login(email, client_ip, link_base=link_base, next_path=next_path):
        return Registration.RATE_LIMITED
    return Registration.SENT


def artist_for(user) -> Artist | None:
    if not getattr(user, "is_authenticated", False):
        return None
    return Artist.objects.filter(user=user).first()


def rename_artist(user, name: str) -> bool:
    """Set the artist name of `user` (account settings, US-1.6). False if `user` is not an
    artist or the name is blank (nothing changes)."""
    name = name.strip()
    if not name:
        return False
    return Artist.objects.filter(user_id=user.pk).update(name=name) == 1


# --- profile wizard, step 1: basics (US-2.1, D102) --------------------------------------------


class InvalidBasics(ValueError):
    """`save_basics()` got a missing or unknown value (the form should have caught it)."""


@dataclass(frozen=True)
class Basics:
    artist_type: str
    name: str
    city: str
    voivodeships: tuple[str, ...]
    audiences: tuple[str, ...]


def basics_of(artist: Artist) -> Basics:
    """The stored basics (empty strings and tuples when not filled in yet); multi-values in
    the order of their choice lists."""
    return Basics(
        artist_type=artist.artist_type,
        name=artist.name,
        city=artist.city,
        voivodeships=_in_choice_order(
            artist.voivodeships.values_list("voivodeship", flat=True), Voivodeship
        ),
        audiences=_in_choice_order(artist.audiences.values_list("audience", flat=True), Audience),
    )


def _in_choice_order(values, choices) -> tuple[str, ...]:
    present = set(values)
    return tuple(value for value in choices.values if value in present)


def basics_complete(artist: Artist | None) -> bool:
    """True when every basic field is filled: the later wizard steps open only then."""
    if artist is None:
        return False
    return bool(
        artist.artist_type
        and artist.name.strip()
        and artist.city.strip()
        and artist.voivodeships.exists()
        and artist.audiences.exists()
    )


def _clean(data) -> Basics:
    def one_of(value, choices, field):
        if value not in choices.values:
            raise InvalidBasics(field)
        return value

    def many_of(values, choices, field):
        values = tuple(dict.fromkeys(values or ()))  # unique, order kept
        if not values:
            raise InvalidBasics(field)
        return tuple(one_of(v, choices, field) for v in values)

    name = (data.get("name") or "").strip()
    city = (data.get("city") or "").strip()
    if not name:
        raise InvalidBasics("name")
    if not city:
        raise InvalidBasics("city")
    return Basics(
        artist_type=one_of(data.get("artist_type"), ArtistType, "artist_type"),
        name=name,
        city=city,
        voivodeships=many_of(data.get("voivodeships"), Voivodeship, "voivodeships"),
        audiences=many_of(data.get("audiences"), Audience, "audiences"),
    )


def save_basics(user, data) -> Artist:
    """Store step 1 for the artist of `user`, all or nothing. `data` has ``artist_type``,
    ``name``, ``city``, ``voivodeships`` and ``audiences`` (lists of choice values).

    Raises `InvalidBasics` (nothing saved) for a missing or unknown value and
    `Artist.DoesNotExist` if `user` is not an artist. The name goes through `rename_artist()`,
    the single way to change it (D97, D101). Voivodeships and audiences are replaced as sets.
    """
    basics = _clean(data)
    with transaction.atomic():
        artist = Artist.objects.select_for_update().get(user_id=user.pk)
        rename_artist(user, basics.name)
        artist.artist_type = basics.artist_type
        artist.city = basics.city
        artist.save(update_fields=["artist_type", "city"])
        _replace(artist.voivodeships, "voivodeship", basics.voivodeships)
        _replace(artist.audiences, "audience", basics.audiences)
    artist.refresh_from_db()
    profile_logger.info(
        "artist basics saved",
        extra={"event": "artist_basics_saved", "user": pseudonymise_user(user.pk)},
    )
    return artist


def _replace(related, field: str, values: tuple[str, ...]) -> None:
    related.exclude(**{f"{field}__in": values}).delete()
    existing = set(related.values_list(field, flat=True))
    related.model.objects.bulk_create(
        related.model(artist=related.instance, **{field: value})
        for value in values
        if value not in existing
    )


@dataclass(frozen=True)
class Step:
    key: str
    title: str
    url_name: str
    required: bool = False


STEPS = (
    Step("basics", _("Dane podstawowe"), "artists:basics", required=True),
    Step("offers", _("Oferty"), "artists:offers"),
    Step("statements", _("Oświadczenia"), "artists:statements"),
    Step("materials", _("Materiały i kwestionariusz"), "artists:materials"),
    Step("import", _("Import ze strony (opcjonalnie)"), "artists:website_import"),
)


@dataclass(frozen=True)
class StepStatus:
    step: Step
    done: bool
    available: bool


def wizard_steps(artist: Artist) -> list[StepStatus]:
    """Each wizard step with whether it is done and whether it can be opened. Later steps
    open once the basics are complete. Offers are done with at least one offer (D6);
    statements with a counted child-protection statement (D6, US-8.2); materials with at least
    one ready material (scanned file or checked link, US-2.3A)."""
    complete = basics_complete(artist)
    done = {
        "basics": complete,
        "offers": complete and has_offers(artist),
        "statements": complete and trust.has_child_protection_statement(artist),
        "materials": complete and materials.has_ready_materials(artist),
        "import": complete and website_import.has_finished_import(artist),
    }
    return [
        StepStatus(
            step=step,
            done=done.get(step.key, False),
            available=True if step.required else complete,
        )
        for step in STEPS
    ]


# --- profile wizard, step "Oferty": offers and repertoire (US-2.9, D2, D6, D103) --------------


class InvalidOffer(ValueError):
    """`create_offer()` / `update_offer()` got invalid data. `errors` maps a field name to a
    Polish message (the form shows the same messages)."""

    def __init__(self, errors: dict):
        super().__init__(", ".join(sorted(errors)))
        self.errors = errors


@dataclass(frozen=True)
class OfferData:
    title: str
    description: str
    age_from: int | None
    age_to: int | None
    duration_minutes: int | None
    price_pln: int | None
    price_on_request: bool


OFFER_FIELDS = tuple(OfferData.__dataclass_fields__)


def _optional_int(value, field, errors, *, low, high=None):
    if value in (None, ""):
        return None
    try:
        number = int(value)
    except (TypeError, ValueError):
        errors[field] = _("Podaj liczbę całkowitą.")
        return None
    if number < low or (high is not None and number > high):
        errors[field] = (
            _("Podaj liczbę od %(low)d do %(high)d.") % {"low": low, "high": high}
            if high is not None
            else _("Podaj liczbę większą od zera.")
        )
        return None
    return number


def offer_errors(data) -> dict:
    """Field -> Polish message for everything wrong in `data` (empty dict: valid). The form
    and the services use this one rule set."""
    return _clean_offer(data)[1]


def _clean_offer(data) -> tuple[OfferData | None, dict]:
    errors: dict = {}
    title = (data.get("title") or "").strip()
    description = (data.get("description") or "").strip()
    if not title:
        errors["title"] = _("Podaj tytuł.")
    elif len(title) > Offer._meta.get_field("title").max_length:
        errors["title"] = _("Tytuł jest za długi.")
    if not description:
        errors["description"] = _("Podaj opis.")
    elif len(description) > Offer._meta.get_field("description").max_length:
        errors["description"] = _("Opis jest za długi.")
    age_from = _optional_int(data.get("age_from"), "age_from", errors, low=0, high=MAX_AGE)
    age_to = _optional_int(data.get("age_to"), "age_to", errors, low=0, high=MAX_AGE)
    if age_from is not None and age_to is not None and age_from > age_to:
        errors["age_to"] = _("Wiek „do” nie może być mniejszy niż wiek „od”.")
    duration = _optional_int(data.get("duration_minutes"), "duration_minutes", errors, low=1)
    price = _optional_int(data.get("price_pln"), "price_pln", errors, low=1)
    on_request = bool(data.get("price_on_request"))
    if "price_pln" not in errors and (price is None) == (not on_request):
        errors["price_pln"] = _("Podaj cenę w złotych albo zaznacz „na zapytanie” (jedno z dwóch).")
    if errors:
        return None, errors
    return OfferData(title, description, age_from, age_to, duration, price, on_request), {}


def _validated(data) -> OfferData:
    cleaned, errors = _clean_offer(data)
    if errors:
        raise InvalidOffer(errors)
    return cleaned


def offers_for(artist: Artist):
    """The artist's offers in their order (queryset)."""
    return Offer.objects.filter(artist=artist).order_by("position", "pk")


def has_offers(artist: Artist | None) -> bool:
    """D6: a profile can be published only with at least one offer (used by US-2.8)."""
    return artist is not None and Offer.objects.filter(artist=artist).exists()


def get_offer(artist: Artist, offer_id) -> Offer:
    """The artist's own offer; `Offer.DoesNotExist` for another artist's or a missing id
    (the views answer 404 for both: no existence leak)."""
    return Offer.objects.get(artist=artist, pk=offer_id)


def offer_data(offer: Offer) -> dict:
    return {field: getattr(offer, field) for field in OFFER_FIELDS}


def poster_url(offer: Offer) -> str:
    """Short-lived signed URL of the private poster ("" without a poster)."""
    return media.signed_url(offer.poster_key) if offer.poster_key else ""


def _store_poster(poster) -> str:
    """Store through the T06 path (sniffed type, 15 MB, EXIF stripped, random key, private).
    Raises `UploadRejected`."""
    return uploads.store_upload(poster, kind="photo", visibility="private").key


def _delete_file(key: str) -> None:
    if not key:
        return
    try:
        media.private_storage().delete(key)
    except Exception:  # storage down: the row change stands, the orphan is only logged
        profile_logger.warning(
            "poster file could not be deleted", extra={"event": "offer_poster_orphan"}
        )


def _delete_after_commit(key: str) -> None:
    if key:
        transaction.on_commit(lambda: _delete_file(key))


def _log(event: str, artist: Artist, offer_id) -> None:
    profile_logger.info(
        event.replace("_", " "),
        extra={"event": event, "user": pseudonymise_user(artist.user_id), "offer": offer_id},
    )


def create_offer(artist: Artist, data, *, poster=None) -> Offer:
    """Add an offer at the end of the artist's list. Raises `InvalidOffer` or
    `UploadRejected` (for the poster); nothing is saved in either case."""
    cleaned = _validated(data)
    key = _store_poster(poster) if poster else ""
    try:
        with transaction.atomic():
            Artist.objects.select_for_update().filter(pk=artist.pk).first()
            last = offers_for(artist).last()
            offer = Offer.objects.create(
                artist=artist,
                position=last.position + 1 if last else 0,
                poster_key=key,
                poster_status=ScanStatus.PENDING if key else "",
                **asdict(cleaned),
            )
            if key:
                materials.enqueue_poster_scan(offer.pk, key)
    except Exception:
        _delete_file(key)
        raise
    _log("offer_created", artist, offer.pk)
    return offer


def update_offer(artist: Artist, offer_id, data, *, poster=None, remove_poster=False) -> Offer:
    """Change the artist's own offer. A new `poster` replaces the old one, `remove_poster`
    drops it; the old file leaves storage after the commit. Raises `Offer.DoesNotExist`,
    `InvalidOffer` or `UploadRejected` (nothing changes)."""
    get_offer(artist, offer_id)  # 404 before validating or storing anything
    cleaned = _validated(data)
    new_key = _store_poster(poster) if poster else ""
    try:
        with transaction.atomic():
            offer = Offer.objects.select_for_update().get(artist=artist, pk=offer_id)
            old_key = offer.poster_key
            for field, value in asdict(cleaned).items():
                setattr(offer, field, value)
            if new_key or remove_poster:
                offer.poster_key = new_key
                offer.poster_status = ScanStatus.PENDING if new_key else ""
            offer.updated_at = timezone.now()
            offer.save()
            if offer.poster_key != old_key:
                _delete_after_commit(old_key)
            if new_key:
                materials.enqueue_poster_scan(offer.pk, new_key)
    except Exception:
        _delete_file(new_key)
        raise
    _log("offer_updated", artist, offer.pk)
    return offer


def delete_offer(artist: Artist, offer_id) -> None:
    """Delete the artist's own offer and, after the commit, its poster file. Raises
    `Offer.DoesNotExist`."""
    with transaction.atomic():
        offer = Offer.objects.select_for_update().get(artist=artist, pk=offer_id)
        key = offer.poster_key
        offer.delete()
        _delete_after_commit(key)
    _log("offer_deleted", artist, offer_id)


def reorder_offers(artist: Artist, offer_ids) -> None:
    """Set the order to `offer_ids`, which must be exactly the artist's offer ids (else
    `ValueError`, nothing changes). Positions become 0..n-1."""
    offer_ids = [int(pk) for pk in offer_ids]
    with transaction.atomic():
        offers = {o.pk: o for o in offers_for(artist).select_for_update()}
        if len(offer_ids) != len(set(offer_ids)) or set(offer_ids) != offers.keys():
            raise ValueError("offer_ids must be exactly the artist's offers")
        changed = []
        for position, pk in enumerate(offer_ids):
            if offers[pk].position != position:
                offers[pk].position = position
                changed.append(offers[pk])
        Offer.objects.bulk_update(changed, ["position"])


def move_offer(artist: Artist, offer_id, direction: str) -> None:
    """Move the artist's own offer one place "up" or "down" (no-op at either end). Raises
    `Offer.DoesNotExist` or `ValueError` for another direction."""
    if direction not in ("up", "down"):
        raise ValueError(direction)
    with transaction.atomic():
        Artist.objects.select_for_update().filter(pk=artist.pk).first()
        ids = list(offers_for(artist).values_list("pk", flat=True))
        offer_id = int(offer_id)
        if offer_id not in ids:
            raise Offer.DoesNotExist
        index = ids.index(offer_id)
        other = index - 1 if direction == "up" else index + 1
        if 0 <= other < len(ids):
            ids[index], ids[other] = ids[other], ids[index]
        reorder_offers(artist, ids)


def seed_artists() -> int:
    """Artist records for the synthetic ``artystaNN@example.invalid`` seed users (idempotent;
    run after `accounts.services.seed_users`). Returns how many were created. Every seed
    artist but the last (`SEED_EMPTY_BASICS`) gets synthetic basics if it has none (D57)."""
    from django.contrib.auth import get_user_model

    created = 0
    for number in range(1, accounts.ARTIST_COUNT + 1):
        user = (
            get_user_model()
            .objects.filter(email=f"artysta{number:02d}@{accounts.SEED_DOMAIN}")
            .first()
        )
        if user is None or user.is_staff or user.is_superuser:
            continue
        artist = Artist.objects.filter(user=user).first()
        if artist is None:
            artist = Artist.objects.create(user=user, name=f"Artysta Testowy {number:02d}")
            created += 1
        if number != SEED_EMPTY_BASICS and not basics_complete(artist):
            save_basics(user, _seed_basics(number, artist.name))
        if number == SEED_REPERTOIRE and not has_offers(artist):
            for data in _seed_repertoire():
                create_offer(artist, data)
    return created


SEED_EMPTY_BASICS = accounts.ARTIST_COUNT  # artysta10 keeps empty basics (wizard demo)
SEED_REPERTOIRE = 1  # artysta01 gets a 20-show synthetic repertoire (US-2.9, D2)
SEED_REPERTOIRE_SIZE = 20


def _seed_repertoire() -> list[dict]:
    """Synthetic offers (no posters: the seed never touches storage)."""
    offers = []
    for n in range(1, SEED_REPERTOIRE_SIZE + 1):
        age_from = 3 + n % 8
        offers.append(
            {
                "title": f"Spektakl testowy {n:02d}",
                "description": f"Syntetyczny opis spektaklu {n:02d} do testów kreatora.",
                "age_from": age_from,
                "age_to": age_from + 4,
                "duration_minutes": 30 + 5 * (n % 6),
                "price_pln": None if n % 5 == 0 else 800 + 50 * n,
                "price_on_request": n % 5 == 0,
            }
        )
    return offers


_SEED_CITIES = ("Wrocław", "Kraków", "Poznań", "Gdańsk", "Lublin", "Łódź", "Opole", "Toruń")


def _seed_basics(number: int, name: str) -> dict:
    types, voivodeships, audiences = ArtistType.values, Voivodeship.values, Audience.values
    return {
        "artist_type": types[number % len(types)],
        "name": name,
        "city": _SEED_CITIES[number % len(_SEED_CITIES)],
        "voivodeships": [voivodeships[number % 16], voivodeships[(number + 5) % 16]],
        "audiences": audiences[number % 3 : number % 3 + 3],
    }
