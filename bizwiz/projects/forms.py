from crispy_forms import layout, helper
from django import forms
from django.utils.translation import ugettext as _

from bizwiz.common.crispy_forms import PickableDateField
from bizwiz.common.dynamic_formset import remove_form_button_factory
from bizwiz.projects.models import Project, CustomerGroup


class UpdateForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = '__all__'

    # form requires assets from custom date picker field:
    Media = PickableDateField.Media

    helper = helper.FormHelper()
    helper.form_tag = False
    helper.layout = layout.Layout(
        layout.Row(
            layout.Div('name', css_class='col-lg-7'),
            layout.Div(PickableDateField('start_date'), css_class='col-lg-2'),
        ),
    )


class BaseCustomerGroupFormset(forms.BaseInlineFormSet):
    helper = helper.FormHelper()
    helper.form_tag = False
    helper.disable_csrf = True
    helper.form_show_labels = False
    helper.layout = layout.Layout(
        layout.Row(
            # since a dynamic formset is used, there is no need to allow posting empty fields for
            # unused extra forms, so all fields can be explicitly required:
            layout.Div(layout.Field('name', required=''), css_class='col-lg-8'),
            layout.Div(remove_form_button_factory(), css_class='col-lg-1 text-right'),
            layout.Field('DELETE', style='display:none;'),
            data_formset_form='',
        )
    )


CustomerGroupFormset = forms.inlineformset_factory(
    Project,
    CustomerGroup,
    formset=BaseCustomerGroupFormset,
    can_delete=True,
    extra=0,
    fields=('name',)
)
