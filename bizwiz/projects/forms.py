from crispy_forms import layout, helper
from django import forms
from django.utils.translation import ugettext as _

from bizwiz.articles.models import Article
from bizwiz.common.crispy_forms import PickableDateField, ChosenMultiSelectField
from bizwiz.common.dynamic_formset import remove_form_button_factory
from bizwiz.customers.models import Customer
from bizwiz.projects.models import Project, CustomerGroup


class UpdateForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = '__all__'

    articles = forms.ModelMultipleChoiceField(queryset=Article.objects.all().order_by('name'))

    # form requires assets from custom date picker field:
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
            layout.Div(ChosenMultiSelectField('articles'), css_class='col-lg-11'),
        ),
    )


class CustomerGroupForm(forms.ModelForm):
    customers = forms.ModelMultipleChoiceField(queryset=Customer.objects.all()
                                               .order_by('last_name', 'first_name', 'company_name'))

    Media = ChosenMultiSelectField.Media


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
            layout.Div(ChosenMultiSelectField('customers'), css_class='col-lg-7'),
            layout.Div(remove_form_button_factory(), css_class='col-lg-1 text-right'),
            layout.Field('DELETE', style='display:none;'),
            data_formset_form='',
        )
    )

    def clean(self):
        super().clean()
        names = set()
        for form in self.forms:
            name = form.cleaned_data['name']
            if name in names:
                raise forms.ValidationError(_("Only one customer group may be called %(name)s."),
                                            code='duplicate_group_name',
                                            params={'name': name})
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


# TODO: add validation to check customer group names within project and at least one customer group
# TODO: exists

# TODO: single customer list possible in HTML?
