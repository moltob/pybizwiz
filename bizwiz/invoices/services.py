"""Business services for invoices."""
import datetime
import decimal
import logging

from django import http
from django.db import models
from django.db import transaction
from djmoney import money

from bizwiz.articles.models import Article
from bizwiz.invoices.export.js import InvoiceJsonExporter
from bizwiz.invoices.export.pdf import InvoicePdfExporter, InvoicePdfFullLetterheadExporter
from bizwiz.invoices.export.xlsx import InvoiceXlsxExporter
from bizwiz.invoices.models import Invoice, InvoicedCustomer, ItemKind, InvoicedArticle
from bizwiz.rebates.models import RebateKind, Rebate

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


def create_invoice(*, customer, invoiced_articles=None, project=None, rebates=None):
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
        rebates (Optional[List[Rebate]]:
            List of rebates applied to invoice.

    Returns (Invoice):
        Stored invoice.
    """
    invoice = Invoice()
    invoice.project = project
    invoice.number = get_next_invoice_number()
    invoice.save()
    if rebates:
        invoice.rebates.set(rebates)
        invoice.save()
    customer = InvoicedCustomer.create(invoice, customer)
    customer.save()
    _logger.info('Creating new invoice {} for customer {}.'.format(invoice.number, customer))

    if invoiced_articles:
        for invoiced_article in invoiced_articles:
            invoiced_article.invoice = invoice
            invoiced_article.save()
            _logger.debug('  {}'.format(invoiced_article))

    refresh_rebates(invoice)
    return invoice


INVOICE_EXPORTER_MAP = {e.action_key: e for e in (
    InvoicePdfExporter(),
    InvoicePdfFullLetterheadExporter(),
    InvoiceJsonExporter(),
    InvoiceXlsxExporter(),
)}


def export_invoices(invoices, exporter_key, *, as_attachment=True):
    exporter = INVOICE_EXPORTER_MAP.get(exporter_key)
    if not exporter:
        _logger.error('Cannot execute unknown action {!r}.'.format(exporter_key))
        return None

    if len(invoices) == 1:
        filename = 'invoice-{}.{}'.format(invoices[0].number, exporter.extension)
    else:
        filename = 'invoices.{}'.format(exporter.extension)

    response = http.HttpResponse(content_type=exporter.content_type)

    if as_attachment:
        response['Content-Disposition'] = 'attachment;filename="{}"'.format(filename)
    else:
        response['Content-Disposition'] = 'filename="{}"'.format(filename)

    exporter.export(invoices, response)
    return response


def apply_rebate_one_free_per(invoice: Invoice, rebate: Rebate):
    article_items = (i for i in invoice.invoiced_articles.all() if i.kind == ItemKind.ARTICLE)
    for item in article_items:
        rebate_amount = int(rebate.value)
        if rebate_amount < 2:
            _logger.warning('Application rebate amount {} not feasible.'.format(rebate_amount))
            return

        rebate_count = item.amount // rebate_amount
        if rebate_count:
            _logger.debug('Applying rebate {} times for article {} invoiced {} times.'.format(
                rebate_count,
                item.name,
                item.amount
            ))

            rebate_text = "{} ({})".format(rebate.name, item.name)
            rebate_item = InvoicedArticle(invoice=invoice, name=rebate_text, price=-item.price,
                                          amount=rebate_count, kind=ItemKind.REBATE)
            rebate_item.save()
            _logger.debug('Computed rebate item {}.'.format(rebate_item))


def apply_rebate_percentage(invoice: Invoice, rebate: Rebate):
    if rebate.value <= 0:
        _logger.warning('Deducting a negative or null percentage is not feasible.')
        return

    factor_percent = decimal.Decimal('0.01')
    rebate_price = -invoice.total * rebate.value * factor_percent
    rebate_item = InvoicedArticle(invoice=invoice, name=rebate.name, price=rebate_price, amount=1,
                                  kind=ItemKind.REBATE)
    rebate_item.save()
    _logger.debug('Computed rebate item {}.'.format(rebate_item))


def apply_rebate_absolute(invoice: Invoice, rebate: Rebate):
    if rebate.value <= 0:
        _logger.warning('Deducting a negative or null amount is not feasible.')
        return

    # turn generic value into money value with matching currency:
    value = money.Money(rebate.value, invoice.total.currency)

    if value < invoice.total:
        rebate_price = -value
    else:
        _logger.debug('Rebate of {} is more than invoice total {}, limiting rebate.'.format(
            value,
            invoice.total,
        ))
        rebate_price = -invoice.total

    rebate_item = InvoicedArticle(invoice=invoice, name=rebate.name, price=rebate_price, amount=1,
                                  kind=ItemKind.REBATE)
    rebate_item.save()
    _logger.debug('Computed rebate item {}.'.format(rebate_item))


APPLY_REBATE = {
    RebateKind.ONE_FREE_PER: apply_rebate_one_free_per,
    RebateKind.PERCENTAGE: apply_rebate_percentage,
    RebateKind.ABSOLUTE: apply_rebate_absolute,
}


def refresh_rebates(invoice: Invoice):
    """
    Recomputes invoice items based on rebate rules.

    Args:
        invoice: Invoice for which to recompute rebates.

    """
    _logger.debug('Recomputing rebates for invoice number {}.'.format(invoice.number))

    # get rid of existing rebate items first:
    _, num_deleted = invoice.invoiced_articles.filter(kind=ItemKind.REBATE).delete()
    _logger.debug('Deleted {} old rebate items from invoice.'.format(num_deleted))

    for rebate in sorted(invoice.rebates.all(), key=lambda r: r.evaluation_index):
        _logger.debug('Applying rebate {}.'.format(rebate))
        APPLY_REBATE[rebate.kind](invoice, rebate)

    invoice.save()
