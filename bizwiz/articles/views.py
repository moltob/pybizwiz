from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from bizwiz.articles.models import Article
from bizwiz.common.views import PaginatedOrderedListView


class List(LoginRequiredMixin, PaginatedOrderedListView):
    model = Article
    ordering = 'name'
