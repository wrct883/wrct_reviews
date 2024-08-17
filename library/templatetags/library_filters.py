from django import template
from django.utils.safestring import mark_safe

from datetime import datetime, date

register = template.Library()

@register.filter(name='anize')
def anize(word):
    vowels = 'aeiou'
    if word[0].lower() in vowels:
        return f'an {word}'
    else:
        return f'a {word}'

@register.filter(name='parse_array')
def parse_array(arr):
    if isinstance(arr, str):
        return arr.split()
    return arr if arr else []

@register.filter(name='verbose_name')
def verbose_name(obj, field_name):
    if not obj:
        return ''
    field = obj._meta.get_field(field_name)
    return field.verbose_name

@register.filter(name='lookup')
def lookup(obj, field):
    # TODO: I shouldn't have to do these if/else statements
    # this is so busted
    attr = getattr(obj, field)
    string_rep = str(attr) if attr else ''
    if field == 'format':
        string_rep = obj.get_format_display()
    elif field == 'status':
        string_rep = obj.get_status_display()
    elif field == 'subgenre':
        string_rep = ', '.join([str(sgenre) for sgenre in obj.subgenre.all()])
    elif isinstance(attr, date) or isinstance(attr, datetime):
        string_rep = attr.strftime("%Y-%m-%d")
    # TODO: make this list, and the one in converters.py, an application constant
    if (field in ['review', 'album', 'artist', 'label', 'user']
        and type(attr) != str and attr is not None):
        string_rep = f'<a href="{attr.get_absolute_url()}">{string_rep}</a>'
    elif (field.lower() != "review" and field.lower() == obj._meta.model_name and type(attr) == str and attr is not None):
        string_rep = f'<a href="{obj.get_absolute_url()}">{string_rep}</a>'

    string_rep = string_rep if string_rep else ''
    return mark_safe(string_rep)
