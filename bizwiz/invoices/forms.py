import logging
from crispy_forms import layout, helper, bootstrap
from django import forms
from django.db.models import BLANK_CHOICE_DASH
from django.utils.translation import ugettext as _

from bizwiz.common.dynamic_formset import remove_form_button_factory
from bizwiz.invoices.models import Invoice, InvoicedCustomer, InvoicedArticle

_logger = logging.getLogger(__name__)


class InvoiceAction:
    PAY = 'PAY'
    TAX = 'TAX'
    DELETE = 'DELETE'


class ListActionForm(forms.Form):
    action = forms.ChoiceField(choices=BLANK_CHOICE_DASH + [
        (InvoiceAction.PAY, _("Mark as paid")),
        (InvoiceAction.TAX, _("File taxes")),
        (InvoiceAction.DELETE, _("Delete")),
    ])
    # whitespace separated list of invoice IDs to be modified, filled by JS before form submission:
    invoice_ids = forms.CharField(strip=True)

    helper = helper.FormHelper()
    helper.layout = layout.Layout(
        layout.Row(
            layout.Div(
                bootstrap.FieldWithButtons(
                    layout.Field('action'),
                    bootstrap.StrictButton(_("Go!"), name='preview', css_class='btn-default',
                                           data_toggle='modal', data_target='#previewModal',
                                           css_id='preview', disabled=True),
                    css_class='moveUpToSearch',
                ),
                layout.Field('invoice_ids', type='hidden'),
                css_class='col-lg-offset-9 col-lg-3'
            ),
        ),
    )
    helper.form_tag = False
    helper.form_show_labels = False

    # List of invoices being modified after form POST.
    invoices = None

    def clean(self):
        self.invoices = None

        cleaned_data = super().clean()
        action = cleaned_data['action']
        invoice_id_strs = set(cleaned_data['invoice_ids'].split())
        invoice_ids = {int(id_) for id_ in invoice_id_strs}

        _logger.info('Action {!r} requested for {} invoices.'.format(action, len(invoice_id_strs)))
        _logger.debug('Affected invoice IDs: ' + ', '.join(invoice_id_strs))

        # verify invoice references:
        invoices = Invoice.objects.filter(pk__in=invoice_ids)
        if not len(invoices) == len(invoice_ids):
            found_ids = {invoice.pk for invoice in invoices}
            missing_ids = invoice_ids - found_ids
            _logger.warning('Invoice with the following IDs not found in database: {}'
                            .format(','.join(str(id_) for id_ in missing_ids)))
            raise forms.ValidationError(
                _("%(num)d invoices have not been found in the database, please refresh browser and"
                  " reselect."),
                code='invoice not found',
                params={'num': len(missing_ids)}
            )

        # verify action against current state of invoices:
        errors_found = False
        if action == InvoiceAction.PAY:
            paid_invoices = {invoice for invoice in invoices if invoice.date_paid}
            if paid_invoices:
                errors_found = True
                _logger.warning('Some invoices are already in status paid: {}'
                                .format(', '.join(str(invoice.pk) for invoice in paid_invoices)))
                self.add_error('action', forms.ValidationError(
                    _("Some of the selected invoices have been paid before, please unselect or "
                      "choose another action."),
                    'paying paid'
                ))
        elif action == InvoiceAction.TAX:
            unpaid_invoices = {invoice for invoice in invoices if not invoice.date_paid}
            taxed_invoices = {invoice for invoice in invoices if invoice.date_taxes_filed}
            if unpaid_invoices:
                errors_found = True
                _logger.warning('Some invoices have not yet been paid: {}'
                                .format(', '.join(str(invoice.pk) for invoice in unpaid_invoices)))
                self.add_error('action', forms.ValidationError(
                    _("Some of the selected invoices have not yet been paid before, please unselect"
                      " or choose another action."),
                    'taxing taxed'
                ))
            if taxed_invoices:
                errors_found = True
                _logger.warning('Some invoices are already in status taxed: {}'
                                .format(', '.join(str(invoice.pk) for invoice in taxed_invoices)))
                self.add_error('action', forms.ValidationError(
                    _("Some of the selected invoices have filed before, please unselect or "
                      "choose another action."),
                    'taxing taxed'
                ))

        if not errors_found:
            self.invoices = invoices


class UpdateForm(forms.ModelForm):
    class Meta:
        model = Invoice
        fields = '__all__'

    helper = helper.FormHelper()
    helper.layout = layout.Layout(
        layout.Row(
            layout.Div(
                layout.Field('project'),
                css_class='col-lg-4'
            ),
            layout.Div(
                layout.Field('date_created'),
                css_class='col-lg-2'
            ),
            layout.Div(
                layout.Field('date_paid'),
                css_class='col-lg-2'
            ),
            layout.Div(
                layout.Field('date_taxes_filed'),
                css_class='col-lg-2'
            ),
            layout.Div(
                layout.Field('number', readonly=True),
                css_class='col-lg-2'
            ),
        )
    )


class InvoicedCustomerForm(forms.ModelForm):
    class Meta:
        model = InvoicedCustomer
        fields = '__all__'

    helper = helper.FormHelper()
    helper.layout = layout.Layout(
        layout.Row(
            layout.Div('salutation', css_class='col-lg-3'),
            layout.Div('title', css_class='col-lg-3'),
        ),
        layout.Row(
            layout.Div('first_name', css_class='col-lg-3'),
            layout.Div('last_name', css_class='col-lg-3'),
            layout.Div('company_name', css_class='col-lg-6'),
        ),
        layout.Row(
            layout.Div('street_address', css_class='col-lg-6'),
            layout.Div('zip_code', css_class='col-lg-2'),
            layout.Div('city', css_class='col-lg-4'),
        ),
    )


class BaseInvoicedArticleFormset(forms.BaseInlineFormSet):
    helper = helper.FormHelper()
    helper.form_show_labels = False
    helper.layout = layout.Layout(
        layout.Row(
            # since a dynamic formset is used, there is no need to allow posting empty fields for
            # unused extra forms, so all fields can be explicitly required:
            layout.Div(layout.Field('name', required=''), css_class='col-lg-6'),
            layout.Div(layout.Field('price', required=''), css_class='col-lg-2', required=''),
            layout.Div(layout.Field('amount', required=''), css_class='col-lg-1', required=''),
            layout.Div(remove_form_button_factory(), css_class='col-lg-1'),
            layout.Div(
                layout.HTML('<p class="form-control-static item-total">0,00</p>'),
                css_class='col-lg-2 text-right'
            ),
            layout.Field('DELETE', style='display:none;'),
            data_formset_form='',
        )
    )


InvoicedArticleFormset = forms.inlineformset_factory(
    Invoice,
    InvoicedArticle,
    #form=InvoicedArticleForm,
    formset=BaseInvoicedArticleFormset,
    can_delete=True,
    min_num=1,
    validate_min=True,
    extra=0,
    fields='__all__'
)
