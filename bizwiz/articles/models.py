from django.db import models
from django.utils.translation import ugettext_lazy as _


class ArticleBase(models.Model):
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

    def __str__(self):
        return self.name

    class Meta:
        abstract = True


class Article(ArticleBase):
    """An article to be sold to customers."""
    inactive = models.BooleanField(
        _("Inactive"),
        default=False,
        help_text=_("Inactive articles can no longer be used in projects and invoices.")
    )

    class Meta:
        verbose_name = _("Article")
        verbose_name_plural = _("Articles")
