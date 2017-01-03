import django_tables2 as tables
from django import urls
from django.contrib.auth import mixins
from django.contrib.messages import views
from django.db import models
from django.utils.translation import ugettext as _
from django.views import generic

from bizwiz.common.views import SizedColumnsMixin
from bizwiz.customers.forms import UpdateForm
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
        order_by = ('last_name', 'first_name')


class List(mixins.LoginRequiredMixin, SizedColumnsMixin, tables.SingleTableView):
    model = Customer
    table_class = CustomerTable
    column_widths = ('20%', '15%', '20%', '20%', '10%', '15%',)

    def get_queryset(self):
        self.queryset = Customer.objects.all()

        strfilter = self.request.GET.get('q')
        if strfilter:
            self.queryset = self.queryset.filter(models.Q(last_name__icontains=strfilter) |
                                                 models.Q(first_name__icontains=strfilter) |
                                                 models.Q(company_name__icontains=strfilter) |
                                                 models.Q(street_address__icontains=strfilter) |
                                                 models.Q(zip_code__icontains=strfilter) |
                                                 models.Q(city__icontains=strfilter))

        return super().get_queryset()


class EditMixin(views.SuccessMessageMixin):
    model = Customer
    success_url = urls.reverse_lazy('customers:list')
    form_class = UpdateForm

    def form_valid(self, form):
        if form.has_changed():
            self.success_message = _("Updated: %(last_name)s, %(first_name)s")
        else:
            self.success_message = ""
        return super().form_valid(form)


class Update(mixins.LoginRequiredMixin, EditMixin, generic.UpdateView):
    pass


class Create(mixins.LoginRequiredMixin, EditMixin, generic.CreateView):
    pass
