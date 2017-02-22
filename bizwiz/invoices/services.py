"""Business services for invoices."""
import datetime
import logging

from django.db import models, transaction
from django.db import transaction
from django.db.models import functions

from bizwiz.articles.models import Article
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
    max_number = Invoice.objects.aggregate(models.Max('number'))['number__max']
    next_number = max_number + 1 if max_number else 1
    return next_number


def create_invoice(*, customer, invoiced_articles=None, project=None):
    """
    Creates a new invoice from data typically coming in through a posted form.

    Customer and articles are copied to allow editing them within the context of this invoice
    without modification of the original master data.

    Args:
        project (Optional[Project])):
            Project this invoice belongs to or `None`.
        customer (Customer):
            Customer the invoice is for (an existing, regular customer).
        invoiced_articles (Optional[List[InvoicedArticle]]):
            List of invoiced articles to be added to new invoice.

    Returns (Invoice):
        Stored invoice.
    """
    invoice = Invoice()
    invoice.project = project
    invoice.number = get_next_invoice_number()
    invoice.save()
    customer = InvoicedCustomer.create(invoice, customer)
    customer.save()
    _logger.info('Creating new invoice {} for customer {}.'.format(invoice.number, customer))

    if invoiced_articles:
        # get articles from database by names:
        names = {a.name for a in invoiced_articles}
        articles = Article.objects.filter(name__in=names)
        article_by_name = {a.name: a for a in articles}

        for invoiced_article in invoiced_articles:
            original_article = article_by_name.get(invoiced_article.name)
            invoiced_article.invoice = invoice
            invoiced_article.original_article = original_article
            invoiced_article.save()
            _logger.debug('  {}'.format(invoiced_article))

    return invoice
