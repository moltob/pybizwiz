from bizwiz.invoices.models import Invoice
from bizwiz.rebates.models import Rebate, RebateKind


# def test__applied_rebate__create():
#     assert len(RebateBase._meta.get_fields()) == 3, 'RebateBase changed, adapt test case.'
#     r1 = Rebate(
#         name='NAME',
#         kind=RebateKind.ABSOLUTE,
#         value=2.05,
#         auto_apply=True,
#     )
#     invoice = Invoice()
#
#     r2 = AppliedRebate.create(invoice, r1)
#
#     assert r2.name == 'NAME'
#     assert r2.kind == RebateKind.ABSOLUTE
#     assert r2.value == 2.05
#     assert r2.invoice == invoice
