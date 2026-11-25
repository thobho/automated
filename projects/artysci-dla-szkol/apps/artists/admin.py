from django.contrib import admin

from .models import Artist, ArtistAudience, ArtistVoivodeship, Offer


class OfferInline(admin.TabularInline):
    """Read-only: offers and their poster files change only through `services` (cleanup)."""

    model = Offer
    extra = 0
    fields = ("position", "title", "price_pln", "price_on_request", "poster_key")
    readonly_fields = fields
    can_delete = False
    show_change_link = False

    def has_add_permission(self, request, obj=None):
        return False


class VoivodeshipInline(admin.TabularInline):
    model = ArtistVoivodeship
    extra = 0


class AudienceInline(admin.TabularInline):
    model = ArtistAudience
    extra = 0


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ("name", "artist_type", "city", "created_at")
    list_filter = ("artist_type",)
    search_fields = ("name", "city")
    # The publication fields change only through `profiles.publication`: an editable form would also
    # write back stale values (undo a withdrawal, free a slug).
    readonly_fields = (
        "user",
        "created_at",
        "slug",
        "publication_status",
        "published_at",
        "withdrawn_at",
    )
    inlines = (VoivodeshipInline, AudienceInline, OfferInline)
