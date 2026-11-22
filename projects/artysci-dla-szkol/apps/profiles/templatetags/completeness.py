"""`{% load completeness %}` · `{% completeness_summary artist %}`: the compact completeness
percentage with a link to the list of missing items (US-2.7), used on the wizard overview."""

from django import template

from apps.profiles import completeness

register = template.Library()


@register.inclusion_tag("profiles/_completeness_summary.html")
def completeness_summary(artist):
    if artist is None:
        return {"percent": None}
    return {
        "percent": completeness.completeness_percent(artist),
        "open": len(completeness.task_list(artist)),
    }
