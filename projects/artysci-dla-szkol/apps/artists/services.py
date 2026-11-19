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
from dataclasses import dataclass

from django.db import transaction
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from apps.accounts import services as accounts
from apps.analytics import services as analytics
from apps.core.logs import pseudonymise_user
from apps.core.regions import Voivodeship
from apps.trust import services as trust
from apps.trust.errors import NoPublishedVersion

from .models import Artist, ArtistType, Audience

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
)
LATER_STEPS = {step.key: step for step in STEPS if not step.required}


@dataclass(frozen=True)
class StepStatus:
    step: Step
    done: bool
    available: bool


def wizard_steps(artist: Artist) -> list[StepStatus]:
    """Each wizard step with whether it is done and whether it can be opened. Later steps
    open once the basics are complete; they are placeholders (never done) until their tasks
    land (offers US-2.9, statements US-8.2, materials US-2.3A)."""
    complete = basics_complete(artist)
    return [
        StepStatus(
            step=step,
            done=complete if step.required else False,
            available=True if step.required else complete,
        )
        for step in STEPS
    ]


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
    return created


SEED_EMPTY_BASICS = accounts.ARTIST_COUNT  # artysta10 keeps empty basics (wizard demo)
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
