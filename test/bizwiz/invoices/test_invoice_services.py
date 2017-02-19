from unittest import mock

import datetime
import pytest

from bizwiz.invoices import services
from bizwiz.invoices.models import Invoice
from bizwiz.invoices.services import get_next_invoice_number


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


@pytest.mark.django_db
def test__get_next_invoice_number__first():
    assert get_next_invoice_number() == '1'


@pytest.mark.django_db
def test__get_next_invoice_number__second():
    Invoice(number='12345').save()
    assert get_next_invoice_number() == '12346'

@pytest.mark.django_db
def test__get_next_invoice_number__many():
    Invoice(number='12345').save()
    Invoice(number='789').save()
    Invoice(number='40000').save()
    Invoice(number='12346').save()
    Invoice(number='125').save()
    Invoice(number='12347').save()
    assert get_next_invoice_number() == '40001'
