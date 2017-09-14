import logging
import os

from django import conf
from django.views import generic

from bizwiz.common.session_filter import set_session_filter
from bizwiz.version import BIZWIZ_VERSION

_logger = logging.getLogger(__name__)


class Welcome(generic.TemplateView):
    template_name = 'common/welcome.html'

    def get_context_data(self, **kwargs):

        # read an render changelog markdown:
        try:
            with open(os.path.join(conf.settings.BASE_DIR, 'CHANGELOG.md')) as changelogfile:
                changelog = changelogfile.read()
        except FileNotFoundError:
            _logger.warning('Changelog not found.')
            changelog = ''

        return super().get_context_data(
            version=BIZWIZ_VERSION,
            changelog=changelog,
            **kwargs
        )


class SizedColumnsMixin:
    """Provides column sizes for table to HTML template."""
    column_widths = None

    def get_columns_widths(self):
        return self.column_widths

    def get_context_data(self, **kwargs):
        return super().get_context_data(column_widths=self.get_columns_widths(), **kwargs)


class SessionFilter(generic.RedirectView):
    """Stores session filter (project and customer group) and returns to previous page."""

    def get(self, request, *args, **kwargs):
        # set session filter:
        project_pk = int(request.GET.get('project', '0'))
        customer_group_pk = int(request.GET.get('group', '0'))
        set_session_filter(request.session, project_pk, customer_group_pk)

        # return to calling page:
        self.url = request.GET['next']
        return super().get(request, *args, **kwargs)
