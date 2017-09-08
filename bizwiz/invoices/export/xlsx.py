"""Excel export of invoice data."""
import logging
import operator

import xlsxwriter
from django.utils.translation import ugettext as _

from bizwiz.invoices.export.exporter import InvoiceExporter

_logger = logging.getLogger(__name__)


class InvoiceXlsxExporter(InvoiceExporter):
    content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    extension = 'xlsx'
    action_key = 'XLSX'
    action_name = _("Export to Excel")

    def export(self, invoices, fileobj):
        js_invoices = []

        workbook = xlsxwriter.Workbook(fileobj)
        self.export_invoices(workbook, invoices)
        workbook.close()

    def export_invoices(self, workbook, invoices):
        worksheet = workbook.add_worksheet(_("Income"))

        # built-in formats:
        currency_format = workbook.add_format({'num_format': 0x08})
        date_format = workbook.add_format({'num_format': 0x0E})

        worksheet.set_column(0, 0, 20)
        worksheet.set_column(1, 2, 15)
        worksheet.set_column(3, 4, 20)
        worksheet.set_column(5, 5, 15)

        data = [[
            invoice.number,
            invoice.date_created,
            invoice.date_paid,
            invoice.invoiced_customer.last_name,
            invoice.invoiced_customer.first_name,
            invoice.total,
        ] for invoice in sorted(invoices, key=operator.attrgetter('date_paid'))]

        worksheet.add_table(0, 0, len(data) + 1, 5, {
            'style': 'Table Style Light 18',
            'data': data,
            'total_row': True,
            'columns': [{
                'header': _("Invoice number"),
            }, {
                'header': _("Date created"),
                'format': date_format,
            }, {
                'header': _("Date paid"),
                'format': date_format,
            }, {
                'header': _("Last name"),
            }, {
                'header': _("First name"),
            }, {
                'header': _("Total"),
                'format': currency_format,
                'total_function': 'sum',
            }]
        })
