import json
from django import template

register = template.Library()


@register.filter
def pretty_json(value):
    return json.dumps(value, indent=4)


@register.filter(name="get_key_value")
def get_key_value(some_dict, key):
    return some_dict.get(key, '')
