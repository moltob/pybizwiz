import datetime
from django.db import models
from django.utils.translation import ugettext_lazy as _

from bizwiz.articles.models import Article
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
    articles = models.ManyToManyField(Article, verbose_name=_("Articles in project"))

    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")

    def __str__(self):
        return self.name


class CustomerGroup(models.Model):
    """Groups of customers within a project."""
    name = models.CharField(
        _("Name"),
        max_length=50,
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    customers = models.ManyToManyField(Customer, verbose_name=_("Customers in group"))

    class Meta:
        verbose_name = _("Customer group")
        verbose_name_plural = _("Customer groups")

    def __str__(self):
        return '{} ({})'.format(self.name, self.project.name)

