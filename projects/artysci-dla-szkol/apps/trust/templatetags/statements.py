"""`{% load statements %}` · `{% artist_statement_badges artist %}`: the counted artist
statements under the label "Oświadczenie artysty" (US-8.2, D31). Shows nothing when none
counts. The wizard overview uses it now; the public profile (US-3.1) will reuse it."""

from django import template

from apps.trust import services

register = template.Library()


@register.inclusion_tag("trust/statement_badges.html")
def artist_statement_badges(artist):
    return {"statements": services.current_statements(artist) if artist is not None else []}
