import logging

import django_tables2 as tables
from django import shortcuts
from django import urls, views
from django.contrib.auth import mixins
from django.contrib.messages import views as message_views
from django.db import models
from django.db import transaction
from django.db.models import functions
from django.utils.translation import ugettext as _
from django.views import generic

from bizwiz.articles.models import ArticleBase
from bizwiz.articles.services import get_articles_for_project, get_session_filtered_articles
from bizwiz.common.session_filter import get_session_filter
from bizwiz.common.views import SizedColumnsMixin
from bizwiz.customers.services import get_session_filtered_customers
from bizwiz.invoices import services
from bizwiz.invoices.forms import InvoiceAction, ListActionForm, UpdateForm, InvoicedCustomerForm, \
    InvoicedArticleFormset, CreateForm
from bizwiz.invoices.models import Invoice, InvoicedArticle, ItemKind
from bizwiz.invoices.tables import COLUMN_RIGHT_ALIGNED, SummingColumn, SummingLinkColumn
from bizwiz.rebates.models import Rebate

_logger = logging.getLogger(__name__)


class InvoiceTable(tables.Table):
    number = tables.LinkColumn('invoices:update', args=[tables.utils.A('pk')])
    print = tables.LinkColumn(
        'invoices:print',
        args=[tables.utils.A('number')],
        orderable=False,
        text='',
        verbose_name='', attrs={'a': {'class': 'glyphicon glyphicon-print'}},
    )
    invoiced_customer = tables.Column(
        _("Customer"),
        order_by=('invoiced_customer.last_name', 'invoiced_customer.first_name')
    )
    project = tables.Column(_("Project"), order_by='project.name')
    total = tables.Column(
        _("Total"),
        order_by=tables.utils.A('total'),
        attrs=COLUMN_RIGHT_ALIGNED
    )
    selected = tables.CheckBoxColumn(
        accessor='pk',
        attrs={'th__input': {'id': 'id-select-all'}}
    )

    class Meta:
        template = 'common/table.html'
        attrs = {'class': 'table table-striped'}
        per_page = 50
        model = Invoice
        fields = ('selected', 'number', 'invoiced_customer', 'date_created', 'date_paid',
                  'date_taxes_filed', 'project', 'total', 'print')
        order_by = ('-number',)

    def render_invoiced_customer(self, record: Invoice):
        return record.invoiced_customer.full_name()

    def order_total(self, queryset, descending):
        queryset = queryset.annotate(
            _total=models.Sum(models.F('invoiced_articles__price') *
                              models.F('invoiced_articles__amount'))
        ).order_by(('-' if descending else '') + '_total')
        return queryset, True


class List(mixins.LoginRequiredMixin, SizedColumnsMixin, generic.edit.FormMixin,
           tables.SingleTableView):
    model = Invoice
    table_class = InvoiceTable
    column_widths = ('5%', '15%', '20%', '10%', '10%', '10%', '25%', '10%', '5%')
    form_class = ListActionForm
    success_url = urls.reverse_lazy('invoices:list')

    def get_queryset(self):
        # apply project filter if active:
        filtered_project = get_session_filter(self.request.session).project
        if filtered_project:
            self.queryset = Invoice.objects.filter(project=filtered_project)
        else:
            self.queryset = Invoice.objects.all()

        subset = self.kwargs.get('subset')
        if subset == 'payable':
            self.queryset = self.queryset.filter(date_paid__isnull=True)
        elif subset == 'taxable':
            self.queryset = self.queryset.filter(date_paid__isnull=False,
                                                 date_taxes_filed__isnull=True)
        elif subset == 'year_paid':
            self.queryset = self.queryset.filter(date_paid__year=self.kwargs['year'])
        elif subset:
            _logger.warning(f'Unexpected subset {subset!r}.')

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
        else:
            response = services.export_invoices(invoices, action)
            if response:
                return response

        return super().form_valid(form)


