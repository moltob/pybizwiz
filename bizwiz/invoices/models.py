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
from bizwiz.common.models import copy_field_data
from bizwiz.customers.models import CustomerBase, Customer
from bizwiz.projects.models import Project


class Invoice(models.Model):
    class Meta:
        verbose_name = _("Invoice")
        verbose_name_plural = _("Invoices")

    number = models.IntegerField(
        _("Invoice number"),
        unique=True,
    )
    date_created = models.DateField(
        _("Created"),
        default=datetime.date.today,
    )
    date_paid = models.DateField(
        _("Paid"),
        blank=True,
        null=True,
    )
    date_taxes_filed = models.DateField(
        _("Taxes filed"),
        blank=True,
        null=True,
    )
    project = models.ForeignKey(
        Project,
        verbose_name=_("Project"),
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )

    def __str__(self):
        return '{} ({})'.format(self.number, self.invoiced_customer.full_name())

    @property
    def total(self):
        """Total amount of invoice."""
        return sum(item.total for item in self.invoiced_articles.all())


class ItemKind:
    ARTICLE = 'ARTICLE'
    REBATE = 'REBATE'


class InvoicedArticle(ArticleBase):
    kind = models.CharField(
        _("Kind"),
        max_length=10,
        choices=(
            (ItemKind.ARTICLE, ItemKind.ARTICLE),
            (ItemKind.REBATE, ItemKind.REBATE),
        ),
        default=ItemKind.ARTICLE,
    )
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
        verbose_name=_("Invoice"),
        on_delete=models.CASCADE,
        related_name='invoiced_articles',
    )

    class Meta:
        verbose_name = _("Invoiced article")
        verbose_name_plural = _("Invoiced articles")

    @classmethod
    def create(cls, invoice, article, amount):
        invoiced_article = InvoicedArticle(invoice=invoice, original_article=article, amount=amount)
        if article:
            copy_field_data(ArticleBase, article, invoiced_article)
        return invoiced_article

    @property
    def total(self):
        return self.price * self.amount


# invoiced articles copy the article name and may be duplicates:
InvoicedArticle._meta.get_field('name')._unique = False


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
        verbose_name=_("Invoice"),
        on_delete=models.CASCADE,
        related_name='invoiced_customer',
    )

    class Meta:
        verbose_name = _("Invoiced customer")
        verbose_name_plural = _("Invoiced customers")

    @classmethod
    def create(cls, invoice, customer):
        invoiced_customer = InvoicedCustomer(invoice=invoice, original_customer=customer)
        copy_field_data(CustomerBase, customer, invoiced_customer)
        return invoiced_customer
