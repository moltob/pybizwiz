from unittest import mock

import pytest
from django import http

from bizwiz.invoices.forms import InvoiceAction
from bizwiz.invoices.views import List, Update


@pytest.mark.parametrize('action,called_function_name', [
    (InvoiceAction.PAY, 'pay_invoices'),
    (InvoiceAction.TAX, 'taxfile_invoices'),
    (InvoiceAction.DELETE, 'delete_invoices'),
])
def test__list__form_valid(action, called_function_name):
    mock_form = mock.MagicMock()
    mock_form.cleaned_data = {
        'action': action,
    }
    mock_form.invoices = [mock.sentinel.INVOICE1, mock.sentinel.INVOICE2]

    with mock.patch('bizwiz.invoices.views.services') as mock_services:
        mock_services.pay_invoices = mock.MagicMock(f='pay_invoices')
        mock_services.taxfile_invoices = mock.MagicMock(f='taxfile_invoices')
        mock_services.delete_invoices = mock.MagicMock(f='delete_invoices')
        service_mocks = [
            mock_services.pay_invoices,
            mock_services.taxfile_invoices,
            mock_services.delete_invoices
        ]

        view = List()
        view.form_valid(mock_form)

        for service_mock in service_mocks:
            if service_mock.f == called_function_name:
                service_mock.assert_called_once_with([mock.sentinel.INVOICE1,
                                                      mock.sentinel.INVOICE2])
            else:
                assert not service_mock.called
            service_mock.reset_mock()


@pytest.mark.django_db
@mock.patch('bizwiz.invoices.views.services')
def test__update_view__forms_valid__refreshes_rebates(mock_invoice_services):
    mock_invoice_form = mock.MagicMock()
    mock_invoice_form.save = mock.MagicMock(return_value=mock.sentinel.INVOICE)
    mock_customer_form = mock.MagicMock()
    mock_invoiced_article_formset = mock.MagicMock()

    view = Update()
    view.form_valid = mock.MagicMock()
    view.forms_valid(mock_invoice_form, mock_customer_form, mock_invoiced_article_formset)

    mock_invoice_services.refresh_rebates.assert_called_once_with(mock.sentinel.INVOICE)
