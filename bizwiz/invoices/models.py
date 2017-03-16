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

# TODO *** Rebate System
#
# User defines rebate rules. Available rules and their properties:
# * PercentageRebate (percent of total, e.g. 8%)
# * AmountRebate (number of free items per total number of items, e.g. 1 of 10)
# * AbsoluteRebate (absolute discount, e.g. 5€)
#
# All rebates have a common properties:
# * name, just like article
# * default activation, flag whether a rebate is applied automatically for new invoices
#
# Rebates are applied to an invoice at the very end, simply by activating them. Text and parameter
# of the rebate can be overwritten in the context of the invoice.
#
# TODO *** Rebate System

class Invoice(models.Model):
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

    class Meta:
        verbose_name = _("Invoice")
        verbose_name_plural = _("Invoices")

    def __str__(self):
        return '{} ({})'.format(self.number, self.invoiced_customer.full_name())

    @property
    def total(self):
        """Total amount of invoice."""
        return sum(item.total for item in self.invoiced_articles.all())


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


def copy_field_data(model, src, dst):
    """Copies all non-automatic fields.

    Helper useful when copying common base class data.

    :model: Model class for which fields are copied, a common ancestor of src and dst.
    :src: Instance from which field data is copied.
    :dst: Instance to which field data is copied.
    """
    for field in model._meta.get_fields():
        if not (isinstance(field, models.AutoField) or isinstance(field, models.BigAutoField)):
            name = field.name
            value = getattr(src, name)
            setattr(dst, name, value)
