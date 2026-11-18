"""Django admin for legal documents: staff publish new versions; published ones are view-only."""

from django.contrib import admin

from . import services
from .models import LegalAcceptance, LegalDocument


@admin.register(LegalDocument)
class LegalDocumentAdmin(admin.ModelAdmin):
    list_display = ("kind", "version", "published_at", "material")
    list_filter = ("kind", "material")
    fields = ("kind", "body", "material")
    actions = None

    def get_fields(self, request, obj=None):
        if obj is None:
            return self.fields
        return ("kind", "version", "published_at", "material", "body")

    def get_readonly_fields(self, request, obj=None):
        return self.get_fields(request, obj) if obj is not None else ()

    def has_change_permission(self, request, obj=None):
        return False  # a correction is a new version (add)

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        if change:  # unreachable while has_change_permission is False; belt and braces
            raise PermissionError("published legal documents cannot be edited")
        document = services.publish(
            form.cleaned_data["kind"], form.cleaned_data["body"], form.cleaned_data["material"]
        )
        # The admin logs and redirects using `obj`; point it at the stored row.
        obj.pk, obj.version, obj.published_at = document.pk, document.version, document.published_at
        obj.material, obj.body = document.material, document.body
        obj._state.adding = False
        obj._state.db = document._state.db


@admin.register(LegalAcceptance)
class LegalAcceptanceAdmin(admin.ModelAdmin):
    list_display = ("user", "document", "accepted_at")
    list_filter = ("document__kind",)
    list_select_related = ("user", "document")
    actions = None

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
