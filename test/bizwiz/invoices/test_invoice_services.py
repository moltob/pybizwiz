from unittest import mock

import datetime

import decimal
import pytest

from bizwiz.customers.models import Customer, Salutation
from bizwiz.invoices import services
from bizwiz.invoices.models import Invoice
from bizwiz.invoices.services import get_next_invoice_number, create_invoice
from bizwiz.projects.models import Project


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


@pytest.fixture
def article_dicts():
    return [
        {
            'name': 'A1',
            'price': decimal.Decimal.from_float(1.23),
            'amount': 2
        },
        {
            'name': 'A2',
            'price': decimal.Decimal.from_float(4),
            'amount': 3
        },
    ]


@pytest.fixture
def customer():
    c = Customer(first_name='FIRST', last_name='LAST', salutation=Salutation.MR)
    c.save()
    return c


@pytest.mark.django_db
def test__create_invoice__global(customer, article_dicts):
    invoice = create_invoice(customer=customer, article_dicts=article_dicts)

    assert not invoice.project
    assert invoice.invoiced_customer.original_customer == customer
    invoiced_articles = list(invoice.invoiced_articles.all())
    assert len(invoiced_articles) == 2
    assert invoiced_articles[0].name == 'A1'
    assert 1.229 < invoiced_articles[0].price < 1.231
    assert invoiced_articles[0].amount == 2
    assert invoiced_articles[1].name == 'A2'
    assert 3.999 < invoiced_articles[1].price < 4.001
    assert invoiced_articles[1].amount == 3


@pytest.mark.django_db
def test__create_invoice__project(customer, article_dicts):
    project = Project(name='PROJECT')
    project.save()

    invoice = create_invoice(project=project, customer=customer, article_dicts=article_dicts)

    assert invoice.project == project


@pytest.mark.django_db
def test__create_invoice__number_unique(customer, article_dicts):
    Invoice(number='123').save()
    Invoice(number='45').save()

    invoice = create_invoice(customer=customer, article_dicts=article_dicts)

    assert invoice.number not in {'123', '45'}
