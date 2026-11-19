from django.urls import path

from . import views

app_name = "artists"

urlpatterns = [
    path("rejestracja/artysta/", views.register, name="register"),
    path("artysta/kreator/", views.start, name="start"),
    path("artysta/profil/dane/", views.basics, name="basics"),
    path("artysta/profil/oferty/", views.offers, name="offers"),
    path("artysta/profil/oferty/nowa/", views.offer_add, name="offer_add"),
    path("artysta/profil/oferty/<int:offer_id>/edycja/", views.offer_edit, name="offer_edit"),
    path("artysta/profil/oferty/<int:offer_id>/usun/", views.offer_delete, name="offer_delete"),
    path("artysta/profil/oferty/<int:offer_id>/przesun/", views.offer_move, name="offer_move"),
    path("artysta/profil/oswiadczenia/", views.statements, name="statements"),
    path("artysta/profil/materialy/", views.materials, name="materials"),
]
