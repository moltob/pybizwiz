from bizwiz.invoices.models import Invoice


class InvoiceExporter:
    """
    Base class for exporting invoices into various formats.

    The caller may hold single instances of derived classes over lifetime, i.e. there must be no
    additional state associated with the instances. The typical usage pattern is that owner creates
    a map at runtime of the form:

        exports = {e.action_name: e for e in exporters}

    This means that implementations must keep all data within the context of the `export` call.

    mime_type (str):
        MIME type to use when sending export to client.

    action_name (str):
        Localized text to show to user in UI select box.
    """

    content_type = None
    action_name = None

    def export(self, invoice: Invoice, file):
        """
        Export invoice and return byte stream of exported data.

        Args:
            invoice: Invoice being exported.
            file: File-like object where to write data.
        """
        raise NotImplementedError
