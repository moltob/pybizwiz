from unittest import mock

import datetime

import decimal
import pytest

from bizwiz.articles.models import Article
from bizwiz.customers.models import Customer, Salutation
from bizwiz.invoices import services
from bizwiz.invoices.models import Invoice, InvoicedArticle
from bizwiz.invoices.services import get_next_invoice_number, create_invoice, refresh_rebates
from bizwiz.projects.models import Project
from bizwiz.rebates.models import Rebate, RebateKind


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
    assert get_next_invoice_number() == 1


@pytest.mark.django_db
def test__get_next_invoice_number__second():
    Invoice(number=12345).save()
    assert get_next_invoice_number() == 12346


@pytest.mark.django_db
def test__get_next_invoice_number__many():
    Invoice(number=12345).save()
    Invoice(number=789).save()
    Invoice(number=40000).save()
    Invoice(number=12346).save()
    Invoice(number=125).save()
    Invoice(number=12347).save()
    assert get_next_invoice_number() == 40001


@pytest.fixture
def posted_articles():
    a1 = InvoicedArticle(name='A1', price=decimal.Decimal.from_float(1.23), amount=2)
    a2 = InvoicedArticle(name='A2', price=decimal.Decimal.from_float(4), amount=3)
    return [a1, a2]


@pytest.fixture
def customer():
    c = Customer(first_name='FIRST', last_name='LAST', salutation=Salutation.MR)
    c.save()
    return c


@pytest.mark.django_db
def test__create_invoice__global(customer, posted_articles):
    invoice = create_invoice(customer=customer, invoiced_articles=posted_articles)

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
def test__create_invoice__project(customer, posted_articles):
    project = Project(name='PROJECT')
    project.save()

    invoice = create_invoice(project=project, customer=customer, invoiced_articles=posted_articles)

    assert invoice.project == project


@pytest.mark.django_db
def test__create_invoice__number_unique(customer, posted_articles):
    Invoice(number='123').save()
    Invoice(number='45').save()

    invoice = create_invoice(customer=customer, invoiced_articles=posted_articles)

    assert invoice.number not in {'123', '45'}


@pytest.mark.django_db
def test__create_invoice__original_article(customer, posted_articles):
    article = Article(name='A1', price=5)
    article.save()

    invoice = create_invoice(customer=customer, invoiced_articles=posted_articles)

    invoiced_articles = invoice.invoiced_articles.all()
    assert invoiced_articles[0].original_article == article
    assert invoiced_articles[1].original_article is None


@pytest.fixture
def invoice_with_rebates(customer, posted_articles):
    rebate1 = Rebate(name='NAME1', kind=RebateKind.PERCENTAGE, value=10, auto_apply=False)
    rebate2 = Rebate(name='NAME2', kind=RebateKind.ONE_FREE_PER, value=5, auto_apply=True)
    rebate1.save()
    rebate2.save()
    rebates = [rebate1, rebate2]

    invoice = create_invoice(customer=customer,
                             invoiced_articles=posted_articles,
                             rebates=rebates)
    return invoice


@pytest.mark.django_db
def test__create_invoice__rebates(invoice_with_rebates):
    # check if rebate list has been saved to DB by getting invoice freshly:
    saved_invoice = Invoice.objects.get(pk=invoice_with_rebates.pk)
    saved_rebates = list(saved_invoice.rebates.all())

    assert len(saved_rebates) == 2
    assert saved_rebates[0].name == 'NAME1'
    assert saved_rebates[1].name == 'NAME2'


def assert_rebate_reapplication_does_not_change_invoice(invoice):
    total = invoice.total
    num_items = invoice.invoiced_articles.count()

    services.refresh_rebates(invoice)

    assert invoice.total == total
    assert invoice.invoiced_articles.count() == num_items


@pytest.mark.django_db
@pytest.mark.parametrize(('amount', 'price'), [
    (20, decimal.Decimal('24.30')),  # rebate not applicable
    (11, decimal.Decimal('24.30')),  # still not applicable
    (10, decimal.Decimal('23.07')),  # one off
    (9, decimal.Decimal('23.07')),  # one off
    (6, decimal.Decimal('23.07')),  # one off
    (5, decimal.Decimal('21.84')),  # two off
    (4, decimal.Decimal('21.84')),  # two off
    (1, decimal.Decimal('24.30')),  # not useful, original price
    (0, decimal.Decimal('24.30')),  # not useful, original price
])
def test__create_invoice__rebate_one_free(customer, posted_articles, amount, price):
    rebate1 = Rebate(name='Rebate', kind=RebateKind.ONE_FREE_PER, value=amount, auto_apply=False)
    rebate1.save()
    rebates = [rebate1]

    posted_articles[0].amount = 10
    invoice = create_invoice(customer=customer,
                             invoiced_articles=posted_articles,
                             rebates=rebates)

    assert invoice.total == price
    assert_rebate_reapplication_does_not_change_invoice(invoice)


@pytest.mark.django_db
def test__create_invoice__rebate_percentage(customer, posted_articles):
    rebate1 = Rebate(name='Rebate', kind=RebateKind.PERCENTAGE, value=decimal.Decimal('20'),
                     auto_apply=False)
    rebate1.save()
    rebates = [rebate1]

    invoice = create_invoice(customer=customer,
                             invoiced_articles=posted_articles,
                             rebates=rebates)

    assert invoice.total == decimal.Decimal('11.57')
    assert_rebate_reapplication_does_not_change_invoice(invoice)


@pytest.mark.django_db
def test__create_invoice__rebate_absolute(customer, posted_articles):
    rebate1 = Rebate(name='Rebate', kind=RebateKind.ABSOLUTE, value=decimal.Decimal('5'),
                     auto_apply=False)
    rebate1.save()
    rebates = [rebate1]

    invoice = create_invoice(customer=customer,
                             invoiced_articles=posted_articles,
                             rebates=rebates)

    assert invoice.total == decimal.Decimal('9.46')
    assert_rebate_reapplication_does_not_change_invoice(invoice)


@pytest.mark.django_db
def test__create_invoice__rebate_absolute_greater_total(customer, posted_articles):
    rebate1 = Rebate(name='Rebate', kind=RebateKind.ABSOLUTE, value=decimal.Decimal('20'),
                     auto_apply=False)
    rebate1.save()
    rebates = [rebate1]

    invoice = create_invoice(customer=customer,
                             invoiced_articles=posted_articles,
                             rebates=rebates)

    # rebate is larger than total of invoice, prevent negative invoice:
    assert invoice.total == decimal.Decimal('0.00')
