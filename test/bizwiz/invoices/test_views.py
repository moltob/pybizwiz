import datetime
import decimal
import itertools
from unittest import mock

import pytest
from djmoney import money

from bizwiz.invoices.forms import InvoiceAction
from bizwiz.invoices.models import Invoice, InvoicedArticle, ItemKind
from bizwiz.invoices.views import List, Update, Sales, ArticleSales


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


@pytest.mark.django_db
def test__sales__queryset__empty():
    qs = Sales().get_queryset()
    data = qs.all()
    assert not data


@pytest.fixture
def invoices_for_aggregation():
    invoices = [
        Invoice(number=1),
        Invoice(number=2, date_paid=datetime.date(2016, 1, 2)),
        Invoice(number=3, date_paid=datetime.date(2016, 3, 4)),
        Invoice(number=4, date_paid=datetime.date(2017, 5, 6)),
    ]
    for i in invoices:
        i.save()

    invoice_articles1 = [
        InvoicedArticle(
            invoice=invoices[0],
            name='A',
            price=money.Money(1, 'EUR'),
            amount=1,
            kind=ItemKind.ARTICLE,
        ),
    ]
    invoiced_articles2 = [
        InvoicedArticle(
            invoice=invoices[1],
            name='A',
            price=money.Money(10.03, 'EUR'),
            amount=5,
            kind=ItemKind.ARTICLE,
        ),
        InvoicedArticle(
            invoice=invoices[1],
            name='B',
            price=money.Money(11, 'EUR'),
            amount=6,
            kind=ItemKind.ARTICLE,
        ),
    ]
    invoiced_articles3 = [
        InvoicedArticle(
            invoice=invoices[2],
            name='A',
            price=money.Money(100, 'EUR'),
            amount=10,
            kind=ItemKind.ARTICLE,
        ),
        InvoicedArticle(
            invoice=invoices[2],
            name='B',
            price=money.Money(101, 'EUR'),
            amount=11,
            kind=ItemKind.ARTICLE,
        ),
        InvoicedArticle(
            invoice=invoices[2],
            name='C3 Rebate',
            price=money.Money(-10, 'EUR'),
            amount=1,
            kind=ItemKind.REBATE,
        ),
    ]
    invoiced_articles4 = [
        InvoicedArticle(
            invoice=invoices[3],
            name='A',
            price=money.Money(1000, 'EUR'),
            amount=20,
            kind=ItemKind.ARTICLE,
        ),
        InvoicedArticle(
            invoice=invoices[3],
            name='B',
            price=money.Money(1001, 'EUR'),
            amount=21,
            kind=ItemKind.ARTICLE,
        ),
    ]
    for a in itertools.chain(invoice_articles1, invoiced_articles2, invoiced_articles3,
                             invoiced_articles4):
        a.save()

    return invoices


@pytest.mark.django_db
def test__sales__queryset__computation(invoices_for_aggregation):
    qs = Sales().get_queryset()
    assert len(qs) == 2

    sales_by_year = {s['year_paid']: s for s in qs}

    sales_2017 = sales_by_year[2017]
    assert sales_2017['num_invoices'] == 1
    assert sales_2017['num_articles'] == 20 + 21
    assert sales_2017['total'] == decimal.Decimal(21 * 1001 + 20 * 1000)
    assert sales_2017['total_currency'] == 'EUR'

    sales_2016 = sales_by_year[2016]
    assert sales_2016['year_paid'] == 2016
    assert sales_2016['num_invoices'] == 2
    assert sales_2016['num_articles'] == 11 + 10 + 6 + 5
    assert sales_2016['total'] == decimal.Decimal('2217.15')
    assert sales_2016['total_currency'] == 'EUR'


@pytest.mark.django_db
def test__article_sales__queryset__computation(invoices_for_aggregation):
    sales = ArticleSales()
    sales.kwargs = dict(year=2016)
    qs = sales.get_queryset()

    sales_by_article_name = {s['name']: s for s in qs}

    assert len(sales_by_article_name) == 2

    sales_a = sales_by_article_name['A']
    assert sales_a['year_amount'] == 5 + 10
    assert sales_a['total'] == decimal.Decimal('1050.15')  # 5 * 10.03 + 10 * 100
    assert sales_a['total_currency'] == 'EUR'

    sales_b = sales_by_article_name['B']
    assert sales_b['year_amount'] == 6 + 11
    assert sales_b['total'] == decimal.Decimal(6 * 11 + 11 * 101)
    assert sales_b['total_currency'] == 'EUR'
