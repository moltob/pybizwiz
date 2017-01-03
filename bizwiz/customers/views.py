import django_tables2 as tables
from django.contrib.auth import mixins
from django.core import paginator
from django.views import generic

from bizwiz.common.views import OrderedListViewMixin
from bizwiz.customers.models import Customer


class CustomerTable(tables.Table):
    last_name = tables.LinkColumn('customers:update', args=[tables.utils.A('pk')])
    first_name = tables.LinkColumn('customers:update', args=[tables.utils.A('pk')])

    class Meta:
        template = 'common/table.html'
        attrs = {'class': 'table table-striped'}
        per_page = 15
        model = Customer
        fields = ('last_name', 'first_name', 'company_name', 'street_address', 'zip_code', 'city',)


class List(mixins.LoginRequiredMixin, tables.SingleTableMixin, generic.ListView):
    model = Customer
    table_class = CustomerTable
    widths = ('20%', '15%', '20%', '20%', '5%', '20%',)

    def get_context_data(self, **kwargs):
        return super().get_context_data(widths=self.widths)
