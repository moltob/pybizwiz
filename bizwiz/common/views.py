from django.views.generic import TemplateView

from bizwiz.version import BIZWIZ_VERSION


class Welcome(TemplateView):
    template_name = 'common/welcome.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(version=BIZWIZ_VERSION, **kwargs)


class SizedColumnsMixin:
    """Provides column sizes for table to HTML template."""
    column_widths = None

    def get_columns_widths(self):
        return self.column_widths

    def get_context_data(self, **kwargs):
        return super().get_context_data(column_widths=self.get_columns_widths(), **kwargs)
