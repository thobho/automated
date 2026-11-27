from django import template

register = template.Library()


@register.simple_tag
def page_url(filters, number):
    """The catalog link of page `number` that keeps the current filters."""
    return filters.url(page=number)
