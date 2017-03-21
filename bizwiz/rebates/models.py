import locale

from django.db import models
from django.utils.translation import ugettext_lazy as _


class RebateKind:
    ABSOLUTE = 'ABS'
    PERCENTAGE = 'PERC'
    ONE_FREE_PER = 'ONEFREE'


class Rebate(models.Model):
    """Rebate rules applied to invoices."""

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

    def __str__(self):
        if self.kind == RebateKind.ABSOLUTE:
            value = locale.currency(self.value)
        elif self.kind == RebateKind.ONE_FREE_PER:
            amount = int(self.value)
            value = "{}/{}".format(amount - 1, amount)
        elif self.kind == RebateKind.PERCENTAGE:
            value = locale.format_string("%.2f %%", self.value)
        else:
            raise NotImplementedError('Unexpected rebate kind {!r}.'.format(self.kind))

        return "{} ({})".format(self.name, value)
