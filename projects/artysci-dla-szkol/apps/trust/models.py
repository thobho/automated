"""Versioned legal documents (US-8.1, D30, D32) and users' acceptances of them.

Rows are created only by `apps.trust.services`. A published `LegalDocument` is immutable: the
model and its queryset refuse updates and deletes, so a correction is always a new version.
"""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from .errors import DocumentImmutable


class LegalDocumentQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise DocumentImmutable("published legal documents cannot be updated")

    def delete(self):
        raise DocumentImmutable("published legal documents cannot be deleted")


class LegalDocument(models.Model):
    class Kind(models.TextChoices):
        TERMS = "terms", _("Regulamin")
        PRIVACY = "privacy", _("Polityka prywatności")
        COOKIES = "cookies", _("Informacja o ciasteczkach")
        # Wordings of the artist statements (US-8.2, D104). Every new version asks for a new
        # statement; the `material` flag only matters for the terms and the privacy policy.
        CHILD_PROTECTION = "child_protection", _("Standardy ochrony małoletnich")
        MATERIAL_RIGHTS = "material_rights", _("Prawa do materiałów")
        IMAGE_ADULTS = "image_adults", _("Zgoda na wizerunek osób dorosłych")
        IMAGE_CHILDREN = "image_children", _("Zgoda na wizerunek dzieci (rodzice lub szkoła)")
        BILLING_FORM = "billing_form", _("Forma rozliczenia")
        INSURANCE = "insurance", _("Ubezpieczenie OC")

    kind = models.CharField(_("rodzaj"), max_length=20, choices=Kind.choices)
    version = models.PositiveIntegerField(_("wersja"), editable=False)
    body = models.TextField(_("treść"), help_text=_("Zwykły tekst; puste linie dzielą akapity."))
    published_at = models.DateTimeField(_("data publikacji"), editable=False)
    material = models.BooleanField(
        _("istotna zmiana"),
        default=False,
        help_text=_(
            "Zaznacz, jeśli zalogowani użytkownicy muszą ponownie zaakceptować dokument "
            "(dotyczy regulaminu i polityki prywatności)."
        ),
    )

    objects = LegalDocumentQuerySet.as_manager()

    class Meta:
        verbose_name = _("dokument prawny")
        verbose_name_plural = _("dokumenty prawne")
        ordering = ["kind", "-version"]
        constraints = [
            models.UniqueConstraint(fields=["kind", "version"], name="trust_legaldoc_kind_version"),
            models.CheckConstraint(
                condition=models.Q(version__gte=1), name="trust_legaldoc_version_positive"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.get_kind_display()} v{self.version}"

    def save(self, *args, **kwargs):
        # Integrity guard, not business logic: a stored version is never rewritten.
        if self.pk is not None and not self._state.adding:
            raise DocumentImmutable("published legal documents cannot be edited")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise DocumentImmutable("published legal documents cannot be deleted")


class LegalAcceptance(models.Model):
    """One user accepted one version. Kept as evidence (PROTECT on both sides)."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="legal_acceptances",
        verbose_name=_("użytkownik"),
    )
    document = models.ForeignKey(
        LegalDocument,
        on_delete=models.PROTECT,
        related_name="acceptances",
        verbose_name=_("dokument"),
    )
    accepted_at = models.DateTimeField(_("data akceptacji"))

    class Meta:
        verbose_name = _("akceptacja dokumentu")
        verbose_name_plural = _("akceptacje dokumentów")
        ordering = ["-accepted_at"]
        constraints = [
            models.UniqueConstraint(fields=["user", "document"], name="trust_acceptance_once"),
        ]

    def __str__(self) -> str:
        return f"{self.document} @ {self.accepted_at:%Y-%m-%d %H:%M}"


STATEMENT_KINDS: tuple[str, ...] = (
    LegalDocument.Kind.CHILD_PROTECTION,
    LegalDocument.Kind.MATERIAL_RIGHTS,
    LegalDocument.Kind.IMAGE_ADULTS,
    LegalDocument.Kind.IMAGE_CHILDREN,
    LegalDocument.Kind.BILLING_FORM,
    LegalDocument.Kind.INSURANCE,
)


class BillingForm(models.TextChoices):
    INVOICE = "faktura", _("faktura")
    BILL = "rachunek", _("rachunek")


class ArtistStatementQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise DocumentImmutable("artist statements cannot be updated")

    def delete(self):
        raise DocumentImmutable("artist statements cannot be deleted")


class ArtistStatement(models.Model):
    """One statement (or its withdrawal) of an artist about one wording version (US-8.2, D104).

    Append-only: a renewal, a change of the billing form or of the OC date and a withdrawal are
    new rows; the newest row per (artist, kind) is the artist's current position. Kept as
    evidence (PROTECT on both sides, like `LegalAcceptance`; account deletion is US-8.6).
    """

    artist = models.ForeignKey(
        "artists.Artist",
        on_delete=models.PROTECT,
        related_name="statements",
        verbose_name=_("artysta"),
    )
    kind = models.CharField(
        _("rodzaj"),
        max_length=20,
        choices=[(k, LegalDocument.Kind(k).label) for k in STATEMENT_KINDS],
    )
    document = models.ForeignKey(
        LegalDocument,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="statements",
        verbose_name=_("wersja treści"),
        help_text=_("Wersja, której dotyczy oświadczenie; przy wycofaniu: bieżąca, jeśli jest."),
    )
    made_at = models.DateTimeField(_("data"))
    withdrawn = models.BooleanField(_("wycofanie"), default=False)
    billing_form = models.CharField(
        _("forma rozliczenia"), max_length=10, choices=BillingForm.choices, blank=True
    )
    valid_until = models.DateField(_("ważne do"), null=True, blank=True)

    objects = ArtistStatementQuerySet.as_manager()

    class Meta:
        verbose_name = _("oświadczenie artysty")
        verbose_name_plural = _("oświadczenia artystów")
        ordering = ["-made_at", "-pk"]
        indexes = [
            models.Index(fields=["artist", "kind", "made_at"], name="trust_statement_latest"),
        ]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(withdrawn=True) | models.Q(document__isnull=False),
                name="trust_statement_has_document",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        kind="billing_form", withdrawn=False, billing_form__in=BillingForm.values
                    )
                    | models.Q(
                        ~models.Q(kind="billing_form") | models.Q(withdrawn=True), billing_form=""
                    )
                ),
                name="trust_statement_billing_form",
            ),
            models.CheckConstraint(
                condition=models.Q(valid_until__isnull=True)
                | models.Q(kind="insurance", withdrawn=False),
                name="trust_statement_valid_until_only_oc",
            ),
        ]

    def __str__(self) -> str:
        return f"Statement {self.pk} ({self.kind})"

    def save(self, *args, **kwargs):
        # Integrity guard, not business logic: a stored statement is never rewritten.
        if self.pk is not None and not self._state.adding:
            raise DocumentImmutable("artist statements cannot be edited")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise DocumentImmutable("artist statements cannot be deleted")


class StatementReminder(models.Model):
    """The OC expiry reminder for one statement row was queued (once per expiry, US-8.2)."""

    statement = models.OneToOneField(
        ArtistStatement,
        on_delete=models.PROTECT,
        related_name="reminder",
        verbose_name=_("oświadczenie"),
    )
    queued_at = models.DateTimeField(_("zlecono"))

    class Meta:
        verbose_name = _("przypomnienie o wygaśnięciu OC")
        verbose_name_plural = _("przypomnienia o wygaśnięciu OC")

    def __str__(self) -> str:
        return f"Reminder for statement {self.statement_id}"
