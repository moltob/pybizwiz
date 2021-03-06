import decimal

import pytest
from djmoney import money

from bizwiz.articles.models import ArticleBase, Article
from bizwiz.customers.models import Customer, Salutation, CustomerBase
from bizwiz.invoices.models import InvoicedCustomer, Invoice, InvoicedArticle, ItemKind


def test__invoiced_customer__create():
    assert len(CustomerBase._meta.get_fields()) == 9, 'CustomerBase changed, adapt test case.'
    c1 = Customer(
        first_name='FIRST',
        last_name='LAST',
        salutation=Salutation.MR,
        title='TITLE',
        company_name='COMPANY_NAME',
        street_address='STREET',
        zip_code='ZIP',
        city='CITY',
        notes='Some notes about this guy.',
    )
    invoice = Invoice()

    c2 = InvoicedCustomer.create(invoice, c1)

    assert c2.invoice == invoice
    assert c2.first_name == 'FIRST'
    assert c2.last_name == 'LAST'
    assert c2.salutation == Salutation.MR
    assert c2.title == 'TITLE'
    assert c2.company_name == 'COMPANY_NAME'
    assert c2.zip_code == 'ZIP'
    assert c2.city == 'CITY'
    assert c2.notes == 'Some notes about this guy.'


def test__invoiced_article__create():
    assert len(ArticleBase._meta.get_fields()) == 3, 'ArticleBase changed, adapt test case.'
    a1 = Article(
        name='NAME',
        price=money.Money(1.2, 'USD'),  # stored as one field per amount, currency
    )
    invoice = Invoice()

    a2 = InvoicedArticle.create(invoice, a1, 1)

    assert a2.invoice == invoice
    assert a2.name == 'NAME'
    assert a2.price == money.Money(1.2, 'USD')
    assert a2.amount == 1
    assert a2.kind == ItemKind.ARTICLE


@pytest.mark.django_db
def test__invoice__total():
    invoice = Invoice(number=1)
    invoice.save()

    a = InvoicedArticle(invoice=invoice, price=1.2, amount=1)
    a.save()
    a = InvoicedArticle(invoice=invoice, price=3.4, amount=0)
    a.save()
    a = InvoicedArticle(invoice=invoice, price=-0.5, amount=2)
    a.save()

    assert invoice.total == money.Money(0.2, 'EUR')
    assert str(invoice.total) == '0,20 €'
