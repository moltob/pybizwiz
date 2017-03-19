from crispy_forms import helper, layout
from django import forms

from bizwiz.common.dynamic_formset import remove_form_button_factory
from bizwiz.rebates.models import Rebate


class RebateForm(forms.ModelForm):
    # prevent use of number inputs which feature the undesired +/- buttons:
    value = forms.DecimalField(
        widget=forms.TextInput,
        decimal_places=2,
        localize=True,
        label=Rebate._meta.get_field('value').verbose_name
    )


class BaseRebateFormset(forms.BaseModelFormSet):
    helper = helper.FormHelper()
    helper.form_tag = False
    helper.form_show_labels = False
    helper.layout = layout.Layout(
        layout.Row(
            # since a dynamic formset is used, there is no need to allow posting empty fields for
            # unused extra forms, so all fields can be explicitly required:
            layout.Div(layout.Field('kind', required=''), css_class='col-lg-3'),
            layout.Div(layout.Field('name', required=''), css_class='col-lg-6'),
            layout.Div(
                layout.Field('value', required='', css_class='text-right'),
                css_class='col-lg-1'
            ),
            layout.Div(
                layout.Field('auto_apply', style='margin:0;'),
                css_class='col-lg-1'
            ),
            layout.Div(remove_form_button_factory(), css_class='col-lg-1 text-right'),
            layout.Field('DELETE', style='display:none;'),
            data_formset_form='',
        )
    )


RebateFormset = forms.modelformset_factory(
    Rebate,
    formset=BaseRebateFormset,
    form=RebateForm,
    can_delete=True,
    fields='__all__',
    extra=0,
)
