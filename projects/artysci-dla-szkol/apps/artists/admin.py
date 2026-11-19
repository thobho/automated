from django.contrib import admin

from .models import Artist, ArtistAudience, ArtistVoivodeship


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
    readonly_fields = ("user", "created_at")
    inlines = (VoivodeshipInline, AudienceInline)
