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
from bizwiz.customers.services import get_session_filtered_customers, apply_session_filter


class CustomerTable(tables.Table):
    last_name = tables.LinkColumn('customers:update', args=[tables.utils.A('pk')])
    first_name = tables.LinkColumn('customers:update', args=[tables.utils.A('pk')])

    class Meta:
        template = 'common/table.html'
        attrs = {'class': 'table table-striped'}
        per_page = 50
        model = Customer
        fields = ('last_name', 'first_name', 'company_name', 'street_address', 'zip_code', 'city',)
        order_by = ('last_name', 'first_name')


class List(mixins.LoginRequiredMixin, SizedColumnsMixin, tables.SingleTableView):
    model = Customer
    table_class = CustomerTable
    column_widths = ('20%', '15%', '20%', '20%', '10%', '15%',)

    def get_queryset(self):
        # apply session filter if set:
        self.queryset = get_session_filtered_customers(self.request.session)

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
    specific_success_message = None

    def form_valid(self, form):
        if form.has_changed():
            self.success_message = self.specific_success_message
        else:
            self.success_message = ""
        return super().form_valid(form)


class Update(mixins.LoginRequiredMixin, EditMixin, generic.UpdateView):
    specific_success_message = _("Updated: %(last_name)s, %(first_name)s")


class Create(mixins.LoginRequiredMixin, EditMixin, generic.CreateView):
    specific_success_message = None

    def form_valid(self, form):
        if form.has_changed():
            # must save new instance before it (possibly) can be added to active customer group:
            form.save()

            # apply session filter to new customer if set:
            if apply_session_filter(self.request.session, form.instance):
                self.specific_success_message = _("Added to current customer group: "
                                                  "%(last_name)s, %(first_name)s")
            else:
                self.specific_success_message = _("Added: %(last_name)s, %(first_name)s")

        return super().form_valid(form)


