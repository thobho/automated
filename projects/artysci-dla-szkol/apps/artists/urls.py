from django.urls import path

from . import views

app_name = "artists"

urlpatterns = [
    path("rejestracja/artysta/", views.register, name="register"),
    path("artysta/kreator/", views.start, name="start"),
]
