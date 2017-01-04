from crispy_forms import helper, layout
from django import forms
from django.utils.translation import ugettext as _

from bizwiz.customers.models import Customer

CostumerForm = forms.modelform_factory(Customer, fields='__all__')


class UpdateForm(CostumerForm):
    helper = helper.FormHelper()
    #helper.form_class = 'form-horizontal'
    #helper.label_class = 'col-lg-2'
    #helper.field_class = 'col-lg-8'
    helper.layout = layout.Layout(
        layout.Row(
            layout.Div('salutation', css_class='col-lg-3'),
            layout.Div('title', css_class='col-lg-3'),
        ),
        layout.Row(
            layout.Div('first_name', css_class='col-lg-6'),
            layout.Div('last_name', css_class='col-lg-6'),
        ),
        layout.Row(
            layout.Div('company_name', css_class='col-lg-6'),
        ),
        layout.Fieldset(
            _("Address"),
            layout.Row(
                layout.Div('street_address', css_class='col-lg-6'),
            ),
            layout.Row(
                layout.Div('zip_code', css_class='col-lg-2'),
                layout.Div('city', css_class='col-lg-4'),
            ),
        ),
        layout.Fieldset(
            _("Contact data"),
            layout.Row(
                layout.Div('phone_number', css_class='col-lg-4'),
                layout.Div('mobile_number', css_class='col-lg-4'),
                layout.Div('email', css_class='col-lg-4'),
            ),
        ),
        layout.Fieldset(
            _("Additional"),
            layout.Row(
                layout.Div('notes', css_class='col-lg-12'),
            ),
        ),
    )
    helper.add_input(layout.Submit('submit', _("Submit")))
