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
        layout.Field('action'),
        bootstrap.StrictButton(_("Submit"), name='preview', css_class='btn-primary',
                               data_toggle='modal', data_target='#previewModal', css_id='preview',
                               disabled=True),
    )
    helper.form_tag = False
