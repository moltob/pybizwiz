from django.db import models
from django.utils.translation import ugettext as _


class Article(models.Model):
    """An article to be sold to customers."""
    name = models.CharField(_("Invoice text"), max_length=128, unique=True)
    price = models.DecimalField(_("Unit price"), max_digits=6, decimal_places=2)
    inactive = models.BooleanField(_("Inactive, no longer in use"), default=False)

    def __str__(self):
        return self.name
