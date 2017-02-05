import datetime
import pytest

from bizwiz.invoices.forms import ListActionForm, InvoiceAction
from bizwiz.invoices.models import Invoice


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

    assert form.is_valid()


@pytest.mark.django_db
def test__list_action_form__tax_valid():
    invoice1 = Invoice(number='1', date_paid=datetime.datetime.now())
    invoice2 = Invoice(number='2', date_paid=datetime.datetime.now())
    invoice1.save()
    invoice2.save()

    form = ListActionForm({
        'action': InvoiceAction.TAX,
        'invoice_ids': '  {}  {}  '.format(invoice1.pk, invoice2.pk),
    })

    assert form.is_valid()


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

    assert form.is_valid()

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

    assert not form.is_valid()


@pytest.mark.django_db
def test__list_action_form__pay_invalid__already_paid():
    invoice1 = Invoice(number='1')
    invoice2 = Invoice(number='2', date_paid=datetime.datetime.now())
    invoice1.save()
    invoice2.save()

    form = ListActionForm({
        'action': InvoiceAction.PAY,
        'invoice_ids': '  {}  {}  '.format(invoice1.pk, invoice2.pk),
    })

    assert not form.is_valid()


@pytest.mark.django_db
def test__list_action_form__tax_invalid__not_paid():
    invoice1 = Invoice(number='1')
    invoice2 = Invoice(number='2', date_paid=datetime.datetime.now())
    invoice1.save()
    invoice2.save()

    form = ListActionForm({
        'action': InvoiceAction.TAX,
        'invoice_ids': '  {}  {}  '.format(invoice1.pk, invoice2.pk),
    })

    assert not form.is_valid()


@pytest.mark.django_db
def test__list_action_form__tax_invalid__already_taxed():
    invoice1 = Invoice(number='1',
                       date_paid=datetime.datetime.now(),
                       date_taxes_filed=datetime.datetime.now())
    invoice2 = Invoice(number='2',
                       date_paid=datetime.datetime.now())
    invoice1.save()
    invoice2.save()

    form = ListActionForm({
        'action': InvoiceAction.TAX,
        'invoice_ids': '  {}  {}  '.format(invoice1.pk, invoice2.pk),
    })

    assert not form.is_valid()
