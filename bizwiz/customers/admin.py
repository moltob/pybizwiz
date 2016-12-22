from django.contrib import admin

from bizwiz.customers.models import Customer


class CustomerAdmin(admin.ModelAdmin):
    pass


admin.site.register(Customer, CustomerAdmin)
