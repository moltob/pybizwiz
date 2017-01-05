import django_tables2 as tables
from django.contrib.auth import mixins
from django.utils.translation import ugettext as _

from bizwiz.common.views import SizedColumnsMixin
from bizwiz.projects.models import Project


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
