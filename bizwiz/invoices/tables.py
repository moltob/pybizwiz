"""Common helpers for tables of invoice data."""
import django_tables2 as tables
from djmoney import money

COLUMN_RIGHT_ALIGNED = {
    'th': {'class': 'text-right'},
    'td': {'class': 'text-right'}
}


class SummingMixin:
    """Mixin adding a sum total footer to column."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def render_footer(self, bound_column, table):
        return sum(bound_column.accessor.resolve(row) for row in table.data)


class SummingMoneyColumn(SummingMixin, tables.Column):
    """A money-valued column with a summed up footer."""

    def render_footer(self, bound_column, table):
        money_values = (money.Money(row[bound_column.name], row[f'{bound_column.name}_currency'])
                        for row in table.data)
        return sum(money_values)


class SummingLinkColumn(SummingMixin, tables.LinkColumn):
    """A linked column with a summed up footer."""
