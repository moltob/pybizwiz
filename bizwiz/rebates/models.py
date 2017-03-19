from django.db import models
from django.utils.translation import ugettext_lazy as _

from bizwiz.common.models import copy_field_data
from bizwiz.invoices.models import Invoice


class RebateKind:
    ABSOLUTE = 'ABS'
    PERCENTAGE = 'PERC'
    ONE_FREE_PER = 'ONEFREE'


class Rebate(models.Model):
    """Rebate as configured in system."""

    class Meta:
        verbose_name = _("Rebate")
        verbose_name_plural = _("Rebates")

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
    auto_apply = models.BooleanField(
        _("Automatic"),
    )
