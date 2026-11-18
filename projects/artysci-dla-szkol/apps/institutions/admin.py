from django.contrib import admin

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
    )
    list_filter = ("verification_status", "institution_type", "voivodeship")
    search_fields = ("name", "locality", "=rspo_number")
    readonly_fields = ("created_at",)
    inlines = (MemberInline,)


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
    """Read-only here: rows come from the seed now and the CSV import in US-1.4."""

    list_display = ("rspo_number", "name", "institution_type", "locality", "voivodeship")
    list_filter = ("institution_type", "voivodeship")
    search_fields = ("name", "locality", "=rspo_number")

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