class SelectableArticle:
    """Helper class holding article information to be shown in form, without DB relevance."""

    def __init__(self, article: ArticleBase):
        self.name = article.name
        self.price = article.price

    def __eq__(self, other):
        # selection list only shows names:
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)


class Update(mixins.LoginRequiredMixin, message_views.SuccessMessageMixin, generic.UpdateView):
    model = Invoice
    form_class = UpdateForm
    specific_success_message = _("Updated: Invoice %(number)s")
    template_name_suffix = '_update'
    success_url = urls.reverse_lazy('invoices:list')

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

        rebates = Rebate.objects.order_by('name')

        return super().get_context_data(invoiced_customer_form=invoiced_customer_form,
                                        invoiced_article_formset=invoiced_article_formset,
                                        articles=self.selectable_articles,
                                        rebates=rebates,
                                        **kwargs)

    def post(self, request, *args, **kwargs):
        # extract object being edited in form:
        self.object = self.get_object()

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
                services.refresh_rebates(invoice)
                self.success_message = self.specific_success_message
            else:
                self.success_message = ""
        return self.form_valid(invoice_form)


class SelectableCustomer:
    def __init__(self, customer):
        self.name = str(customer)
        self.pk = customer.pk


class Create(mixins.LoginRequiredMixin, message_views.SuccessMessageMixin, generic.FormView):
    template_name = 'invoices/invoice_create.html'
    form_class = CreateForm
    success_message = _("Created: Invoice for %(customer)s")
    success_url = urls.reverse_lazy('invoices:list')

    def get_initial(self):
        # for new invoices pre-set automatic rebates:
        initial = super().get_initial()
        initial.update(rebates=Rebate.objects.filter(auto_apply=True).order_by('name'))
        return initial

    def get_context_data(self, **kwargs):
        customers = get_session_filtered_customers(self.request.session).order_by(
            'last_name',
            'first_name',
            'company_name'
        )
        articles = get_session_filtered_articles(self.request.session).order_by(
            'name'
        )
        selectable_customers = [SelectableCustomer(c) for c in customers]
        selectable_articles = [SelectableArticle(a) for a in articles]
        rebates = Rebate.objects.order_by('name')

        if self.request.method in ('POST', 'PUT'):
            invoiced_article_formset = InvoicedArticleFormset(self.request.POST)
        else:
            invoiced_article_formset = InvoicedArticleFormset()

        return super().get_context_data(customers=selectable_customers,
                                        articles=selectable_articles,
                                        invoiced_article_formset=invoiced_article_formset,
                                        rebates=rebates,
                                        **kwargs)

    def post(self, request, *args, **kwargs):
        invoice_form = self.get_form()
        invoiced_article_formset = InvoicedArticleFormset(self.request.POST)

        if invoice_form.is_valid() & invoiced_article_formset.is_valid():
            return self.forms_valid(invoice_form, invoiced_article_formset)
        else:
            return self.form_invalid(invoice_form)

    def forms_valid(self, invoice_form, invoiced_article_formset):
        project = get_session_filter(self.request.session).project
        original_customer = invoice_form.cleaned_data['customer']
        rebates = invoice_form.cleaned_data['rebates']

        with transaction.atomic():
            invoiced_articles = invoiced_article_formset.save(commit=False)
            invoice = services.create_invoice(
                project=project,
                invoiced_articles=invoiced_articles,
                customer=original_customer,
                rebates=rebates,
            )

            # DEFECT:
            # original article is not set this way
            #   --> incomplete data
            #   --> incorrect article sales report
            # TODO: try to make use of full create_invoice API, do not take shortcut of formset
            # TODO: clean up data by reading article references via name comparison
            # TODO: implement report based on invoiced article names, not from original one
            # TODO: remove "original" references (article and customer) if possible

        return self.form_valid(invoice_form)


class Print(views.View):
    def get(self, request, number):
        invoice = shortcuts.get_object_or_404(Invoice, number=number)
        return services.export_invoices([invoice], 'PDF', as_attachment=False)


