"""`{% load institutions %}` · `{% institution_badge institution %}`: the "verified" badge
(US-1.4). Shows nothing for an unverified institution. Inquiry and notice pages use it in M2/M3."""

from django import template

from apps.institutions import services

register = template.Library()


@register.inclusion_tag("institutions/badge.html")
def institution_badge(institution):
    return {"verified": services.is_verified(institution)}
