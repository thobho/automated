import json

from django import forms
from django.contrib import admin, messages
from django.contrib.admin.helpers import ActionForm
from django.utils.html import format_html_join
from django.utils.translation import gettext_lazy as _

from . import services
from .models import (
    EvaluationRun,
    Generation,
    GenerationReview,
    GeneratorComponentVersion,
    PackageEvaluation,
    ReviewQueue,
)


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


class ReviewActionForm(ActionForm):
    note = forms.CharField(label=_("Notatka (wymagana)"), required=False, max_length=2000)


@admin.register(ReviewQueue)
class ReviewQueueAdmin(ReadOnlyAdmin):
    """Generations waiting for manual review (`do przeglądu`), with the findings left after the
    repair rounds. Staff can close one as `gotowa` or `błąd` with a note (audited)."""

    list_display = ("id", "started_at", "artist", "repair_rounds", "remaining_findings", "stopped")
    list_select_related = ("artist",)
    action_form = ReviewActionForm
    actions = ["mark_ready", "mark_error"]
    fields = (
        "artist",
        "status",
        "repair_rounds",
        "remaining_findings",
        "stopped",
        "warnings_list",
        "started_at",
        "finished_at",
        "result_json",
    )
    readonly_fields = fields

    def get_queryset(self, request):
        return super().get_queryset(request).filter(status=Generation.Status.REVIEW)

    def has_review_permission(self, request):
        user = request.user
        return user.is_active and user.is_staff and user.has_perm("quality.view_reviewqueue")

    @admin.display(description=_("pozostałe naruszenia"))
    def remaining_findings(self, obj):
        hard = (obj.report or {}).get("hard", [])
        return format_html_join(
            " | ", "[{}] {}: {}", ((h["rule"], h["path"], h["message"]) for h in hard)
        )

    @admin.display(description=_("powód przerwania poprawek"))
    def stopped(self, obj):
        return ((obj.report or {}).get("repair") or {}).get("stopped") or "—"

    @admin.display(description=_("ostrzeżenia"))
    def warnings_list(self, obj):
        return "; ".join(obj.warnings) or "—"

    @admin.display(description=_("wynik"))
    def result_json(self, obj):
        return json.dumps(obj.result, ensure_ascii=False, indent=2)

    def _review(self, request, queryset, decision):
        note = (request.POST.get("note") or "").strip()
        if not note:
            self.message_user(request, _("Podaj notatkę."), level=messages.ERROR)
            return
        done = 0
        for generation in queryset:
            try:
                services.review_generation(generation, request.user, decision, note)
            except (services.GenerationError, PermissionError) as exc:
                self.message_user(request, str(exc), level=messages.ERROR)
            else:
                done += 1
        if done:
            self.message_user(request, _("Zamknięto generacji: %(n)s.") % {"n": done})

    @admin.action(description=_("Oznacz jako gotowa (z notatką)"), permissions=["review"])
    def mark_ready(self, request, queryset):
        self._review(request, queryset, GenerationReview.Decision.READY)

    @admin.action(description=_("Oznacz jako błąd (z notatką)"), permissions=["review"])
    def mark_error(self, request, queryset):
        self._review(request, queryset, GenerationReview.Decision.ERROR)


@admin.register(GenerationReview)
class GenerationReviewAdmin(ReadOnlyAdmin):
    list_display = ("created_at", "generation", "decision", "reviewer", "note")
    list_filter = ("decision",)
    readonly_fields = ("generation", "reviewer", "decision", "note", "created_at")


class EvaluationRowInline(admin.TabularInline):
    model = PackageEvaluation
    extra = 0
    can_delete = False
    fields = (
        "slug",
        "level",
        "generation_status",
        "hard_pass",
        "review_status",
        "score_wiernosc",
        "score_kompletnosc",
        "score_przydatnosc",
        "score_jezyk",
        "score_ton",
        "score_uczciwosc",
        "cost_usd",
    )
    readonly_fields = fields
    show_change_link = True

    def has_add_permission(self, request, obj=None):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(EvaluationRun)
class EvaluationRunAdmin(ReadOnlyAdmin):
    """Read-only list and detail of evaluation runs (US-11.3A)."""

    list_display = ("id", "started_at", "status", "level", "package_count", "cost_usd")
    list_filter = ("status",)
    inlines = [EvaluationRowInline]
    fields = (
        "status",
        "note",
        "level",
        "slugs",
        "started_at",
        "finished_at",
        "generator_model",
        "reviewer_model",
        "ai_client",
        "generator_components",
        "reviewer_components",
        "package_set_hash",
        "abandoned_cost_usd",
        "cost_usd",
    )
    readonly_fields = fields

    @admin.display(description=_("pakiety"))
    def package_count(self, obj):
        return f"{obj.evaluations.count()}/{len(obj.slugs)}"


@admin.register(PackageEvaluation)
class PackageEvaluationAdmin(ReadOnlyAdmin):
    list_display = (
        "id",
        "run",
        "slug",
        "level",
        "generation_status",
        "hard_pass",
        "review_status",
        "cost_usd",
    )
    list_filter = ("level", "review_status", "hard_pass")
    list_select_related = ("run",)
    fields = (
        "run",
        "slug",
        "level",
        "package_hash",
        "generation",
        "generation_status",
        "hard_pass",
        "validator_json",
        "expectations_json",
        "review_status",
        "review_reason",
        "score_wiernosc",
        "score_kompletnosc",
        "score_przydatnosc",
        "score_jezyk",
        "score_ton",
        "score_uczciwosc",
        "problems_json",
        "review_call_ids",
        "cost_usd",
        "duration_ms",
        "created_at",
    )
    readonly_fields = fields

    @staticmethod
    def _dump(value):
        return json.dumps(value, ensure_ascii=False, indent=2)

    @admin.display(description=_("wynik walidatora"))
    def validator_json(self, obj):
        return self._dump(obj.validator)

    @admin.display(description=_("oczekiwania"))
    def expectations_json(self, obj):
        return self._dump(obj.expectations)

    @admin.display(description=_("problemy"))
    def problems_json(self, obj):
        return self._dump(obj.problems)
