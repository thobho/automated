from django.urls import path

from . import views

app_name = "profiles"

urlpatterns = [
    path("artysta/profil/generowanie/", views.generation_page, name="generation"),
    path("artysta/profil/generowanie/status/", views.generation_status, name="generation_status"),
    path("artysta/profil/generowanie/start/", views.generation_start, name="generation_start"),
    path("panel/podglad/", views.preview, name="preview"),
]
