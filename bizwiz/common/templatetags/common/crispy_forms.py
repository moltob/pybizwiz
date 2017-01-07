from django import template

register = template.Library()


@register.inclusion_tag('common/datetime_picker.html')
def datetime_picker(field):
    """Adds a search box form to HTML."""
    d = dict(picked_field=field)
    return d
