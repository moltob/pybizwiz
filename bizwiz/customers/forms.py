import logging
from crispy_forms import helper, layout, bootstrap
from django import forms
from django.utils.translation import ugettext as _

from bizwiz.customers.models import Customer

_logger = logging.getLogger(__name__)


class UpdateForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'

    duplicate_accepted = forms.BooleanField(
        label=_("Name is correct"),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # layout is modified during form processing, so it must configured per instance:
        self.helper = helper.FormHelper()
        self.helper.layout = layout.Layout(
            layout.Row(
                layout.Div(
                    layout.Field('duplicate_accepted', type='hidden'),
                    css_class='col-lg-12'
                )
            ),
            layout.Row(
                layout.Div('salutation', css_class='col-lg-3'),
                layout.Div('title', css_class='col-lg-3'),
            ),
            layout.Row(
                layout.Div('first_name', css_class='col-lg-6'),
                layout.Div('last_name', css_class='col-lg-6'),
            ),
            layout.Row(
                layout.Div('company_name', css_class='col-lg-6'),
            ),
            layout.Row(
                layout.Div('street_address', css_class='col-lg-6'),
            ),
            layout.Row(
                layout.Div('zip_code', css_class='col-lg-2'),
                layout.Div('city', css_class='col-lg-4'),
            ),
            bootstrap.Accordion(
                bootstrap.AccordionGroup(
                    _("Additional"),
                    layout.Row(
                        layout.Div('phone_number', css_class='col-lg-4'),
                        layout.Div('mobile_number', css_class='col-lg-4'),
                        layout.Div('email', css_class='col-lg-4'),
                    ),
                    layout.Row(
                        layout.Div('notes', css_class='col-lg-12'),
                    ),
                    active=False
                ),
            ),
            layout.Row(
                layout.Div(layout.Submit('submit', _("Submit")), css_class='col-lg-1')
            ),
        )

        self.duplicates = None

    def clean(self):
        cleaned_data = super().clean()

        # if user changed the name, check whether a duplicate was created:
        if {'last_name', 'first_name'} & set(self.changed_data):
            last_name = cleaned_data['last_name']
            first_name = cleaned_data['first_name']

            # find other customers with this name, exclude current instance:
            duplicates = Customer.objects \
                .filter(last_name__iexact=last_name, first_name__iexact=first_name) \
                .exclude(pk__exact=self.instance.pk)

            if duplicates and not cleaned_data['duplicate_accepted']:
                _logger.debug('User tries to add duplicate customer {}, {}. Found {} duplicates.'
                              .format(last_name, first_name, len(duplicates)))

                # flag validation error and provide duplicates to rendered context:
                self.add_error('duplicate_accepted', forms.ValidationError('', code='duplicate'))
                self.duplicates = duplicates

                # make confirmation box visible:
                self.helper['duplicate_accepted'].update_attributes(type='')
