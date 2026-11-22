from django.urls import path

from . import views

app_name = "profiles"

urlpatterns = [
    path("artysta/profil/generowanie/", views.generation_page, name="generation"),
    path("artysta/profil/generowanie/status/", views.generation_status, name="generation_status"),
    path("artysta/profil/generowanie/start/", views.generation_start, name="generation_start"),
    path("artysta/profil/braki/", views.gaps, name="gaps"),
    path("panel/podglad/", views.preview, name="preview"),
    path("panel/podglad/motyw/", views.theme, name="theme"),
    path("panel/podglad/edycja/", views.edit_field, name="edit_field"),
    path("panel/podglad/odblokuj/", views.unlock_field, name="unlock_field"),
    path("panel/podglad/sekcja/", views.regenerate_section, name="regenerate_section"),
    path("panel/podglad/sekcja/status/", views.section_status, name="section_status"),
    path("panel/podglad/przywroc/", views.restore_version, name="restore_version"),
]
