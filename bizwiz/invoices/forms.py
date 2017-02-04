from crispy_forms import layout, helper, bootstrap
from django import forms
from django.db.models import BLANK_CHOICE_DASH
from django.utils.translation import ugettext as _


class InvoiceAction:
    PAY = 'PAY'
    TAX = 'TAX'
    DELETE = 'DELETE'


class ListActionForm(forms.Form):
    action = forms.ChoiceField(choices=BLANK_CHOICE_DASH + [
        (InvoiceAction.PAY, _("Mark as paid")),
        (InvoiceAction.TAX, _("File taxes")),
        (InvoiceAction.DELETE, _("Delete")),
    ])

    helper = helper.FormHelper()
    helper.layout = layout.Layout(
        layout.Row(
            layout.Div(
                layout.Field('action'),
                css_class='col-lg-offset-8 col-lg-3'
            ),
            layout.Div(
                bootstrap.StrictButton(_("Apply"), name='preview', css_class='btn-default',
                                       data_toggle='modal', data_target='#previewModal',
                                       css_id='preview', disabled=True),
                css_class='col-lg-1'
            ),
        ),
    )
    helper.form_tag = False
    helper.form_show_labels = False
