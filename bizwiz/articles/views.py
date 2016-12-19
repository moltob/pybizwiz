from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from bizwiz.articles.models import Article


class List(LoginRequiredMixin, ListView):
    model = Article
    paginate_by = 15
