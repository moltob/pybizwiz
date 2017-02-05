from unittest import mock

import pytest

from bizwiz.invoices.forms import InvoiceAction
from bizwiz.invoices.views import List


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
