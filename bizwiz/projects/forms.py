from crispy_forms import layout, helper
from django import forms
from django.utils.translation import ugettext as _

from bizwiz.articles.models import Article
from bizwiz.common.crispy_forms import PickableDateField
from bizwiz.common.dynamic_formset import remove_form_button_factory
from bizwiz.common.selectize import ModelMultipleChoiceTextField
from bizwiz.customers.models import Customer
from bizwiz.projects.models import Project, CustomerGroup


class UpdateForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = '__all__'

    articles = ModelMultipleChoiceTextField(queryset=Article.objects.all().order_by('name'),
                                            label=_("Article set"))

    # form required assets:
    Media = PickableDateField.Media

    helper = helper.FormHelper()
    helper.form_tag = False
    helper.layout = layout.Layout(
        layout.Row(
            layout.Div('name', css_class='col-lg-4'),
            layout.Div(PickableDateField('start_date'), css_class='col-lg-2'),
            layout.Div('notes', css_class='col-lg-5'),
        ),
        layout.Row(
            layout.Div(layout.Field('articles', css_class='article-name'),
                       css_class='col-lg-11'),
        ),
    )


class CustomerGroupForm(forms.ModelForm):
    customers = ModelMultipleChoiceTextField(queryset=Customer.objects.all(), label=_("Customers"))


class BaseCustomerGroupFormset(forms.BaseInlineFormSet):
    helper = helper.FormHelper()
    helper.form_tag = False
    helper.disable_csrf = True
    helper.form_show_labels = False
    helper.layout = layout.Layout(
        layout.Row(
            # since a dynamic formset is used, there is no need to allow posting empty fields for
            # unused extra forms, so all fields can be explicitly required:
            layout.Div(layout.Field('name', required=''), css_class='col-lg-4'),
            layout.Div(layout.Field('customers', css_class='customer-name'), css_class='col-lg-7'),
            layout.Div(remove_form_button_factory(), css_class='col-lg-1 text-right'),
            layout.Field('DELETE', style='display:none;'),
            data_formset_form='',
        )
    )

    def clean(self):
        super().clean()
        names = set()
        for form in self.forms:
            if form not in self.deleted_forms:
                name = form.cleaned_data['name']
                if name in names:
                    raise forms.ValidationError(
                        _("Only one customer group may be called %(name)s."),
                        code='duplicate_group_name',
                        params={'name': name}
                    )
                names.add(name)


CustomerGroupFormset = forms.inlineformset_factory(
    Project,
    CustomerGroup,
    form=CustomerGroupForm,
    formset=BaseCustomerGroupFormset,
    can_delete=True,
    min_num=1,
    validate_min=True,
    extra=0,
    fields='__all__'
)
