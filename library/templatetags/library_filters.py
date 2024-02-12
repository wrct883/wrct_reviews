from django import template

register = template.Library()

@register.filter(name='lookup')
def lookup(obj, field):
    # TODO: I shouldn't have to do these if/else statements
    # this is so busted
    if field == 'format':
        return obj.get_format_display()
    elif field == 'status':
        return obj.get_status_display()
    elif field == 'genre':
        return obj.genre.all().first()
    attr = getattr(obj, field)
    return attr if attr else ''
