"""Business services for invoices."""
import datetime
import logging

from django.db import models, transaction
from django.db import transaction
from django.db.models import functions

from bizwiz.invoices.models import Invoice, InvoicedCustomer, InvoicedArticle

_logger = logging.getLogger(__name__)


def pay_invoices(invoices):
    today = datetime.date.today()
    with transaction.atomic():
        for inv in invoices:
            _logger.info('Paying invoice id={}, number={}.'.format(inv.pk, inv.number))
            inv.date_paid = today
            inv.save()


def taxfile_invoices(invoices):
    today = datetime.date.today()
    with transaction.atomic():
        for inv in invoices:
            _logger.info('Filing taxes for invoice id={}, number={}.'.format(inv.pk, inv.number))
            inv.date_taxes_filed = today
            inv.save()


def delete_invoices(invoices):
    with transaction.atomic():
        for inv in invoices:
            _logger.info('Deleting invoice id={}, number={}.'.format(inv.pk, inv.number))
            inv.delete()


def get_next_invoice_number():
    """Returns next available invoice number. Should be called from within transaction."""
    converted_invoices = Invoice.objects.annotate(
        int_number=functions.Cast('number', models.IntegerField())
    )
    max_number = converted_invoices.aggregate(models.Max('int_number'))['int_number__max']
    next_number = max_number + 1 if max_number else 1
    return str(next_number)


def create_invoice(*, project, customer, article_dicts):
    """
    Creates a new invoice from data typically coming in through a posted form.

    Customer and articles are copied to allow editing them within the context of this invoice
    without modification of the original master data.

    Args:
        project:
            Project this invoice belongs to or `None`.
        customer:
            Customer the invoice is for (an existing, regular customer).
        article_dicts:
            List of dictionaries of invoiced articles.

    Returns:
        Stored invoice.
    """
    with transaction.atomic():
        invoice = Invoice()
        invoice.project = project
        invoice.number = get_next_invoice_number()
        invoice.save()
        customer = InvoicedCustomer.create(invoice, customer)
        customer.save()
        _logger.info('Creating new invoice {} for customer {}.'.format(invoice.number, customer))

        for article_dict in article_dicts:
            name = article_dict['name']
            price = article_dict['price']
            amount = article_dict['amount']
            # TODO: identify possibly referenced original article
            original_article = None
            article = InvoicedArticle.create(invoice, original_article, amount)
            article.name = name
            article.price = price
            article.save()
            _logger.debug('  {}, price: {}, amount: {}'.format(name, price, amount))

    return invoice
