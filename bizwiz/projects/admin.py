from django.contrib import admin

from bizwiz.projects.models import Project, CustomerGroup


class CustomerGroupsInline(admin.TabularInline):
    model = CustomerGroup


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date')
    search_fields = ('name',)
    inlines = [CustomerGroupsInline]


admin.site.register(Project, ProjectAdmin)
admin.site.register(CustomerGroup)
