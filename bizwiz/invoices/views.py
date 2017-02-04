import django_tables2 as tables
from django import urls
from django.contrib.auth import mixins
from django.contrib.messages import views
from django.db import models
from django.db import transaction
from django.utils.translation import ugettext as _
from django.views import generic

from bizwiz.common.session_filter import get_session_filter
from bizwiz.common.views import SizedColumnsMixin
from bizwiz.invoices.forms import InvoiceAction, ListActionForm
from bizwiz.invoices.models import Invoice


class InvoiceTable(tables.Table):
    #number = tables.LinkColumn('invoices:list', args=[tables.utils.A('pk')])
    number = tables.LinkColumn('invoices:list')
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
            return self.form_invalid(form)
