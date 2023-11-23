from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def get_field_value(data_row, field_name):
    # Assuming data_row is a dictionary with field names as keys
    return data_row.get(field_name, '')