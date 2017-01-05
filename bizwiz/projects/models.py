import datetime
from django.db import models
from django.utils.translation import ugettext_lazy as _

from bizwiz.customers.models import Customer


class Project(models.Model):
    """Photography project."""
    name = models.CharField(
        _("Name"),
        max_length=50,
        unique=True,
    )
    start_date = models.DateField(
        _("Start date"),
        default=datetime.date.today,
    )
    notes = models.TextField(
        _("Notes"),
        blank=True
    )


class CustomerGroup(models.Model):
    """Groups of customers within a project."""
    name = models.CharField(
        _("Name"),
        max_length=50,
        unique=True,
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    customers = models.ManyToManyField(Customer)
