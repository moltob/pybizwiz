from unittest import mock

import datetime

import itertools

import decimal
import pytest
from django import http

from bizwiz.articles.models import Article
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
    qs = Sales.queryset
    data = qs.all()
    assert not data


@pytest.fixture
def invoices_for_aggregation():
    articles = [
        Article(name='A', price=1),
        Article(name='B', price=2),
    ]
    for a in articles:
        a.save()

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
            name='A1',
            price=1,
            amount=1,
            original_article=articles[0],
            kind=ItemKind.ARTICLE,
        ),
    ]
    invoiced_articles2 = [
        InvoicedArticle(
            invoice=invoices[1],
            name='B1',
            price=10.03,
            amount=5,
            original_article=articles[0],
            kind=ItemKind.ARTICLE,
        ),
        InvoicedArticle(
            invoice=invoices[1],
            name='B2',
            price=11,
            amount=6,
            original_article=articles[1],
            kind=ItemKind.ARTICLE,
        ),
    ]
    invoiced_articles3 = [
        InvoicedArticle(
            invoice=invoices[2],
            name='C1',
            price=100,
            amount=10,
            original_article=articles[0],
            kind=ItemKind.ARTICLE,
        ),
        InvoicedArticle(
            invoice=invoices[2],
            name='C2',
            price=101,
            amount=11,
            original_article=articles[1],
            kind=ItemKind.ARTICLE,
        ),
        InvoicedArticle(
            invoice=invoices[2],
            name='C3 Rebate',
            price=-10,
            amount=1,
            kind=ItemKind.REBATE,
        ),
    ]
    invoiced_articles4 = [
        InvoicedArticle(
            invoice=invoices[3],
            name='D1',
            price=1000,
            amount=20,
            original_article=articles[0],
            kind=ItemKind.ARTICLE,
        ),
        InvoicedArticle(
            invoice=invoices[3],
            name='D2',
            price=1001,
            amount=21,
            original_article=articles[1],
            kind=ItemKind.ARTICLE,
        ),
    ]
    for a in itertools.chain(invoice_articles1, invoiced_articles2, invoiced_articles3,
                             invoiced_articles4):
        a.save()

    return invoices


@pytest.mark.django_db
def test__sales__queryset__computation(invoices_for_aggregation):
    qs = Sales.queryset
    assert len(qs) == 2

    sales_by_year = {s['year_paid']: s for s in qs}

    sales_2017 = sales_by_year[2017]
    assert sales_2017['num_invoices'] == 1
    assert sales_2017['num_articles'] == 20 + 21
    assert sales_2017['total'] == 21 * 1001 + 20 * 1000

    sales_2016 = sales_by_year[2016]
    assert sales_2016['year_paid'] == 2016
    assert sales_2016['num_invoices'] == 2
    assert sales_2016['num_articles'] == 11 + 10 + 6 + 5
    assert sales_2016['total'] == decimal.Decimal('2227.15')


@pytest.mark.django_db
def test__article_sales__queryset__computation(invoices_for_aggregation):
    sales = ArticleSales()
    sales.kwargs = dict(year=2016)
    qs = sales.get_queryset()

    sales_by_article_name = {s['original_article__name']: s for s in qs}

    assert len(sales_by_article_name) == 2

    sales_a = sales_by_article_name['A']
    assert sales_a['year_amount'] == 5 + 10
    assert sales_a['total'] == decimal.Decimal('1050.15')  # 5 * 10.03 + 10 * 100

    sales_b = sales_by_article_name['B']
    assert sales_b['year_amount'] == 6 + 11
    assert sales_b['total'] == 6 * 11 + 11 * 101
