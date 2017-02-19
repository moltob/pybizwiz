import django_tables2 as tables
from django import urls
from django.contrib.auth import mixins
from django.contrib.messages import views
from django.db import models
from django.db import transaction
from django.utils.translation import ugettext as _
from django.views import generic

from bizwiz.articles.models import Article, ArticleBase
from bizwiz.articles.services import get_articles_for_project
from bizwiz.common.session_filter import get_session_filter
from bizwiz.common.views import SizedColumnsMixin
from bizwiz.invoices import services
from bizwiz.invoices.forms import InvoiceAction, ListActionForm, UpdateForm, InvoicedCustomerForm, \
    InvoicedArticleFormset
from bizwiz.invoices.models import Invoice


class InvoiceTable(tables.Table):
    number = tables.LinkColumn('invoices:update', args=[tables.utils.A('pk')])
    invoiced_customer = tables.Column(_("Customer"), order_by=(
        'invoiced_customer.last_name',
        'invoiced_customer.first_name'
    ))
    project = tables.Column(_("Project"), order_by='project.name')
    total = tables.Column(order_by=tables.utils.A('total'), attrs={
        'th': {'class': 'text-right'},
        'td': {'class': 'text-right'}
    })
    selected = tables.CheckBoxColumn(accessor='pk', attrs={
        'th__input': {'id': 'id-select-all'},
    })

    class Meta:
        template = 'common/table.html'
        attrs = {'class': 'table table-striped'}
        per_page = 15
        model = Invoice
        fields = ('selected', 'number', 'invoiced_customer', 'date_created', 'date_paid',
                  'date_taxes_filed', 'project', 'total')
        order_by = ('-number',)

    def render_invoiced_customer(self, record: Invoice):
        return record.invoiced_customer.full_name()

    def order_total(self, queryset, descending):
        queryset = queryset.annotate(
            total=models.Sum(models.F('invoiced_articles__price') *
                             models.F('invoiced_articles__amount'))
        ).order_by(('-' if descending else '') + 'total')
        return queryset, True


class List(mixins.LoginRequiredMixin, SizedColumnsMixin, generic.edit.FormMixin,
           tables.SingleTableView):
    model = Invoice
    table_class = InvoiceTable
    column_widths = ('5%', '15%', '20%', '10%', '10%', '10%', '30%', '10%')
    form_class = ListActionForm
    success_url = urls.reverse_lazy('invoices:list')

    def get_queryset(self):
        # apply project filter if active:
        filtered_project = get_session_filter(self.request.session).project
        if filtered_project:
            self.queryset = Invoice.objects.filter(project=filtered_project)
        else:
            self.queryset = Invoice.objects.all()

        strfilter = self.request.GET.get('q')
        if strfilter:
            self.queryset = self.queryset.filter(
                models.Q(number__icontains=strfilter) |
                models.Q(date_created__icontains=strfilter) |
                models.Q(date_paid__icontains=strfilter) |
                models.Q(date_taxes_filed__icontains=strfilter) |
                models.Q(project__name__icontains=strfilter) |
                models.Q(invoiced_customer__first_name__icontains=strfilter) |
                models.Q(invoiced_customer__last_name__icontains=strfilter)
            )

        return super().get_queryset()

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            # provide object list for error page, which will need to reproduce the list:
            self.object_list = self.get_queryset()
            return self.form_invalid(form)

    def form_valid(self, form):
        action = form.cleaned_data['action']
        invoices = form.invoices

        if action == InvoiceAction.PAY:
            services.pay_invoices(invoices)
        elif action == InvoiceAction.TAX:
            services.taxfile_invoices(invoices)
        elif action == InvoiceAction.DELETE:
            services.delete_invoices(invoices)

        return super().form_valid(form)


class SelectableArticle:
    """Helper class holding article information to be shown in form, without DB relevance."""

    def __init__(self, article: ArticleBase):
        self.name = article.name
        self.price = article.price
        # only store PK of original articles:
        self.pk = article.pk if isinstance(article, Article) else 0

    def __eq__(self, other):
        # selection list only shows names:
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)


class EditMixin(views.SuccessMessageMixin):
    model = Invoice
    success_url = urls.reverse_lazy('invoices:list')
    form_class = UpdateForm
    specific_success_message = None

    @property
    def selectable_articles(self):
        # make sure user can pick from active articles (in project) _plus_ the ones currently used:
        visible_articles = get_articles_for_project(self.object.project)
        used_articles = self.object.invoiced_articles.all()

        selectable_articles = set()
        selectable_articles |= {SelectableArticle(a) for a in visible_articles}
        selectable_articles |= {SelectableArticle(a) for a in used_articles}
        selectable_articles = sorted(selectable_articles, key=lambda a: a.name)

        return selectable_articles

    def get_context_data(self, **kwargs):
        if self.request.method in ('POST', 'PUT'):
            invoiced_customer_form = InvoicedCustomerForm(self.request.POST,
                                                          instance=self.object.invoiced_customer)
            invoiced_article_formset = InvoicedArticleFormset(self.request.POST,
                                                              instance=self.object)
        else:
            invoiced_customer_form = InvoicedCustomerForm(instance=self.object.invoiced_customer)
            invoiced_article_formset = InvoicedArticleFormset(instance=self.object)

        return super().get_context_data(invoiced_customer_form=invoiced_customer_form,
                                        invoiced_article_formset=invoiced_article_formset,
                                        articles=self.selectable_articles,
                                        **kwargs)

    def post(self, request, *args, **kwargs):
        invoiced_customer_form = InvoicedCustomerForm(self.request.POST,
                                                      instance=self.object.invoiced_customer)
        invoiced_article_formset = InvoicedArticleFormset(self.request.POST,
                                                          instance=self.object)
        invoice_form = self.get_form()

        valid = True
        valid &= invoice_form.is_valid()
        valid &= invoiced_customer_form.is_valid()
        valid &= invoiced_article_formset.is_valid()

        if valid:
            return self.forms_valid(invoice_form, invoiced_customer_form, invoiced_article_formset)
        else:
            return self.form_invalid(invoice_form)

    def forms_valid(self, invoice_form, invoiced_customer_form, invoiced_article_formset):
        with transaction.atomic():
            invoice = invoice_form.save()
            invoiced_customer_form.instance.invoice = invoice
            invoiced_article_formset.instance = invoice
            invoiced_customer_form.save()
            invoiced_article_formset.save()
        if invoice_form.has_changed() \
                or invoiced_customer_form.has_changed() \
                or invoiced_article_formset.has_changed():
            self.success_message = self.specific_success_message
        else:
            self.success_message = ""
        return self.form_valid(invoice_form)


class Update(mixins.LoginRequiredMixin, EditMixin, generic.UpdateView):
    specific_success_message = _("Updated: Invoice %(number)s")
    template_name_suffix = '_update'

    def post(self, request, *args, **kwargs):
        # extract object being edited in form:
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)
