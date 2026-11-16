from django.contrib import admin

from .models import AICall


@admin.register(AICall)
class AICallAdmin(admin.ModelAdmin):
    """Read-only audit of AI calls and their cost."""

    list_display = ("created_at", "purpose", "model", "provider", "status", "cost_usd")
    list_filter = ("status", "purpose", "client")
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
