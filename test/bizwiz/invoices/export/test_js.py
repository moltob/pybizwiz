import datetime
import json
import os
import shutil

import io
import pytest

from bizwiz.customers.models import Salutation
from bizwiz.invoices.export.js import InvoiceJsonExporter
from bizwiz.invoices.models import Invoice, InvoicedCustomer, InvoicedArticle


@pytest.fixture
def invoice():
    i = Invoice(
        number=1234,
        date_created=datetime.date(2017, 3, 1),
    )
    i.save()

    InvoicedCustomer(
        invoice=i,
        last_name='LAST_NAME-Müller',
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
def test__invoice_js_exporter__export(invoice):
    with io.StringIO() as data:
        InvoiceJsonExporter().export([invoice], data)
        value = data.getvalue()

    assert '"last_name": "LAST_NAME-M' in value
    assert '"total": "2000.60"' in value

    # verify JSON string translation works both ways:
    obj = json.loads(value)
    assert obj['invoices'][0]['last_name'] == 'LAST_NAME-Müller'
