"""Extensions and customizations of cripsy forms."""
import decimal

from crispy_forms import layout
from django import forms

from bizwiz.common import media


class PickableDateField(layout.Field):
    """Datefield with picker."""
    template = 'common/datetime_picker_field.html'

    """Media required for this field, include in using form."""
    Media = media.Media(
        css={
            'all': (
                'eonasdan-bootstrap-datetimepicker/build/css/bootstrap-datetimepicker.min.css',
            )
        },
        js=(
            'moment/min/moment.min.js',
            'eonasdan-bootstrap-datetimepicker/build/js/bootstrap-datetimepicker.min.js'
        )
    )


class MoneyAmountField(forms.DecimalField):
    """Render and process only the amount part of the associated money model.

    Use this widget if only the amount of an instance of `djmoney.money.Money` should be edited.
    """

    def prepare_value(self, value):
        try:
            return value.amount.quantize(decimal.Decimal(10) ** -self.decimal_places)
        except AttributeError:
            # this was not a money value, probably resulting from an invalid value, returned to
            # form to get corrected by user, so just take it as is:
            return super().prepare_value(value)
