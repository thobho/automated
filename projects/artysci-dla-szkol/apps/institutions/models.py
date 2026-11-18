from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class InstitutionType(models.TextChoices):
    PRIMARY_SCHOOL = "primary_school", _("szkoła podstawowa")
    KINDERGARTEN = "kindergarten", _("przedszkole")
    SECONDARY_SCHOOL = "secondary_school", _("szkoła ponadpodstawowa")
    CULTURE_CENTRE = "culture_centre", _("dom kultury")
    OTHER = "other", _("inne")


class Voivodeship(models.TextChoices):
    """The 16 Polish voivodeships (a fixed choice)."""

    DOLNOSLASKIE = "dolnoslaskie", _("dolnośląskie")
    KUJAWSKO_POMORSKIE = "kujawsko-pomorskie", _("kujawsko-pomorskie")
    LUBELSKIE = "lubelskie", _("lubelskie")
    LUBUSKIE = "lubuskie", _("lubuskie")
    LODZKIE = "lodzkie", _("łódzkie")
    MALOPOLSKIE = "malopolskie", _("małopolskie")
    MAZOWIECKIE = "mazowieckie", _("mazowieckie")
    OPOLSKIE = "opolskie", _("opolskie")
    PODKARPACKIE = "podkarpackie", _("podkarpackie")
    PODLASKIE = "podlaskie", _("podlaskie")
    POMORSKIE = "pomorskie", _("pomorskie")
    SLASKIE = "slaskie", _("śląskie")
    SWIETOKRZYSKIE = "swietokrzyskie", _("świętokrzyskie")
    WARMINSKO_MAZURSKIE = "warminsko-mazurskie", _("warmińsko-mazurskie")
    WIELKOPOLSKIE = "wielkopolskie", _("wielkopolskie")
    ZACHODNIOPOMORSKIE = "zachodniopomorskie", _("zachodniopomorskie")


class VerificationStatus(models.TextChoices):
    """US-1.2 only knows the default; US-1.4 adds the verified states."""

    UNVERIFIED = "unverified", _("niezweryfikowana")


class MemberFunction(models.TextChoices):
    DIRECTOR = "director", _("dyrektor")
    TEACHER = "teacher", _("nauczyciel")
    PEDAGOGUE = "pedagogue", _("pedagog")
    OTHER = "other", _("inna")


class Institution(models.Model):
    """A school, kindergarten or cultural centre. One institution can have several member
    accounts; a second account for the same RSPO number is linked for review (US-1.2)."""

    institution_type = models.CharField(_("typ"), max_length=32, choices=InstitutionType.choices)
    name = models.CharField(_("nazwa"), max_length=300)  # RSPO names can be long
    locality = models.CharField(_("miejscowość"), max_length=100)
    voivodeship = models.CharField(_("województwo"), max_length=32, choices=Voivodeship.choices)
    rspo_number = models.PositiveIntegerField(_("numer RSPO"), null=True, blank=True, unique=True)
    verification_status = models.CharField(
        _("status weryfikacji"),
        max_length=32,
        choices=VerificationStatus.choices,
        default=VerificationStatus.UNVERIFIED,
    )
    created_at = models.DateTimeField(_("utworzono"), default=timezone.now)

    class Meta:
        verbose_name = _("placówka")
        verbose_name_plural = _("placówki")

    def __str__(self) -> str:
        return self.name


class InstitutionMember(models.Model):
    """The link between an account and its institution: one account = one institution."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="institution_member"
    )
    institution = models.ForeignKey(
        Institution, on_delete=models.PROTECT, related_name="members", verbose_name=_("placówka")
    )
    function = models.CharField(_("funkcja"), max_length=32, choices=MemberFunction.choices)
    needs_review = models.BooleanField(
        _("do sprawdzenia"),
        default=False,
        help_text=_("Konto dołączyło do placówki, która miała już konto (US-1.2)."),
    )
    created_at = models.DateTimeField(_("utworzono"), default=timezone.now)

    class Meta:
        verbose_name = _("członek placówki")
        verbose_name_plural = _("członkowie placówek")

    def __str__(self) -> str:
        return f"InstitutionMember {self.pk}"


class RspoEntry(models.Model):
    """Minimal reference copy of the public RSPO registry (read-only in US-1.2; the CSV import
    is US-1.4). Rows are written through `services.add_rspo_entry()`, which fills the
    `*_search` columns (case-folded, so matching ignores case on SQLite and PostgreSQL)."""

    rspo_number = models.PositiveIntegerField(_("numer RSPO"), unique=True)
    name = models.CharField(_("nazwa"), max_length=300)
    institution_type = models.CharField(_("typ"), max_length=32, choices=InstitutionType.choices)
    locality = models.CharField(_("miejscowość"), max_length=100)
    voivodeship = models.CharField(_("województwo"), max_length=32, choices=Voivodeship.choices)
    name_search = models.CharField(max_length=300, editable=False)
    locality_search = models.CharField(max_length=100, editable=False)

    class Meta:
        verbose_name = _("wpis RSPO")
        verbose_name_plural = _("wpisy RSPO")
        ordering = ("name", "rspo_number")

    def __str__(self) -> str:
        return f"{self.name} ({self.locality}, RSPO {self.rspo_number})"
