import logging

import django_tables2 as tables

from bizwiz.rebates.models import Rebate

_logger = logging.getLogger(__name__)


class InvoiceTable(tables.Table):
    #name = tables.LinkColumn('invoices:update_rebate', args=[tables.utils.A('pk')])
    selected = tables.CheckBoxColumn(accessor='pk', attrs={
        'th__input': {'id': 'id-select-all'},
    })

    class Meta:
        template = 'common/table.html'
        attrs = {'class': 'table table-striped'}
        per_page = 50
        model = Rebate
        fields = ('kind', 'name', 'value', 'auto_apply')
        order_by = ('-number',)
