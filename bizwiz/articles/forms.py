from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
from django.forms import modelform_factory, Form
from django.utils.translation import ugettext as _

from bizwiz.articles.models import Article

UpdateForm = modelform_factory(
    Article,
    fields='__all__',
    labels={
        'name': _("Invoice text"),
        'price': _("Unit price"),
        'inactive': _("Inactive, no longer in use"),
    },
)

UpdateForm.helper = FormHelper()
UpdateForm.helper.form_class = 'form-horizontal'
UpdateForm.helper.label_class = 'col-lg-2'
UpdateForm.helper.field_class = 'col-lg-8'
UpdateForm.helper.add_input(Submit('submit', _("Submit")))


class CreateForm(Form):
    helper = FormHelper()
    helper.add_input(Submit('submit', _("Submit")))
