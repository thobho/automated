from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("logowanie/", views.login, name="login"),
    path("logowanie/kod/", views.login_code, name="login_code"),
    path("logowanie/link/", views.login_link, name="login_link"),
    path("wyloguj/", views.logout, name="logout"),
    path("konto/", views.account_settings, name="settings"),
    path("konto/email/", views.email_change, name="email_change"),
    path("konto/email/kod/", views.email_change_code, name="email_change_code"),
    path("konto/email/link/", views.email_change_link, name="email_change_link"),
    path("konto/dane/", views.data_export, name="data_export"),
    path("konto/usun/", views.delete_account, name="delete_account"),
]
