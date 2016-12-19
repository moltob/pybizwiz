from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from bizwiz.articles.models import Article
from bizwiz.common.views import OrderedListViewMixin


class List(LoginRequiredMixin, OrderedListViewMixin, ListView):
    model = Article
    ordering = 'name'
    paginate_by = 15
