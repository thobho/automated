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
