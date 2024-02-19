from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='verbose_name')
def verbose_name(obj, field_name):
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
    elif field == 'genre':
        string_rep = ', '.join([str(genre) for genre in obj.genre.all()])
    # TODO: make this list, and the one in converters.py, an application constant
    if (field in ['review', 'album', 'artist', 'label', 'user']
        and type(attr) != str):
        string_rep = f'<a href="{attr.get_absolute_url()}">{string_rep}</a>'
    return mark_safe(string_rep)
