from django import template

register = template.Library()


@register.inclusion_tag('common/search_form.html', takes_context=True)
def search_form(context, query_field_name='q'):
    """Adds a search box form to HTML."""
    d = dict(query_field_name=query_field_name)
    value = context.request.GET.get(query_field_name)
    if value:
        d['query_field_value'] = value
    return d
