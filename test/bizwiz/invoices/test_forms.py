import datetime

import pytest

from bizwiz.invoices.forms import ListActionForm, InvoiceAction
from bizwiz.invoices.models import Invoice


def assert_form_valid(form, invoice1, invoice2):
    assert form.is_valid()
    assert len(form.invoices) == 2
    assert invoice1 in form.invoices
    assert invoice2 in form.invoices


def assert_form_invalid(form):
    assert not form.is_valid()
    assert not form.invoices


@pytest.mark.django_db
def test__list_action_form__pay_valid():
    invoice1 = Invoice(number='1')
    invoice2 = Invoice(number='2')
    invoice1.save()
    invoice2.save()

    form = ListActionForm({
        'action': InvoiceAction.PAY,
        'invoice_ids': '  {}  {}  '.format(invoice1.pk, invoice2.pk),
    })

    assert_form_valid(form, invoice1, invoice2)


@pytest.mark.django_db
def test__list_action_form__tax_valid():
    invoice1 = Invoice(number='1', date_paid=datetime.date.today())
    invoice2 = Invoice(number='2', date_paid=datetime.date.today())
    invoice1.save()
    invoice2.save()

    form = ListActionForm({
        'action': InvoiceAction.TAX,
        'invoice_ids': '  {}  {}  '.format(invoice1.pk, invoice2.pk),
    })

    assert_form_valid(form, invoice1, invoice2)


@pytest.mark.django_db
def test__list_action_form__delete_valid():
    invoice1 = Invoice(number='1')
    invoice2 = Invoice(number='2')
    invoice1.save()
    invoice2.save()

    form = ListActionForm({
        'action': InvoiceAction.DELETE,
        'invoice_ids': '  {}  {}  '.format(invoice1.pk, invoice2.pk),
    })

    assert_form_valid(form, invoice1, invoice2)


@pytest.mark.django_db
def test__list_action_form__pay_invalid__unknown_id():
    invoice1 = Invoice(number='1')
    invoice2 = Invoice(number='2')
    invoice1.save()
    invoice2.save()

    form = ListActionForm({
        'action': InvoiceAction.PAY,
        'invoice_ids': '  {}  {}  '.format(invoice1.pk, invoice2.pk + 1),
    })

    assert_form_invalid(form)


@pytest.mark.django_db
def test__list_action_form__pay_invalid__already_paid():
    invoice1 = Invoice(number='1')
    invoice2 = Invoice(number='2', date_paid=datetime.date.today())
    invoice1.save()
    invoice2.save()

    form = ListActionForm({
        'action': InvoiceAction.PAY,
        'invoice_ids': '  {}  {}  '.format(invoice1.pk, invoice2.pk),
    })

    assert_form_invalid(form)


@pytest.mark.django_db
def test__list_action_form__tax_invalid__not_paid():
    invoice1 = Invoice(number='1')
    invoice2 = Invoice(number='2', date_paid=datetime.date.today())
    invoice1.save()
    invoice2.save()

    form = ListActionForm({
        'action': InvoiceAction.TAX,
        'invoice_ids': '  {}  {}  '.format(invoice1.pk, invoice2.pk),
    })

    assert_form_invalid(form)


@pytest.mark.django_db
def test__list_action_form__tax_invalid__already_taxed():
    invoice1 = Invoice(number='1',
                       date_paid=datetime.date.today(),
                       date_taxes_filed=datetime.date.today())
    invoice2 = Invoice(number='2',
                       date_paid=datetime.date.today())
    invoice1.save()
    invoice2.save()

    form = ListActionForm({
        'action': InvoiceAction.TAX,
        'invoice_ids': '  {}  {}  '.format(invoice1.pk, invoice2.pk),
    })

    assert_form_invalid(form)
