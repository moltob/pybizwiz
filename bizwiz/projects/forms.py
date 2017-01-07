from crispy_forms import layout, helper
from django import forms
from django.utils.translation import ugettext as _

from bizwiz.common.crispy_forms import PickableDateField
from bizwiz.projects.models import Project


class UpdateForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = '__all__'

    helper = helper.FormHelper()
    helper.layout = layout.Layout(
        layout.Row(
            layout.Div('name', css_class='col-lg-6'),
            layout.Div(PickableDateField('start_date'), css_class='col-lg-2'),
        ),
        layout.Row(
            layout.Div(layout.Submit('submit', _("Submit")), css_class='col-lg-1')
        ),
    )
