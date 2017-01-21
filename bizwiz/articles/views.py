import django_tables2 as tables
from django import urls
from django.contrib.auth import mixins
from django.contrib.messages import views
from django.db import models
from django.utils.translation import ugettext as _
from django.views import generic

from bizwiz.articles.forms import UpdateForm, CreateForm, ArticleFormset
from bizwiz.articles.models import Article
from bizwiz.common.session_filter import get_session_filter
from bizwiz.common.views import SizedColumnsMixin


class ArticleTable(tables.Table):
    name = tables.LinkColumn('articles:update', args=[tables.utils.A('pk')])
    price = tables.Column(attrs={
        'th': {'class': 'text-right'},
        'td': {'class': 'text-right'}
    })
    inactive = tables.BooleanColumn(yesno='✔,', attrs={
        'th': {'class': 'text-center'},
        'td': {'class': 'text-center'},
    })

    class Meta:
        template = 'common/table.html'
        attrs = {'class': 'table table-striped'}
        per_page = 15
        model = Article
        fields = ('name', 'price', 'inactive')
        order_by = ('name',)


class List(mixins.LoginRequiredMixin, SizedColumnsMixin, tables.SingleTableView):
    model = Article
    table_class = ArticleTable
    column_widths = ('73%', '20%', '7%',)
    count_inactive = None

    def get_context_data(self, **kwargs):
        # pass view argument (from URL) to context:
        return super().get_context_data(show_inactive=self.kwargs['show_inactive'],
                                        count_inactive=self.count_inactive,
                                        **kwargs)

    def get_queryset(self):
        # apply project filter if active:
        filtered_project = get_session_filter(self.request.session).project
        if filtered_project:
            self.queryset = filtered_project.articles
        else:
            self.queryset = Article.objects.all()

        # only if requested, show inactive elements:
        if not self.kwargs['show_inactive']:
            self.count_inactive = self.queryset.filter(inactive=True).count()
            self.queryset = self.queryset.filter(inactive=False)

        strfilter = self.request.GET.get('q')
        if strfilter:
            self.queryset = self.queryset.filter(models.Q(name__icontains=strfilter) |
                                                 models.Q(price__icontains=strfilter))

        return super().get_queryset()

    def get_table(self, **kwargs):
        table = super().get_table(**kwargs)
        if self.kwargs['show_inactive']:
            table.exclude = ()
        else:
            table.exclude = ('inactive',)
        return table


class Update(mixins.LoginRequiredMixin, views.SuccessMessageMixin, generic.UpdateView):
    model = Article
    success_url = urls.reverse_lazy('articles:list_active')
    form_class = UpdateForm

    def form_valid(self, form):
        if form.has_changed():
            self.success_message = _("Updated: %(name)s")
        else:
            self.success_message = ""
        return super().form_valid(form)


class Create(mixins.LoginRequiredMixin, views.SuccessMessageMixin, generic.FormView):
    success_url = urls.reverse_lazy('articles:list_active')
    form_class = CreateForm
    template_name = 'articles/article_create.html'

    def get_context_data(self, **kwargs):
        if self.request.method in ('POST', 'PUT'):
            article_formset = ArticleFormset(self.request.POST)
        else:
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

        if article_formset.new_objects:
            names = (str(a) for a in article_formset.new_objects)

            if apply_session_filter(self.request.session, article_formset.new_objects):
                self.success_message = _("Added to current project: {}.").format(", ".join(names))
            else:
                self.success_message = _("Added: {}.").format(", ".join(names))
        else:
            self.success_message = ""

        return self.form_valid(form)


def apply_session_filter(session, articles):
    """If active, articles are added to filtered project and True is returned."""
    session_filter = get_session_filter(session)
    if session_filter.project:
        for article in articles:
            article.project_set.add(session_filter.project)
        return True
    return False
