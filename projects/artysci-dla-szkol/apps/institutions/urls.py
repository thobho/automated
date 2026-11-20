from django.urls import path

from . import views

app_name = "institutions"

urlpatterns = [
    path("rejestracja/placowka/", views.register, name="register"),
    path("rejestracja/placowka/rspo/", views.rspo_suggestions, name="rspo_suggestions"),
    path("placowka/", views.start, name="start"),
]
