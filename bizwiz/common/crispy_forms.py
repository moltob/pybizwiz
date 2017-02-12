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


class ChosenMultiSelectField(layout.Field):
    """Mutli-select with chosen.js automation."""

    def __init__(self, *args, **kwargs):
        # apply chosen class to let plugin find this element:
        my_kwargs = kwargs.copy()
        my_kwargs['css_class'] = 'chosen ' + kwargs.get('css_class', '')

        # hide original multi-select to prevent flicker:
        assert 'style' not in my_kwargs, 'Mixing style attribute not yet implemented.'
        my_kwargs['style'] = 'visibility:hidden;'

        super().__init__(*args, **my_kwargs)

    Media = media.Media(
        css={
            'all': (
                'chosen/chosen.css',
                'common/chosen-bootstrap.css',
            )
        },
        js=(
            'chosen/chosen.jquery.js',
        )
    )
