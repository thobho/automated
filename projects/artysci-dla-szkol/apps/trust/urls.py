from django.urls import path

from . import views
from .models import LegalDocument

app_name = "trust"

urlpatterns = [
    path("regulamin/", views.document, {"kind": LegalDocument.Kind.TERMS}, name="terms"),
    path(
        "polityka-prywatnosci/",
        views.document,
        {"kind": LegalDocument.Kind.PRIVACY},
        name="privacy",
    ),
    path("ciasteczka/", views.document, {"kind": LegalDocument.Kind.COOKIES}, name="cookies"),
    path("akceptacja-dokumentow/", views.accept, name="accept"),
]
