from django.contrib import admin

from bizwiz.invoices.models import Invoice, InvoicedArticle, InvoicedCustomer


class InvoicedArticlesInline(admin.TabularInline):
    model = InvoicedArticle


class InvoicedCustomerInline(admin.StackedInline):
    model = InvoicedCustomer


class InvoiceAdmin(admin.ModelAdmin):
    inlines = [InvoicedCustomerInline, InvoicedArticlesInline]
    list_display = ('number', 'date_created', 'project', 'invoiced_customer')
    search_fields = ('number', 'invoiced_customer')


admin.site.register(Invoice, InvoiceAdmin)
