from django.urls import path

from . import views

app_name = "catalog"

urlpatterns = [
    path("artysci/", views.catalog_list, name="list"),
]
