"""Invoice data model.

In order to make existing invoices independent of later changes/deletions of article and customer
data, each invoice copies the required fields, as part of the derived "Invoiced*" classes. The user
will still have the feeling of selecting customers and articles from the existing lists, but
internally the incoice is decoupled from the entities after copying.
"""
import datetime
from django.db import models
from django.utils.translation import ugettext_lazy as _
from bizwiz.articles.models import ArticleBase, Article
from bizwiz.customers.models import CustomerBase, Customer
from bizwiz.projects.models import Project


class InvoicedArticle(ArticleBase):
    original_article = models.ForeignKey(
        Article,
        on_delete=models.SET_NULL,
        verbose_name=_("Original article"),
        blank=True,
        null=True,
        related_name='invoiced_article',
    )
    amount = models.PositiveSmallIntegerField(_("Amount"))
    invoice = models.ForeignKey(
        Invoice,
        _("Invoice"),
        on_delete=models.CASCADE,
        related_name='invoiced_articles',
    )

    class Meta:
        verbose_name = _("Invoiced article")
        verbose_name_plural = _("Invoiced articles")


class InvoicedCustomer(CustomerBase):
    original_customer = models.ForeignKey(
        Customer,
        on_delete=models.SET_NULL,
        verbose_name=_("Original customer"),
        blank=True,
        null=True,
        related_name='invoiced_customer',
    )
    invoice = models.OneToOneField(
        Invoice,
        _("Invoice"),
        on_delete=models.CASCADE,
        related_name='invoiced_customer',
    )

    class Meta:
        verbose_name = _("Invoiced customer")
        verbose_name_plural = _("Invoiced customers")


class Invoice(models.Model):
    number = models.CharField(
        _("Invoice number"),
        max_length=7,
        unique=True,
    )
    date = models.DateField(
        _("Date"),
        default=datetime.date.today,
    )
    project = models.ForeignKey(
        Project,
        verbose_name=_("Project"),
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    current_state = models.OneToOneField(
        State,
        verbose_name=_("Current state"),
        on_delete=models.PROTECT,
        related_name='+',
    )

    class Meta:
        verbose_name = _("Invoice")
        verbose_name_plural = _("Invoices")


class InvoiceState:
    PAYMENT_PENDING = 'PENDING'
    PAID = 'PAID'
    TAXES_FILED = 'TAXFILED'


class State(models.Model):
    invoice = models.ForeignKey(
        Invoice,
        verbose_name=_("Invoice"),
        on_delete=models.CASCADE,
        related_name='states',
    )
    previous = models.OneToOneField(
        'State',
        verbose_name=_("Previous Transition"),
        on_delete=models.SET_NULL,
        related_name='next',
        blank=True,
    )
    timestamp = models.DateTimeField(
        _("Timestamp"),
        auto_now=True,
    )
    name = models.CharField(
        _("State"),
        max_length=20,
        choices=(
            (InvoiceState.PAYMENT_PENDING, _("Payment pending")),
            (InvoiceState.PAID, _("Paid")),
            (InvoiceState.TAXES_FILED, _("Taxes filed")),
        ),
        default=InvoiceState.PAYMENT_PENDING,
    )
