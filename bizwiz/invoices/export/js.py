"""JSON export of invoice data."""
import decimal
import json
import logging

from django.utils.translation import ugettext as _

from bizwiz.invoices.export.exporter import InvoiceExporter

_logger = logging.getLogger(__name__)


class InvoiceJsonExporter(InvoiceExporter):
    content_type = 'application/json'
    extension = 'json'
    action_key = 'JSON'
    action_name = _("Export JSON")

    def export(self, invoices, fileobj):
        js_invoices = []

        for invoice in invoices:
            _logger.info('Exporting invoice id={}, number={}.'.format(invoice.pk, invoice.number))

            js_invoice = dict(
                number=invoice.number,
                date_created=invoice.date_created,
                date_paid=invoice.date_paid,
                date_taxes_filed=invoice.date_taxes_filed,
                last_name=invoice.invoiced_customer.last_name,
                first_name=invoice.invoiced_customer.first_name,
                total=invoice.total.quantize(decimal.Decimal('1.00'))
            )
            js_invoices.append(js_invoice)

        js_obj = dict(
            version=1,
            invoices=js_invoices
        )

        json.dump(js_obj, fileobj, default=lambda o: str(o), indent=2)
