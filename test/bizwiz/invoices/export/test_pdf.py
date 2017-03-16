import datetime
import os
import shutil

import pytest

from bizwiz.customers.models import Salutation
from bizwiz.invoices.export.pdf import TextBlocks, InvoicePdfExporter
from bizwiz.invoices.models import Invoice, InvoicedCustomer, InvoicedArticle


@pytest.fixture(scope='module')
def output_folder():
    curdir = os.path.dirname(__file__)
    return os.path.join(curdir, 'output')


@pytest.fixture(scope='module', autouse=True)
def clean_output_folder(output_folder):
    if os.path.exists(output_folder):
        shutil.rmtree(output_folder)
    os.mkdir(output_folder)


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
@pytest.mark.skipif(os.environ.get('TRAVIS'),
                    reason='Travis CI does not support locale installation.')
def test__text_blocks__article_table(invoice):
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


@pytest.mark.django_db
def test__invoice_pdf_exporter__export(invoice, output_folder):
    with open(os.path.join(output_folder, 'test_invoice.pdf'), 'wb') as file:
        InvoicePdfExporter().export([invoice], file)
