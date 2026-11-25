"""Generation registry (US-11.1, D13, D14): which versions produced which profile draft.

Rows are created and finished only by `apps.quality.services`. `GeneratorComponentVersion`
is never edited or deleted; a `Generation` can change only while it runs (`trwa`) and is
append-only once finished (edits and deletes are refused, like `trust.ArtistStatement`).
"""

from django.conf import settings
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
        SECTION = "section", _("regeneracja sekcji")

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
    # Validator report (US-2.5B): {"ok", "hard": [...], "soft": [...]}; None before it ran.
    report = models.JSONField(_("raport walidatora"), null=True, blank=True)
    repair_rounds = models.PositiveSmallIntegerField(_("rundy poprawek"), default=0)
    started_at = models.DateTimeField(_("rozpoczęto"))
    finished_at = models.DateTimeField(_("zakończono"), null=True, blank=True)
    duration_ms = models.PositiveIntegerField(_("czas (ms)"), null=True, blank=True)
    cost_usd = models.DecimalField(
        _("koszt (USD)"), max_digits=16, decimal_places=10, null=True, blank=True
    )

    objects = GenerationQuerySet.as_manager()
    _closing_review = False  # set only by `services.review_generation`

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
        # Integrity guard, not business logic: a finished generation is never rewritten. The one
        # exception: `services.review_generation` closes a `do przeglądu` one (sets the flag).
        if self.pk is not None and not self._state.adding:
            stored = type(self).objects.filter(pk=self.pk).values_list("status", flat=True).first()
            closing_review = self._closing_review and stored == self.Status.REVIEW
            if stored not in (None, self.Status.RUNNING) and not closing_review:
                raise RegistryImmutable("finished generations cannot be edited")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise RegistryImmutable("generations cannot be deleted")

    @property
    def finished(self) -> bool:
        return self.status != self.Status.RUNNING


class ReviewQueue(Generation):
    """Admin-only view of the generations waiting for manual review (`do przeglądu`)."""

    class Meta:
        proxy = True
        verbose_name = _("generacja do przeglądu")
        verbose_name_plural = _("generacje do przeglądu")


class GenerationReview(models.Model):
    """Audit entry: which staff user closed a `do przeglądu` generation, how, when and why.

    Written only by `services.review_generation`; never edited or deleted.
    """

    class Decision(models.TextChoices):
        READY = "ready", _("gotowa")
        ERROR = "error", _("błąd")

    generation = models.OneToOneField(
        Generation,
        on_delete=models.PROTECT,
        related_name="review",
        verbose_name=_("generacja"),
    )
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="+",
        verbose_name=_("recenzent"),
    )
    decision = models.CharField(_("decyzja"), max_length=10, choices=Decision.choices)
    note = models.TextField(_("notatka"))
    created_at = models.DateTimeField(_("kiedy"))

    class Meta:
        verbose_name = _("przegląd generacji")
        verbose_name_plural = _("przeglądy generacji")
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"Review of generation {self.generation_id}: {self.decision}"

    def save(self, *args, **kwargs):
        if self.pk is not None and not self._state.adding:
            raise RegistryImmutable("review entries cannot be edited")
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise RegistryImmutable("review entries cannot be deleted")


class TestsetLoad(models.Model):
    """Which version (digest of the package JSON) of a test-set package is loaded for its
    synthetic artist (US-11.2). Written only by `apps.quality.testset.load_package`; lets a
    repeated load of an unchanged package change nothing."""

    __test__ = False  # not a pytest class

    slug = models.SlugField(_("pakiet"), max_length=80, unique=True)
    artist = models.OneToOneField(
        "artists.Artist", on_delete=models.CASCADE, related_name="testset_load"
    )
    digest = models.CharField(_("odcisk pakietu"), max_length=64)
    loaded_at = models.DateTimeField(_("załadowano"))

    class Meta:
        verbose_name = _("załadowany pakiet testowy")
        verbose_name_plural = _("załadowane pakiety testowe")

    def __str__(self) -> str:
        return f"Test set package {self.slug}"
