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
    path("artysta/profil/materialy/", views.materials_page, name="materials"),
    path(
        "artysta/profil/materialy/zdjecia/",
        views.materials_upload,
        {"kind": "photo"},
        name="materials_photos",
    ),
    path(
        "artysta/profil/materialy/pdf/",
        views.materials_upload,
        {"kind": "pdf"},
        name="materials_pdfs",
    ),
    path("artysta/profil/materialy/film/", views.materials_link, name="materials_link"),
    path(
        "artysta/profil/materialy/<int:material_id>/usun/",
        views.material_delete,
        name="material_delete",
    ),
    path("artysta/profil/kwestionariusz/", views.questionnaire, name="questionnaire"),
    path("artysta/profil/import/", views.website_import_view, name="website_import"),
    path(
        "artysta/profil/import/<int:import_id>/",
        views.website_import_status,
        name="website_import_status",
    ),
]
