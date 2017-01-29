from crispy_forms import layout, helper
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
        (InvoiceAction.PAY, _("Delete")),
    ])

    helper = helper.FormHelper()
    helper.layout = layout.Layout(
        layout.Field('action'),
        layout.Submit('submit', _("Submit"))
    )
