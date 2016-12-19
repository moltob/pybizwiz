from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import ugettext as _
from django.views.generic import ListView, UpdateView

from bizwiz.articles.forms import UpdateForm
from bizwiz.articles.models import Article
from bizwiz.common.views import OrderedListViewMixin


class List(LoginRequiredMixin, OrderedListViewMixin, ListView):
    model = Article
    ordering = 'name'
    paginate_by = 15

    def get_context_data(self, **kwargs):
        # pass view argument (from URL) to context:
        return super().get_context_data(show_inactive=self.kwargs['show_inactive'], **kwargs)

    def get_queryset(self):
        self.queryset = Article.objects.all()

        # only show inactive elements if requested:
        if not self.kwargs['show_inactive']:
            self.queryset = self.queryset.filter(inactive=False)

        return super().get_queryset()


class Update(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = Article
    success_message = _("Article %(name) has been updated.")
    success_url = reverse_lazy('articles:list')
    form_class = UpdateForm
