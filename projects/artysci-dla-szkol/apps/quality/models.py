"""Generation registry (US-11.1, D13, D14): which versions produced which profile draft.

Rows are created and finished only by `apps.quality.services`. `GeneratorComponentVersion`
is never edited or deleted; a `Generation` can change only while it runs (`trwa`) and is
append-only once finished (edits and deletes are refused, like `trust.ArtistStatement`).
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from .registry import KINDS


class RegistryImmutable(Exception):
    """A stored component version or a finished generation cannot change."""


class ComponentVersionQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise RegistryImmutable("component versions cannot be updated")

    def delete(self):
        raise RegistryImmutable("component versions cannot be deleted")


class GeneratorComponentVersion(models.Model):
    """One version of one generator component, deduplicated by its content hash.

    `content` is a full snapshot for the text kinds (instructions, schema); for code kinds
    (validator, template) declared by files it is empty and `files` + `content_hash` identify
    the code in git (a code kind declared with inline content keeps that content).
    """

    kind = models.CharField(_("rodzaj"), max_length=20, choices=[(k, k) for k in KINDS])
    name = models.CharField(_("nazwa"), max_length=100)
    version = models.CharField(_("wersja"), max_length=50)
    content_hash = models.CharField(_("skrót treści (SHA-256)"), max_length=64)
    content = models.TextField(_("treść"), blank=True)
    files = models.JSONField(_("pliki"), default=list, blank=True)
    created_at = models.DateTimeField(_("zarejestrowano"))

    objects = ComponentVersionQuerySet.as_manager()

    class Meta:
        verbose_name = _("wersja komponentu generatora")
        verbose_name_plural = _("wersje komponentów generatora")
        ordering = ["kind", "name", "-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["kind", "name", "content_hash"], name="quality_component_hash_once"
            ),
            models.UniqueConstraint(
                fields=["kind", "name", "version"], name="quality_component_version_once"
            ),
        ]

    def __str__(self) -> str:
        return f"{self.kind}:{self.name} v{self.version}"

    def save(self, *args, **kwargs):
        # Integrity guard, not business logic: a stored version is never rewritten.
        if self.pk is not None and not self._state.adding:
            raise RegistryImmutable("component versions cannot be edited")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise RegistryImmutable("component versions cannot be deleted")


class GenerationQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise RegistryImmutable("generations cannot be updated in bulk")

    def delete(self):
        raise RegistryImmutable("generations cannot be deleted")


class Generation(models.Model):
    """One run of the profile generator for one artist.

    `input_fingerprint` is SHA-256 over the ready materials (ids and content hashes) and the
    questionnaire values (D107): a fingerprint, never a copy of the materials. `cost_usd` is
    the sum of the linked `profiles.AICall` rows, fixed when the run finishes; no prompt or
    reply text is stored here or there.
    """

    class Trigger(models.TextChoices):
        IMPORT = "import", _("import")
        QUESTIONNAIRE = "questionnaire", _("ankieta")
        MANUAL = "manual", _("ręcznie")
        RERUN = "rerun", _("ponowne uruchomienie")

    class Status(models.TextChoices):
        RUNNING = "running", _("trwa")
        READY = "ready", _("gotowa")
        REVIEW = "review", _("do przeglądu")
        ERROR = "error", _("błąd")

    artist = models.ForeignKey(
        "artists.Artist",
        on_delete=models.PROTECT,
        related_name="generations",
        verbose_name=_("artysta"),
    )
    trigger = models.CharField(_("wyzwalacz"), max_length=20, choices=Trigger.choices)
    components = models.ManyToManyField(
        GeneratorComponentVersion,
        related_name="generations",
        verbose_name=_("wersje komponentów"),
    )
    ai_model = models.CharField(_("model AI"), max_length=500, blank=True)
    input_fingerprint = models.CharField(_("odcisk danych wejściowych"), max_length=64)
    status = models.CharField(
        _("status"), max_length=10, choices=Status.choices, default=Status.RUNNING
    )
    result = models.JSONField(_("wynik"), null=True, blank=True)
    warnings = models.JSONField(_("ostrzeżenia"), default=list, blank=True)
    repair_rounds = models.PositiveSmallIntegerField(_("rundy poprawek"), default=0)
    started_at = models.DateTimeField(_("rozpoczęto"))
    finished_at = models.DateTimeField(_("zakończono"), null=True, blank=True)
    duration_ms = models.PositiveIntegerField(_("czas (ms)"), null=True, blank=True)
    cost_usd = models.DecimalField(
        _("koszt (USD)"), max_digits=16, decimal_places=10, null=True, blank=True
    )

    objects = GenerationQuerySet.as_manager()

    class Meta:
        verbose_name = _("generacja profilu")
        verbose_name_plural = _("generacje profili")
        ordering = ["-started_at", "-pk"]
        indexes = [models.Index(fields=["artist", "-started_at"], name="quality_gen_artist")]
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(status="running", finished_at__isnull=True)
                    | (~models.Q(status="running") & models.Q(finished_at__isnull=False))
                ),
                name="quality_generation_finished_iff_not_running",
            ),
        ]

    def __str__(self) -> str:
        return f"Generation {self.pk} ({self.status})"

    def save(self, *args, **kwargs):
        # Integrity guard, not business logic: a finished generation is never rewritten.
        if self.pk is not None and not self._state.adding:
            stored = type(self).objects.filter(pk=self.pk).values_list("status", flat=True)
            if stored.first() not in (None, self.Status.RUNNING):
                raise RegistryImmutable("finished generations cannot be edited")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise RegistryImmutable("generations cannot be deleted")

    @property
    def finished(self) -> bool:
        return self.status != self.Status.RUNNING
