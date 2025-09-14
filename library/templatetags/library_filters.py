from django import template
from django.utils.safestring import mark_safe
from django.utils.html import escape as escape_html
from datetime import datetime, date
import re

register = template.Library()

@register.filter(name='anize')
def anize(word):
    vowels = 'aeiou'
    if word[0].lower() in vowels:
        return f'an {word}'
    else:
        return f'a {word}'

@register.filter(name='otherwise')
def otherwise(value, alternative):
    return value if value else alternative

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
    return obj.get(field, "") if obj else ""

@register.simple_tag(takes_context=True)
def formatted_attribute(context, obj, field):
    attr = getattr(obj, field)
    if not attr:
        return ""
    if field == 'format':
        string_rep = obj.get_format_display()
    elif field == 'status':
        string_rep = obj.get_status_display()
    elif field == 'subgenre' and not isinstance(attr, str):
        string_rep = ', '.join([str(sgenre) for sgenre in obj.subgenre.all()])
    elif isinstance(attr, date) or isinstance(attr, datetime):
        string_rep = attr.strftime("%Y-%m-%d")
    else:
        string_rep = str(attr)
    string_rep = escape_html(string_rep)

    # Highlight the search term if one is present in the context
    if (form := context.get('form')) \
        and (query := form.cleaned_data.get('query')) \
        and (pos := form.cleaned_data.get('pos')):
        escaped_query = escape_html(query)
        if pos == 'icontains':
            regex = re.compile(escaped_query, re.IGNORECASE)
        elif pos == 'istartswith':
            regex = re.compile(r"^(?:<.+?>)?(" + re.escape(escaped_query) + ")", re.IGNORECASE)
        elif pos == 'iendswith':
            regex = re.compile(r"(" + re.escape(escaped_query) + ")(?:<.+?>)?$", re.IGNORECASE)
        elif pos == 'iexact':
            regex = re.compile(r"^(?:<.+?>)?(" + re.escape(escaped_query) + ")(?:<.+?>)?$", re.IGNORECASE)
        string_rep = regex.sub(r'<b>\g<0></b>', string_rep)

    # Linkify if applicable
    # TODO: make this list, and the one in converters.py, an application constant
    if (field in ['review', 'album', 'artist', 'label', 'user']
        and type(attr) != str and attr is not None):
        string_rep = f'<a href="{attr.get_absolute_url()}">{string_rep}</a>'
    elif ((field.lower() != "review" and field.lower() == obj._meta.model_name and
           type(attr) == str and attr is not None)
          or field == 'username'):
        string_rep = f'<a href="{obj.get_absolute_url()}">{string_rep}</a>'

    string_rep = string_rep if string_rep else ''

    return mark_safe(string_rep)

@register.filter(name='in')
def filter_in(obj, arr):
    return obj in arr
