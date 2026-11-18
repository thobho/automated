from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("logowanie/", views.login, name="login"),
    path("logowanie/kod/", views.login_code, name="login_code"),
    path("logowanie/link/", views.login_link, name="login_link"),
    path("wyloguj/", views.logout, name="logout"),
]
