from django import template

register = template.Library()


@register.inclusion_tag('common/chosen_multiselect_apply.html')
def chosen_multiselect_apply(*selectors):
    return dict(selectors=selectors)
