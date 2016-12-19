from django import template

register = template.Library()


@register.inclusion_tag('common/ordering_link.html')
def ordering_link(link_text, field_name, order_by, order_dir):
    return dict(link_text=link_text, field_name=field_name, order_by=order_by, order_dir=order_dir)
