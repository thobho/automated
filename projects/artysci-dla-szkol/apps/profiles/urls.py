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
    path("panel/publikacja/", views.publication_page, name="publication"),
    path("panel/publikacja/opublikuj/", views.publish, name="publish"),
    path("panel/publikacja/zmiany/", views.publish_changes, name="publish_changes"),
    path("panel/publikacja/wycofanie/", views.withdraw_confirm, name="withdraw_confirm"),
    path("panel/publikacja/wycofaj/", views.withdraw, name="withdraw"),
    path("panel/publikacja/podglad/utworz/", views.preview_link_create, name="preview_link_create"),
    path(
        "panel/publikacja/podglad/odwolaj/", views.preview_link_revoke, name="preview_link_revoke"
    ),
    # Any segment (not only a well-formed token), so a malformed one gets the same 404 page.
    path("podglad/<str:token>/", views.shared_preview, name="shared_preview"),
    path("sitemap.xml", views.sitemap, name="sitemap"),
    path("artysci/<slug:slug>/", views.public_page, name="public"),
]
