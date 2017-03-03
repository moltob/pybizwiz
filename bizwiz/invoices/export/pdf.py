import functools
import locale
import logging

from django.utils.translation import ugettext as _

from bizwiz.customers.models import Salutation
from bizwiz.invoices.export.exporter import InvoiceExporter
from bizwiz.invoices.export.template_pdf_bpf_2017 import BpfInvoiceDocTemplate
from bizwiz.invoices.models import Invoice
from bwsite import settings

_logger = logging.getLogger(__name__)


class InvoicePdfExporter(InvoiceExporter):
    content_type = 'x-application/pdf'
    action_key = 'PRINT'
    action_name = _("Export/print PDF (BPF German)")

    def export(self, invoice: Invoice, file):
        doc = BpfInvoiceDocTemplate(file, TextBlocks(invoice))
        doc.build(doc.flowables)


class TextBlocks:
    """Container for text blocks used on page."""

    def __init__(self, invoice):
        self.invoice = invoice

    @property
    def clause_date(self):
        return "Grafrath, den {:%d.%m.%Y}".format(self.invoice.date_created)

    @property
    def clause_subject(self):
        return "Ihre Rechnung R{:06d}".format(self.invoice.number)

    @property
    def clause_salutation(self):
        customer = self.invoice.invoiced_customer
        clause = []
        if customer.salutation == Salutation.MR:
            clause.append("Sehr geehrter Herr")
        elif customer.salutation == Salutation.MRS:
            clause.append("Sehr geehrter Frau")
        elif customer.salutation == Salutation.FAMILY:
            clause.append("Sehr geehrte Familie")
        else:
            _logger.error('Unknown saluation type {!r}.'.format(customer.salutation))
            clause.append("Sehr geehrter Herr")
        clause.append(customer.last_name + ',')
        return ' '.join(clause)

    @property
    def clause_body_top(self):
        return "für die ausgeführten Fotoarbeiten erlaube ich mir die folgenden Beträge zu " \
               "berechnen:"

    @property
    def clause_body_bottom(self):
        return "Bitte überweisen Sie den Gesamtbetrag innerhalb von 14 Tagen nach Erhalt dieser " \
               "Rechnung unter Angabe der Rechnungsnummer auf das Konto der Deutschen Kreditbank " \
               "AG, IBAN: DE81120300001008185538, BIC: BYLADEM1001."

    @property
    def clause_taxinfo(self):
        return "Es handelt sich um eine steuerfreie Leistung eines Kleinunternehmers gemäß §19 " \
               "UStG."

    @property
    def clause_closing(self):
        return "Mit freundlichen Grüßen"

    @property
    def clause_signature(self):
        return "Ihre Britta Pagel"

    def iter_article_rows(self):
        currency = functools.partial(locale.currency, grouping=True)

        yield ['Artikel', 'Stückpreis', 'Anzahl', 'Gesamt']
        for item in self.invoice.invoiced_articles.iterator():
            yield [item.name, currency(item.price), item.amount, currency(item.total)]
        yield [None, None, None, currency(self.invoice.total)]

    def iter_address_field_lines(self):
        customer = self.invoice.invoiced_customer

        if customer.company_name:
            yield customer.company_name

        if customer.salutation == Salutation.MR:
            yield "Herrn"
        elif customer.salutation == Salutation.MRS:
            yield "Frau"
        elif customer.salutation == Salutation.FAMILY:
            yield "Familie"

        name = []
        if customer.title:
            name.append(customer.title)
        if customer.first_name:
            name.append(customer.first_name)
        if customer.last_name:
            name.append(customer.last_name)
        if name:
            yield ' '.join(name)

        if customer.street_address:
            yield customer.street_address

        city = []
        if customer.zip_code:
            city.append(customer.zip_code)
        if customer.city:
            city.append(customer.city)
        if city:
            yield ' '.join(city)
