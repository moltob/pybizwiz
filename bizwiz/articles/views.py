from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from bizwiz.articles.models import Article


class List(LoginRequiredMixin, ListView):
    model = Article
    paginate_by = 15

    @property
    def order_by(self):
        return self.request.GET.get('order_by', 'name')

    @property
    def order_dir(self):
        return self.request.GET.get('order_dir', 'asc')

    def get_ordering(self):
        if self.order_dir == 'asc':
            return self.order_by
        else:
            return '-{}'.format(self.order_by)

    def get_context_data(self, **kwargs):
        return super().get_context_data(order_by=self.order_by, order_dir=self.order_dir)
