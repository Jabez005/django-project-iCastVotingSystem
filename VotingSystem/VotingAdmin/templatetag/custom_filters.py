from django import template
from django.template.defaultfilters import stringfilter
import json

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
@stringfilter
def get_dynamic_field(field_data, field_name):
    # Convert string representation of a dictionary back to a dictionary
    try:
        field_data = json.loads(field_data)
    except ValueError:
        # Handle the exception if the string is not a valid JSON
        return ''

    # Now we can safely use the get method since field_data is a dictionary
    return field_data.get(field_name, '')
