import decimal
import os

import pytest

from bizwiz.invoices.models import Invoice
from bizwiz.rebates.models import Rebate, RebateKind

VALUE = decimal.Decimal('8.00')


@pytest.mark.skipif(os.environ.get('TRAVIS') == 'true',
                    reason='Travis CI does not support locale installation.')
def test__rebate__str__percentage():
    r = Rebate(name='NAME', kind=RebateKind.PERCENTAGE, value=VALUE)
    assert str(r) == "NAME (8,00 %)"


@pytest.mark.skipif(os.environ.get('TRAVIS') == 'true',
                    reason='Travis CI does not support locale installation.')
def test__rebate__str__absolute():
    r = Rebate(name='NAME', kind=RebateKind.ABSOLUTE, value=VALUE)
    assert str(r) == "NAME (8,00 €)"


def test__rebate__str__amount():
    r = Rebate(name='NAME', kind=RebateKind.ONE_FREE_PER, value=VALUE)
    assert str(r) == "NAME (7/8)"


def test__evaluation_index():
    r1 = Rebate(name='NAME', kind=RebateKind.ONE_FREE_PER, value=VALUE)
    r2 = Rebate(name='NAME', kind=RebateKind.ABSOLUTE, value=VALUE)
    r3 = Rebate(name='NAME', kind=RebateKind.PERCENTAGE, value=VALUE)
    assert r1.evaluation_index < r2.evaluation_index
    assert r1.evaluation_index < r3.evaluation_index
    assert r2.evaluation_index < r3.evaluation_index
