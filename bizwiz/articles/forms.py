from crispy_forms import bootstrap
from crispy_forms import helper, layout
from django import forms
from django.utils.translation import ugettext as _

from bizwiz.articles.models import Article
from bizwiz.common.dynamic_formset import remove_form_button_factory


class UpdateForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = '__all__'

    helper = helper.FormHelper()
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-lg-2'
    helper.field_class = 'col-lg-8'
    helper.add_input(layout.Submit('submit', _("Submit")))


class CreateForm(forms.Form):
    helper = helper.FormHelper()
    helper.form_tag = False


class BaseArticleFormset(forms.BaseModelFormSet):
    helper = helper.FormHelper()
    helper.form_tag = False
    helper.disable_csrf = True
    helper.form_show_labels = False
    helper.layout = layout.Layout(
        layout.Row(
            # since a dynamic formset is used, there is no need to allow posting empty fields for
            # unused extra forms, so all fields can be explicitly required:
            layout.Div(layout.Field('name', required=''), css_class='col-lg-9'),
            layout.Div(layout.Field('price', required=''), css_class='col-lg-2', required=''),
            layout.Div(remove_form_button_factory(), css_class='col-lg-1 text-right'),
            layout.Field('DELETE', style='display:none;'),
            data_formset_form='',
        )
    )


ArticleFormset = forms.modelformset_factory(
    Article,
    formset=BaseArticleFormset,
    can_delete=True,
    fields='__all__'
)
