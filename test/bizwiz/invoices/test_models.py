from unittest import mock

from bizwiz.articles.models import ArticleBase, Article
from bizwiz.customers.models import Customer, Salutation, CustomerBase
from bizwiz.invoices.models import InvoicedCustomer, Invoice, InvoicedArticle


def test__invoiced_customer__create():
    assert len(CustomerBase._meta.get_fields()) == 8, 'CustomerBase changed, adapt test case.'
    c1 = Customer(
        first_name='FIRST',
        last_name='LAST',
        salutation=Salutation.MR,
        title='TITLE',
        company_name='COMPANY_NAME',
        street_address='STREET',
        zip_code='ZIP',
        city='CITY',
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


def test__invoiced_article__create():
    assert len(ArticleBase._meta.get_fields()) == 2, 'ArticleBase changed, adapt test case.'
    a1 = Article(
        name='NAME',
        price=1.2,
    )
    invoice = Invoice()

    a2 = InvoicedArticle.create(invoice, a1, 1)

    assert a2.invoice == invoice
    assert a2.name == 'NAME'
    assert a2.price == 1.2
    assert a2.amount == 1
