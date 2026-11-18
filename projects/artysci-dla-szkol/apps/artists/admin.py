from django.contrib import admin

from .models import Artist


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    search_fields = ("name",)
    readonly_fields = ("user", "created_at")
