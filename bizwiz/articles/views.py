from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.utils.translation import ugettext as _
from django.views.generic import FormView
from django.views.generic import ListView, UpdateView

from bizwiz.articles.forms import UpdateForm, CreateForm, ArticleFormset
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
    success_url = reverse_lazy('articles:list_active')
    form_class = UpdateForm

    def form_valid(self, form):
        if form.has_changed():
            self.success_message = _("Updated: %(name)s")
        else:
            self.success_message = ""
        return super().form_valid(form)


class Create(LoginRequiredMixin, SuccessMessageMixin, FormView):
    success_url = reverse_lazy('articles:list_active')
    form_class = CreateForm
    template_name = 'articles/article_create.html'

    def get_context_data(self, **kwargs):
        article_formset = ArticleFormset(queryset=Article.objects.none())
        return super().get_context_data(formset=article_formset, **kwargs)

    def post(self, request, *args, **kwargs):
        article_formset = ArticleFormset(request.POST)
        form = self.get_form()  # type: CreateForm

        if form.is_valid() and article_formset.is_valid():
            return self.forms_valid(form, article_formset)
        else:
            return self.form_invalid(form)

    def forms_valid(self, form, article_formset):
        article_formset.save()
        return self.form_valid(form)
