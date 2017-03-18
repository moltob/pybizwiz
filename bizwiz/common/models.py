from django.db import models


def copy_field_data(model, src, dst):
    """Copies all non-automatic fields.

    Helper useful when copying common base class data.

    :model: Model class for which fields are copied, a common ancestor of src and dst.
    :src: Instance from which field data is copied.
    :dst: Instance to which field data is copied.
    """
    for field in model._meta.get_fields():
        if not (isinstance(field, models.AutoField) or isinstance(field, models.BigAutoField)):
            name = field.name
            value = getattr(src, name)
            setattr(dst, name, value)