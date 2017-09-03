"""Common helpers for tables of invoice data."""
import django_tables2 as tables

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


class SummingColumn(SummingMixin, tables.Column):
    """A column with a summed up footer."""


class SummingLinkColumn(SummingMixin, tables.LinkColumn):
    """A linked column with a summed up footer."""
