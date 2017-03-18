from django.db import models
from django.utils.translation import ugettext_lazy as _

from bizwiz.common.models import copy_field_data
from bizwiz.invoices.models import Invoice


class RebateKind:
    ABSOLUTE = 'ABS'
    PERCENTAGE = 'PERC'
    ONE_FREE_PER = 'ONEFREE'


class RebateBase(models.Model):
    kind = models.CharField(
        _("Kind"),
        max_length=10,
        choices=(
            (RebateKind.ABSOLUTE, _("Absolute")),
            (RebateKind.PERCENTAGE, _("Percentage")),
            (RebateKind.ONE_FREE_PER, _("One free per")),
        )
    )
    name = models.CharField(
        _("Invoice text"),
        max_length=128,
        unique=True,
    )
    value = models.DecimalField(
        _("Value"),
        max_digits=6,
        decimal_places=2,
    )

    class Meta:
        abstract = True
        verbose_name = _("Rebate")
        verbose_name_plural = _("Rebates")


class Rebate(RebateBase):
    """Rebate as configured in system"""
    auto_apply = models.BooleanField(
        _("Apply automatically"),
    )


class AppliedRebate(RebateBase):
    """Rebate as it was applied to existing invoice, as a stable copy."""
    invoice = models.OneToOneField(
        Invoice,
        verbose_name=_("Invoice"),
        on_delete=models.CASCADE,
        related_name='applied_rebate',
    )

    @classmethod
    def create(cls, invoice, rebate):
        applied_rebate = AppliedRebate(invoice=invoice)
        copy_field_data(RebateBase, rebate, applied_rebate)
        return applied_rebate
