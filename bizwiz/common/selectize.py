"""Support for selectize.js Javascript library."""
from django import forms

from bizwiz.common import media


class SelectizeTextInput(forms.TextInput):
    Media = media.Media(
        css={'all': ('selectize/dist/css/selectize.bootstrap3.css',)},
        js=('selectize/dist/js/standalone/selectize.min.js',)
    )


class HiddenWidgetMixin:
    def widget_attrs(self, widget):
        """Hide this widget, since it will be replaced by selectize or similar in DOM."""
        attrs = super().widget_attrs(widget)
        attrs.update({'style': 'display:none'})
        return attrs


class ModelMultipleChoiceTextField(HiddenWidgetMixin, forms.ModelMultipleChoiceField):
    widget = SelectizeTextInput

    def prepare_value(self, value):
        """Turn list of PKs into comma separated string for rendering."""
        prepared = super().prepare_value(value)
        if isinstance(prepared, list):
            return ','.join(str(e) for e in prepared)
        return prepared

    def to_python(self, value):
        """Turn comma-separated string back into list of PKs."""
        pk_values = [int(v) for v in value.split(',') if v]
        return pk_values

    def validate(self, value):
        # "required" check done in base class:
        super().validate(value)
        if not isinstance(value, (list, tuple)):
            raise forms.ValidationError(self.error_messages['list'], code='list')

    def clean(self, value):
        """Clean form data.

        This is a reimplementation of the base class method, as that one violates the field cleaning
        ptotocol from https://www.djangoproject.com/doc/html/ref/forms/validation.html, where clean
        is supposed to call:
            1. to_python
            2. validate
            3. run_validators

        ModelMultipleChoice however calls prepare_value instead of to_python, which is supposed to
        be invoked during _rendering_ the field, not during validation. This new implementation
        reinstantiates the original protocol.
        """
        if not self.required and not value:
            return self.queryset.none()

        # jump over bad implementation of clean protocol from immediate base class:
        value = forms.Field.clean(self, value)

        qs = self._check_values(value)
        return qs


class ModelChoiceTextField(HiddenWidgetMixin, forms.ModelChoiceField):
    widget = SelectizeTextInput
