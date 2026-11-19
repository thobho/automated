from django.urls import path

from . import views

app_name = "artists"

urlpatterns = [
    path("rejestracja/artysta/", views.register, name="register"),
    path("artysta/kreator/", views.start, name="start"),
    path("artysta/profil/dane/", views.basics, name="basics"),
    path("artysta/profil/oferty/", views.offers, name="offers"),
    path("artysta/profil/oswiadczenia/", views.statements, name="statements"),
    path("artysta/profil/materialy/", views.materials, name="materials"),
]
