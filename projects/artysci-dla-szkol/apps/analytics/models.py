from django.db import models


class Event(models.Model):
    """One business event. Written only through `services.track`; no PII."""

    name = models.CharField(max_length=64, db_index=True)
    actor = models.CharField(max_length=64, blank=True, help_text="Pseudonymous actor id (HMAC).")
    object_type = models.CharField(max_length=64, blank=True)
    object_id = models.CharField(max_length=64, blank=True)
    properties = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-created_at", "-id"]

    def __str__(self):
        return f"{self.name} #{self.pk}"


class DailySalt(models.Model):
    """Random salt for one day's visitor hashes. Rows of past days are deleted."""

    day = models.DateField(unique=True)
    salt = models.CharField(max_length=64)

    def __str__(self):
        return str(self.day)


class Visit(models.Model):
    """Page views of one anonymous visitor (daily hash) on one path and day."""

    day = models.DateField()
    path = models.CharField(max_length=200)
    visitor = models.CharField(max_length=64)
    views = models.PositiveIntegerField(default=1)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["day", "path", "visitor"], name="uniq_visit_day_path")
        ]
        indexes = [models.Index(fields=["day", "path"])]

    def __str__(self):
        return f"{self.day} {self.path}"
