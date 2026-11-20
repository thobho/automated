from django.contrib import admin, messages
from django.utils.translation import gettext_lazy as _
from django.utils.translation import ngettext

from . import services
from .models import Institution, InstitutionMember, RspoEntry


class MemberInline(admin.TabularInline):
    model = InstitutionMember
    fields = ("user", "function", "needs_review", "created_at")
    readonly_fields = ("user", "function", "created_at")
    extra = 0
    can_delete = False


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "institution_type",
        "locality",
        "voivodeship",
        "rspo_number",
        "verification_status",
        "verification_method",
        "verified_at",
    )
    list_filter = ("verification_status", "verification_method", "institution_type", "voivodeship")
    search_fields = ("name", "locality", "=rspo_number")
    # Verification changes only through the action below (it records the event once).
    readonly_fields = (
        "verification_status",
        "verification_method",
        "verified_at",
        "verified_by",
        "created_at",
    )
    inlines = (MemberInline,)
    actions = ("approve",)

    @admin.action(description=_("Zatwierdź placówkę"), permissions=("change",))
    def approve(self, request, queryset):
        """Manual verification (US-1.4); already verified institutions are left as they are."""
        count = services.approve(queryset, by=request.user)
        self.message_user(
            request,
            ngettext(
                "Zatwierdzono %(count)d placówkę.",
                "Zatwierdzono %(count)d placówek.",
                count,
            )
            % {"count": count},
            messages.SUCCESS,
        )


@admin.register(InstitutionMember)
class InstitutionMemberAdmin(admin.ModelAdmin):
    """US-1.2: accounts that joined an institution that already had one show under the
    `needs_review` filter (the admin panel and e-mail notice are E9, US-9.5)."""

    list_display = ("__str__", "institution", "function", "needs_review", "created_at")
    list_filter = ("needs_review", "function")
    list_select_related = ("institution",)
    readonly_fields = ("user", "institution", "function", "created_at")
    search_fields = ("institution__name", "=institution__rspo_number")


@admin.register(RspoEntry)
class RspoEntryAdmin(admin.ModelAdmin):
    """Read-only here: rows come from `manage.py import_rspo` (US-1.4) and the seed."""

    list_display = (
        "rspo_number",
        "name",
        "institution_type",
        "locality",
        "voivodeship",
        "email_domain",
    )
    list_filter = ("institution_type", "voivodeship")
    search_fields = ("name", "locality", "=rspo_number")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
