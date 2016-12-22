from django.contrib import admin

from bizwiz.customers.models import Customer


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('last_name', 'first_name', 'salutation', 'company_name', 'email',
                    'street_address', 'zip_code', 'city')
    search_fields = ('last_name', 'first_name', 'company_name', 'email')


admin.site.register(Customer, CustomerAdmin)
