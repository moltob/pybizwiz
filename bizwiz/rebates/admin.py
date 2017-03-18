from django.contrib import admin

from bizwiz.rebates.models import Rebate


class RebateAdmin(admin.ModelAdmin):
    list_display = ('kind', 'name', 'value', 'auto_apply')
    search_fields = ('kind', 'name')


admin.site.register(Rebate, RebateAdmin)
