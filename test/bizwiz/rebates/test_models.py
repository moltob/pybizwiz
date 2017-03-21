import decimal

from bizwiz.invoices.models import Invoice
from bizwiz.rebates.models import Rebate, RebateKind

VALUE = decimal.Decimal('8.00')

def test__rebate__str__percentage():
    r = Rebate(name='NAME', kind=RebateKind.PERCENTAGE, value=VALUE)
    assert str(r) == "NAME (8,00 %)"


def test__rebate__str__absolute():
    r = Rebate(name='NAME', kind=RebateKind.ABSOLUTE, value=VALUE)
    assert str(r) == "NAME (8,00 €)"


def test__rebate__str__amount():
    r = Rebate(name='NAME', kind=RebateKind.ONE_FREE_PER, value=VALUE)
    assert str(r) == "NAME (7/8)"
