from django import template

register = template.Library()


@register.inclusion_tag('common/dynamic_formset_begin.html')
def dynformset(css_id, formset):
    return dict(css_id=css_id, formset=formset)


@register.inclusion_tag('common/dynamic_formset_body.html')
def dynformset_body(formset):
    return dict(formset=formset)


@register.inclusion_tag('common/dynamic_formset_add_button.html')
def dynformset_add_button(col_offset=11):
    return dict(col_offset=col_offset)


@register.inclusion_tag('common/dynamic_formset_end.html')
def enddynformset():
    return {}


@register.inclusion_tag('common/dynamic_formset_apply.html')
def dynformset_apply(selector):
    return dict(selector=selector)
