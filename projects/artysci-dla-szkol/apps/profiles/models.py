from django.db import models


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

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"{self.purpose} {self.model} {self.cost_usd}"
