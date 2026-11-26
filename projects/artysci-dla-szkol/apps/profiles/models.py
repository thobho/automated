from django.db import models
from django.utils.translation import gettext_lazy as _


class PageVersion(models.Model):
    """One saved state of an artist's page texts (US-2.6). The newest version is the current one.

    `content` holds only the artist-editable texts (tagline, facts, about, for_schools, faq);
    photos, videos and offers always come live from the artist's data. `locks` lists the field
    paths the artist edited ("about", "facts.0", "faq.1.answer"): regeneration keeps them.
    At most 10 versions per artist are kept (see `pages.py`).
    """

    class Source(models.TextChoices):
        GENERATED = "generated", _("wygenerowana")
        EDITED = "edited", _("edytowana")
        REGENERATED = "regenerated", _("sekcja wygenerowana ponownie")
        RESTORED = "restored", _("przywrócona")

    artist = models.ForeignKey("artists.Artist", on_delete=models.CASCADE, related_name="versions")
    number = models.PositiveIntegerField()
    source = models.CharField(max_length=12, choices=Source.choices)
    content = models.JSONField(default=dict)
    locks = models.JSONField(default=list, blank=True)
    # The registry row of the AI run this version came from (generated, regenerated).
    generation = models.ForeignKey(
        "quality.Generation", on_delete=models.PROTECT, null=True, blank=True, related_name="+"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-number"]
        constraints = [
            models.UniqueConstraint(fields=["artist", "number"], name="profiles_version_number")
        ]

    def __str__(self):
        return f"{self.artist_id} v{self.number} {self.source}"


class PublishedPage(models.Model):
    """The copy of the page the public sees (US-2.8): written only by publishing, so later edits
    change nothing public until "Opublikuj zmiany". `content` holds the texts of the version,
    `data` the rest (`content.page_data`: name, city, offers and the ids of the materials shown)."""

    artist = models.OneToOneField(
        "artists.Artist", on_delete=models.CASCADE, related_name="published_page"
    )
    content = models.JSONField(default=dict)
    data = models.JSONField()
    theme = models.CharField(max_length=32, blank=True)
    # The PageVersion.number this copy was taken from (for "there are unpublished changes").
    version_number = models.PositiveIntegerField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.artist_id} published v{self.version_number}"


class PreviewLink(models.Model):
    """A private link to the artist's preview (US-3.7). Only the SHA-256 of the token is stored;
    the token itself is shown once, at creation (`previews.py`)."""

    artist = models.ForeignKey(
        "artists.Artist", on_delete=models.CASCADE, related_name="preview_links"
    )
    token_hash = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField()
    expires_at = models.DateTimeField()
    revoked_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["artist", "expires_at"], name="profiles_prevlink_artist")]

    def __str__(self):
        return f"{self.artist_id} preview until {self.expires_at:%Y-%m-%d}"


class AICall(models.Model):
    """One request sent to an AI provider (apps/profiles/ai). Never stores prompt or reply text.

    The daily cost cap sums `cost_usd` of today's rows. A row is created as `pending` with the
    call's worst-case cost before the request is sent (a reservation), then settled with the
    real `usage.cost`. Failed requests keep a row too (a provider may bill them).
    """

    class Status(models.TextChoices):
        PENDING = "pending", "pending"
        OK = "ok", "ok"
        ERROR = "error", "error"

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    client = models.CharField(max_length=20)  # "openrouter" or "fake"
    purpose = models.CharField(max_length=50)
    model = models.CharField(max_length=200)
    provider = models.CharField(max_length=100, blank=True)
    generation_id = models.CharField(max_length=200, blank=True)  # provider's response id
    status = models.CharField(max_length=10, choices=Status.choices)
    error = models.CharField(max_length=200, blank=True)  # short code, no prompt text
    prompt_tokens = models.PositiveIntegerField(default=0)
    completion_tokens = models.PositiveIntegerField(default=0)
    cost_usd = models.DecimalField(max_digits=16, decimal_places=10, default=0)
    latency_ms = models.PositiveIntegerField(default=0)
    # The profile generation this call belongs to (US-11.1), set by the caller through
    # `complete(..., generation=)` or `quality.services.record_ai_call()`.
    profile_generation = models.ForeignKey(
        "quality.Generation",
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="ai_calls",
    )

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.purpose} {self.model} {self.cost_usd}"
