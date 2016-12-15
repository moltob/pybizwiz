from django.views.generic import ListView

from bizwiz.articles.models import Article


class List(ListView):
    model = Article
