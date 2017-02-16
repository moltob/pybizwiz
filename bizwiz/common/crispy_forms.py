"""Extensions and customizations of cripsy forms."""
from crispy_forms import layout

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