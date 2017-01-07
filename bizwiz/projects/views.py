import django_tables2 as tables
from django import urls
from django.contrib.auth import mixins
from django.contrib.messages import views
from django.utils.translation import ugettext as _
from django.views import generic

from bizwiz.common.views import SizedColumnsMixin
from bizwiz.projects.forms import UpdateForm, CustomerGroupFormset
from bizwiz.projects.models import Project, CustomerGroup


class ProjectTable(tables.Table):
    name = tables.LinkColumn('projects:update', args=[tables.utils.A('pk')])
    customergroups = tables.Column(_("Customer Groups"), empty_values=(), orderable=False)

    class Meta:
        template = 'common/table.html'
        attrs = {'class': 'table table-striped'}
        per_page = 15
        model = Project
        fields = ('start_date', 'name', 'customergroups')
        order_by = ('-start_date',)

    def render_customergroups(self, record: Project):
        return ', '.join(g.name for g in record.customergroup_set.all().order_by('name'))


class List(mixins.LoginRequiredMixin, SizedColumnsMixin, tables.SingleTableView):
    model = Project
    table_class = ProjectTable
    column_widths = ('10%', '30%', '60%')

    def get_queryset(self):
        self.queryset = Project.objects.all()

        strfilter = self.request.GET.get('q')
        if strfilter:
            self.queryset = self.queryset.filter(name__icontains=strfilter)

        return super().get_queryset()


class EditMixin(views.SuccessMessageMixin):
    model = Project
    success_url = urls.reverse_lazy('projects:list')
    form_class = UpdateForm
    specific_success_message = None

    def post(self, request, *args, **kwargs):
        customer_group_formset = CustomerGroupFormset(request.POST, instance=self.object)
        form = self.get_form()

        if form.is_valid() and customer_group_formset.is_valid():
            return self.forms_valid(form, customer_group_formset)
        else:
            return self.form_invalid(form)

    def get_context_data(self, **kwargs):
        if self.request.method in ('POST', 'PUT'):
            customer_group_formset = CustomerGroupFormset(self.request.POST, instance=self.object)
        else:
            customer_group_formset = CustomerGroupFormset(instance=self.object)
        return super().get_context_data(formset=customer_group_formset, **kwargs)

    def forms_valid(self, form, customer_group_formset):
        customer_group_formset.instance = form.save()
        customer_group_formset.save()
        if form.has_changed() or customer_group_formset.has_changed():
            self.success_message = self.specific_success_message
        else:
            self.success_message = ""
        return self.form_valid(form)


class Update(mixins.LoginRequiredMixin, EditMixin, generic.UpdateView):
    specific_success_message = _("Updated: %(name)s")

    def post(self, request, *args, **kwargs):
        # extract object being edited in form:
        self.object = self.get_object()
        return super().post(request, *args, **kwargs)


class Create(mixins.LoginRequiredMixin, EditMixin, generic.CreateView):
    specific_success_message = _("Created: %(name)s")

    def post(self, request, *args, **kwargs):
        # no current object when creating a new one:
        self.object = None
        return super().post(request, *args, **kwargs)
