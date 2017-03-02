import locale
from unittest import mock

import datetime
import pytest

from bizwiz.customers.models import Salutation
from bizwiz.invoices.export.pdf import TextBlocks
from bizwiz.invoices.models import Invoice, InvoicedCustomer, InvoicedArticle
from bwsite import settings


@pytest.fixture
def invoice():
    i = Invoice(
        number=1234,
        date_created=datetime.date(2017, 3, 1),
    )
    i.save()

    InvoicedCustomer(
        invoice=i,
        last_name='LAST_NAME',
        first_name='FIRST_NAME',
        salutation=Salutation.MR,
        title='Dr.',
        company_name='COMPANY',
        street_address='STREETADDRESS 7A',
        zip_code='12345',
        city='CITY',
    ).save()

    InvoicedArticle(
        invoice=i,
        name='NAME 1',
        price=0.20,
        amount=3,
    ).save()

    InvoicedArticle(
        invoice=i,
        name='NAME 2',
        price=1000,
        amount=2,
    ).save()

    return i


@pytest.mark.django_db
def test__text_blocks__clauses_formatting(invoice):
    blocks = TextBlocks(invoice)

    assert '01.03.2017' in blocks.clause_date
    assert 'R001234' in blocks.clause_subject
    assert 'Sehr geehrter Herr LAST_NAME' in blocks.clause_salutation


@pytest.mark.django_db
def test__text_blocks__article_table(invoice):
    locale.setlocale(locale.LC_ALL, settings.LANGUAGE_CODE)
    data = list(TextBlocks(invoice).iter_article_rows())
    assert len(data) == 4
    assert data[1] == ['NAME 1', '0,20 €', 3, '0,60 €']
    assert data[2] == ['NAME 2', '1.000,00 €', 2, '2.000,00 €']
    assert data[3][3] == '2.000,60 €'


@pytest.mark.django_db
def test__text_blocks__address_lines(invoice):
    lines = list(TextBlocks(invoice).iter_address_field_lines())
    assert lines == [
        "COMPANY",
        "Herrn",
        "Dr. FIRST_NAME LAST_NAME",
        "STREETADDRESS 7A",
        "12345 CITY"
    ]
