from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field

update_helper = FormHelper()
update_helper.form_class = 'form-horizontal'
update_helper.label_class = 'col-lg-2'
update_helper.field_class = 'col-lg-8'
update_helper.layout = Layout(
    'name',
    'price',
    'inactive',
)
update_helper.add_input(Submit('submit', 'Submit'))
