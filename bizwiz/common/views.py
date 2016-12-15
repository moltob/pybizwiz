from django.views.generic import TemplateView

from bizwiz.version import BIZWIZ_VERSION


class Welcome(TemplateView):
    template_name = 'common/welcome.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(version=BIZWIZ_VERSION, **kwargs)
