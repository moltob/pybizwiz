import datetime
import os
import shutil

import pytest

from bizwiz.customers.models import Salutation
from bizwiz.invoices.export.xlsx import InvoiceXlsxExporter
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
        number=100234,
        date_created=datetime.date(2017, 3, 1),
        date_paid=datetime.date(2017, 5, 23),
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
def test__invoice_xlsx_exporter__export(invoice, output_folder):
    with open(os.path.join(output_folder, 'test_invoice.xlsx'), 'wb') as file:
        InvoiceXlsxExporter().export([invoice], file)