class SalesTable(tables.Table):
    year_paid = tables.Column(_('Year'))
    num_invoices = SummingLinkColumn(
        verbose_name=_('Invoices'),
        viewname='invoices:sales',
        args=[tables.utils.A('year_paid')],
        attrs=COLUMN_RIGHT_ALIGNED
    )
    num_articles = SummingLinkColumn(
        verbose_name=_('Articles'),
        viewname='invoices:sales_articles',
        args=[tables.utils.A('year_paid')],
        attrs=COLUMN_RIGHT_ALIGNED
    )
    total = SummingColumn(_('Yearly income'), attrs=COLUMN_RIGHT_ALIGNED)

    class Meta:
        template = 'common/table.html'
        attrs = {'class': 'table table-striped'}
        per_page = 50
        order_by = ('-year_paid',)


class Sales(mixins.LoginRequiredMixin, SizedColumnsMixin, tables.SingleTableView):
    """Sales per year."""
    table_class = SalesTable
    column_widths = ('10%', '20%', '30%', '40%',)
    queryset = Invoice.objects \
        .exclude(date_paid=None) \
        .annotate(year_paid=functions.ExtractYear('date_paid')) \
        .values('year_paid') \
        .filter(invoiced_articles__kind=ItemKind.ARTICLE) \
        .annotate(num_invoices=models.Count('id', distinct=True),
                  num_articles=models.Sum('invoiced_articles__amount'),
                  total=models.Sum(
                      models.F('invoiced_articles__price') * models.F('invoiced_articles__amount')
                  ))
    template_name = 'invoices/sales_list.html'

    def get_context_data(self, **kwargs):
        # prepare chart data by separating x and y axis:
        sales_years = [p['year_paid'] for p in self.queryset]
        sales_totals = [p['total'] for p in self.queryset]

        return super().get_context_data(sales_years=sales_years,
                                        sales_totals=sales_totals,
                                        **kwargs)


class ArticleSalesTable(tables.Table):
    name = tables.LinkColumn(
        'articles:update',
        args=[tables.utils.A('original_article__pk')],
        verbose_name=_("Invoice text"),
        accessor='original_article__name'
    )
    amount = tables.Column(_("Ordered"), accessor='year_amount', attrs=COLUMN_RIGHT_ALIGNED)
    total = tables.Column(_('Total value'), attrs=COLUMN_RIGHT_ALIGNED)

    class Meta:
        template = 'common/table.html'
        attrs = {'class': 'table table-striped'}
        per_page = 50
        order_by = ('-amount',)


class ArticleSales(mixins.LoginRequiredMixin, SizedColumnsMixin, tables.SingleTableView):
    table_class = ArticleSalesTable
    column_widths = ('50%', '20%', '30%',)
    template_name = 'invoices/article_sales_list.html'

    def get_queryset(self):
        return InvoicedArticle.objects \
            .filter(kind=ItemKind.ARTICLE, original_article__isnull=False) \
            .filter(price__gt=0) \
            .filter(invoice__date_paid__year=self.kwargs['year']) \
            .values('original_article__pk', 'original_article__name') \
            .annotate(year_amount=models.Sum('amount'),
                      total=models.Sum(models.F('price') * models.F('amount'))) \
            .order_by('-year_amount')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(year=self.kwargs['year'], **kwargs)

        # prepare chart data by separating x and y axis:
        queryset = context['object_list']
        article_amounts = [a['year_amount'] for a in queryset]
        article_names = [a['original_article__name'] for a in queryset]

        # clear names of articles with minor contribution:
        total_amount = sum(article_amounts)
        percentage_amounts = [a / total_amount for a in article_amounts]
        article_names = [n if percentage_amounts[i] > 0.03 else " "
                         for i, n in enumerate(article_names)]

        context.update(article_names=article_names, article_amounts=article_amounts)
        return context
