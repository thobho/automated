from django.urls import path

from . import views

app_name = "notices"

urlpatterns = [
    path("ogloszenia/nowe/", views.new_notice, name="new"),
]
