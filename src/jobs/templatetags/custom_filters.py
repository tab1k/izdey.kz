from django import template

register = template.Library()

@register.filter
def split(value, arg):
    """Разбивает строку по указанному разделителю."""
    return value.split(arg)
