from django.views.generic import TemplateView

from bizwiz.exceptions import IncorrectViewConfigurationError
from bizwiz.version import BIZWIZ_VERSION


class Welcome(TemplateView):
    template_name = 'common/welcome.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(version=BIZWIZ_VERSION, **kwargs)


class SizedColumnsMixin:
    """Provides column sizes for table to HTML template."""
    column_widths = None

    def get_context_data(self, **kwargs):
        return super().get_context_data(column_widths=self.column_widths)


class OrderedListViewMixin:
    @property
    def order_by(self):
        if not self.ordering:
            raise IncorrectViewConfigurationError('Default ordering not set.')
        return self.request.GET.get('order_by', self.ordering)

    @property
    def order_dir(self):
        return self.request.GET.get('order_dir', 'asc')

    def get_ordering(self):
        if self.order_dir == 'asc':
            return self.order_by
        else:
            return '-{}'.format(self.order_by)

    def get_context_data(self, **kwargs):
        return super().get_context_data(order_by=self.order_by, order_dir=self.order_dir, **kwargs)
