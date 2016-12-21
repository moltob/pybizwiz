from crispy_forms import bootstrap


def remove_form_button_factory():
    return bootstrap.StrictButton(
        '<span class="glyphicon glyphicon-minus"></span>',
        css_class='btn-default',
        data_formset_delete_button=''
    )
