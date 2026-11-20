import json

from django.contrib import admin
from django.utils.html import format_html_join
from django.utils.translation import gettext_lazy as _

from . import services
from .models import Generation, GeneratorComponentVersion


class ReadOnlyAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Generation)
class GenerationAdmin(ReadOnlyAdmin):
    """Read-only audit of profile generations (US-11.1)."""

    list_display = (
        "id",
        "started_at",
        "artist",
        "trigger",
        "status",
        "ai_model",
        "repair_rounds",
        "duration_ms",
        "cost_usd",
    )
    list_filter = ("status", "trigger")
    date_hierarchy = "started_at"
    list_select_related = ("artist",)
    fields = (
        "artist",
        "trigger",
        "status",
        "ai_model",
        "component_versions",
        "input_fingerprint",
        "warnings_list",
        "repair_rounds",
        "started_at",
        "finished_at",
        "duration_ms",
        "cost_usd",
        "result_json",
    )
    readonly_fields = fields

    @admin.display(description=_("wersje komponentów"))
    def component_versions(self, obj):
        return format_html_join(
            ", ",
            "{}:{} v{} ({})",
            (
                (v["kind"], v["name"], v["version"], v["content_hash"][:12])
                for v in services.versions_of(obj)
            ),
        )

    @admin.display(description=_("ostrzeżenia"))
    def warnings_list(self, obj):
        return "; ".join(obj.warnings) or "—"

    @admin.display(description=_("wynik"))
    def result_json(self, obj):
        return json.dumps(obj.result, ensure_ascii=False, indent=2)


@admin.register(GeneratorComponentVersion)
class GeneratorComponentVersionAdmin(ReadOnlyAdmin):
    list_display = ("kind", "name", "version", "content_hash", "created_at")
    list_filter = ("kind", "name")
    readonly_fields = ("kind", "name", "version", "content_hash", "files", "content", "created_at")
