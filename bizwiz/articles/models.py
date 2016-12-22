from django.db import models
from django.utils.translation import ugettext_lazy as _


class Article(models.Model):
    """An article to be sold to customers."""
    name = models.CharField(
        _("Invoice text"),
        max_length=128,
        unique=True,
    )
    price = models.DecimalField(
        _("Unit price"),
        max_digits=6,
        decimal_places=2
    )
    inactive = models.BooleanField(
        _("No longer used."),
        default=False,
        help_text=_("Inactive articles can no longer be used in projects and invoices.")
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Article")
        verbose_name_plural = _("Articles")
