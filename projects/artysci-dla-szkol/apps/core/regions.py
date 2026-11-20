"""The 16 Polish voivodeships: the one list for every app (institutions, artists, catalog).

Moved here from `apps.institutions.models` (D102) so artists and institutions share it without
one domain app importing the other's models. Geography, not domain logic.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _


class Voivodeship(models.TextChoices):
    """The 16 Polish voivodeships (a fixed choice)."""

    DOLNOSLASKIE = "dolnoslaskie", _("dolnośląskie")
    KUJAWSKO_POMORSKIE = "kujawsko-pomorskie", _("kujawsko-pomorskie")
    LUBELSKIE = "lubelskie", _("lubelskie")
    LUBUSKIE = "lubuskie", _("lubuskie")
    LODZKIE = "lodzkie", _("łódzkie")
    MALOPOLSKIE = "malopolskie", _("małopolskie")
    MAZOWIECKIE = "mazowieckie", _("mazowieckie")
    OPOLSKIE = "opolskie", _("opolskie")
    PODKARPACKIE = "podkarpackie", _("podkarpackie")
    PODLASKIE = "podlaskie", _("podlaskie")
    POMORSKIE = "pomorskie", _("pomorskie")
    SLASKIE = "slaskie", _("śląskie")
    SWIETOKRZYSKIE = "swietokrzyskie", _("świętokrzyskie")
    WARMINSKO_MAZURSKIE = "warminsko-mazurskie", _("warmińsko-mazurskie")
    WIELKOPOLSKIE = "wielkopolskie", _("wielkopolskie")
    ZACHODNIOPOMORSKIE = "zachodniopomorskie", _("zachodniopomorskie")
