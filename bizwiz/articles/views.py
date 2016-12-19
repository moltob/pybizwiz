from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from bizwiz.articles.models import Article
from bizwiz.common.views import OrderedListViewMixin


class List(LoginRequiredMixin, OrderedListViewMixin, ListView):
    model = Article
    ordering = 'name'
    paginate_by = 15

    def get_context_data(self, **kwargs):
        return super().get_context_data(show_inactive=self.kwargs['show_inactive'], **kwargs)

    def get_queryset(self):
        self.queryset = Article.objects.all()
        if not self.kwargs['show_inactive']:
            self.queryset = self.queryset.filter(inactive=False)
        return super().get_queryset()
