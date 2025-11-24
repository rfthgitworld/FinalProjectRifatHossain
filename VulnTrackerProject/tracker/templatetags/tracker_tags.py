
from django import template

register = template.Library()

@register.filter
def zip_lists(a, b):
    """Zip two lists together"""
    return zip(a, b)