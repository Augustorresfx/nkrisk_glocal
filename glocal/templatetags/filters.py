from django import template

register = template.Library()

@register.filter
def is_boolean(value):
    return isinstance(value, bool)

@register.filter
def boolean_to_text(value):
    if value is True:
        return "Sí"
    elif value is False:
        return "No"
    return value