from unittest import mock

import datetime
import pytest

from bizwiz.invoices import services


@pytest.fixture
def invoices():
    return [
        mock.MagicMock(),
        mock.MagicMock()
    ]


@mock.patch('bizwiz.invoices.services.transaction')
def test__pay_invoices(mock_transaction, invoices):
    services.pay_invoices(invoices)

    # make sure tests are set up correctly and list is not empty:
    assert invoices

    for invoice in invoices:
        assert isinstance(invoice.date_paid, datetime.date)
        invoice.save.assert_called_once_with()


@mock.patch('bizwiz.invoices.services.transaction')
def test__taxfile_invoices(mock_transaction, invoices):
    services.taxfile_invoices(invoices)

    for invoice in invoices:
        assert isinstance(invoice.date_taxes_filed, datetime.date)
        invoice.save.assert_called_once_with()


@mock.patch('bizwiz.invoices.services.transaction')
def test__delete_invoices(mock_transaction, invoices):
    services.delete_invoices(invoices)

    for invoice in invoices:
        invoice.delete.assert_called_once_with()
