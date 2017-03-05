import typing

from bizwiz.invoices.models import Invoice


class InvoiceExporter:
    """
    Base class for exporting invoices into various formats.

    The caller may hold single instances of derived classes over lifetime, i.e. there must be no
    additional state associated with the instances. The typical usage pattern is that owner creates
    a map at runtime of the form:

        exports = {e.action_name: e for e in exporters}

    This means that implementations must keep all data within the context of the `export` call.

    content_type (str):
        MIME type to use when sending export to client.

    extension (str):
        File extension used for downloaded file.

    action_key (str):
        Selection key for this action.

    action_name (str):
        Localized text to show to user in UI select box.
    """

    content_type = None
    extension = None
    action_key = None
    action_name = None

    def export(self, invoices: typing.List[Invoice], fileobj):
        """
        Export invoice and return byte stream of exported data.

        Args:
            invoices: List of invoices being exported.
            fileobj: File-like object to write data to.
        """
        raise NotImplementedError
