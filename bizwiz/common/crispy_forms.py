"""Extensions and customizations of cripsy forms."""
from crispy_forms import layout


class PickableDateField(layout.Field):
    """Datefield with picker."""
    template = 'common/datetime_picker_field.html'

    class Media:
        """Media required for this field, include in using form."""
        css = {
            'all': (
                'eonasdan-bootstrap-datetimepicker/build/css/bootstrap-datetimepicker.min.css',
            )
        }

        js = (
            'moment/min/moment.min.js',
            'eonasdan-bootstrap-datetimepicker/build/js/bootstrap-datetimepicker.min.js'
        )


class ChosenMultiSelectField(layout.Field):
    """Mutli-select with chosen.js automation."""

    def __init__(self, *args, **kwargs):
        my_kwargs = kwargs.copy()
        my_kwargs['css_class'] = 'chosen ' + kwargs.get('css_class', '')
        super().__init__(*args, **my_kwargs)

    class Media:
        """Media required for this field, include in using form."""
        css = {
            'all': (
                'chosen/chosen.css',
                'common/chosen-bootstrap.css',
            )
        }

        js = (
            'chosen/chosen.jquery.js',
        )
