from crispy_forms import helper, layout
from django import forms
from django.utils.translation import ugettext as _

from bizwiz.customers.models import Customer

CostumerForm = forms.modelform_factory(Customer, fields='__all__')


class UpdateForm(CostumerForm):
    helper = helper.FormHelper()
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-lg-2'
    helper.field_class = 'col-lg-8'
    helper.add_input(layout.Submit('submit', _("Submit")))
