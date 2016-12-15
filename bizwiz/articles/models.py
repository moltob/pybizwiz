from django.db import models


class Article(models.Model):
    """An article to be sold to customers."""
    name = models.CharField(max_length=128)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    inactive = models.BooleanField(default=False)
