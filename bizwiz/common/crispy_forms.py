"""Extensions and customizations of cripsy forms."""
from crispy_forms import layout


class PickableDateField(layout.Field):
    """Datefield with picker."""
    template = 'common/datetime_picker_field.html'
