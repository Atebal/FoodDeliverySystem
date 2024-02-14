from django import template

register = template.Library()

@register.filter
@register.simple_tag()
def multiply(value, arg):
    return value * arg
