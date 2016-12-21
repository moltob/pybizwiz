from crispy_forms import helper, layout
from django import forms
from django.utils.translation import ugettext as _

from bizwiz.articles.models import Article

FORM_FACTORY_OPTIONS = dict(
    fields='__all__',
    labels={
        'name': _("Invoice text"),
        'price': _("Unit price"),
        'inactive': _("Inactive, no longer in use"),
    },
)

ArticleForm = forms.modelform_factory(Article, **FORM_FACTORY_OPTIONS)


class UpdateForm(ArticleForm):
    helper = helper.FormHelper()
    helper.form_class = 'form-horizontal'
    helper.label_class = 'col-lg-2'
    helper.field_class = 'col-lg-8'
    helper.add_input(layout.Submit('submit', _("Submit")))


class CreateForm(forms.Form):
    helper = helper.FormHelper()
    helper.form_tag = False
    helper.add_input(layout.Submit('submit', _("Submit")))


class BaseArticleFormset(forms.BaseModelFormSet):
    helper = helper.FormHelper()
    helper.form_tag = False
    helper.disable_csrf = True


ArticleFormset = forms.modelformset_factory(Article,
                                            formset=BaseArticleFormset,
                                            **FORM_FACTORY_OPTIONS)
