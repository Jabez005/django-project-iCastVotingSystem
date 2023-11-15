from django import template

register = template.Library()

@register.filter(name='get_field_value')
def get_attr(obj, attr_name):
    return getattr(obj, attr_name, "")