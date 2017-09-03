from unittest import mock

import datetime

import itertools
import pytest
from django import http

from bizwiz.invoices.forms import InvoiceAction
from bizwiz.invoices.models import Invoice, InvoicedArticle
from bizwiz.invoices.views import List, Update, Sales


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


@pytest.mark.django_db
def test__sales__queryset__computation():
    invoices = [
        Invoice(number=1),
        Invoice(number=2, date_paid=datetime.date(2016, 1, 2)),
        Invoice(number=3, date_paid=datetime.date(2016, 3, 4)),
        Invoice(number=4, date_paid=datetime.date(2017, 5, 6)),
    ]
    for i in invoices:
        i.save()

    articles1 = [
        InvoicedArticle(invoice=invoices[0], name='A1', price=1, amount=1),
    ]
    articles2 = [
        InvoicedArticle(invoice=invoices[1], name='B1', price=10, amount=5),
        InvoicedArticle(invoice=invoices[1], name='B2', price=11, amount=6),
    ]
    articles3 = [
        InvoicedArticle(invoice=invoices[2], name='C1', price=100, amount=10),
        InvoicedArticle(invoice=invoices[2], name='C2', price=101, amount=11),
    ]
    articles4 = [
        InvoicedArticle(invoice=invoices[3], name='D1', price=1000, amount=20),
        InvoicedArticle(invoice=invoices[3], name='D2', price=1001, amount=21),
    ]
    for a in itertools.chain(articles1, articles2, articles3, articles4):
        a.save()

    qs = Sales.queryset
    data = qs.all()

    assert len(data) == 2

    sales_2017 = data[0]
    assert sales_2017['year_paid'] == 2017
    assert sales_2017['num_invoices'] == 1
    assert sales_2017['num_articles'] == 20 + 21
    assert sales_2017['total'] == 21 * 1001 + 20 * 1000

    sales_2016 = data[1]
    assert sales_2016['year_paid'] == 2016
    assert sales_2016['num_invoices'] == 2
    assert sales_2016['num_articles'] == 11 + 10 + 6 + 5
    assert sales_2016['total'] == 11 * 101 + 10 * 100 + 6 * 11 + 5 * 10
