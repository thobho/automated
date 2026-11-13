from django.db import models


class PingRecord(models.Model):
    """Row written by the demo `ping` job; used by tests and the smoke check."""

    token = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return self.token
