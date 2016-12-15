"""Crispy helpers for athentication forms."""
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Div
from django.utils.translation import ugettext as _

login_helper = FormHelper()
login_helper.layout = Layout(
    Row(
        Div('username', css_class='col-lg-offset-4 col-lg-4')
    ),
    Row(
        Div('password', css_class='col-lg-offset-4 col-lg-4')
    ),
    Row(
        Div(
            # Translators: This is the button text.
            Submit('submit', _('Login'), css_class='btn-block'),
            css_class='col-lg-offset-4 col-lg-4'
        )
    ),
)
