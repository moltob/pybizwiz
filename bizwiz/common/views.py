from django.views.generic import TemplateView


class Welcome(TemplateView):
    template_name = 'common/welcome.html'
