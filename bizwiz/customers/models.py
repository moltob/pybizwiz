from django.db import models
from django.utils.translation import ugettext_lazy as _


class Customer(models.Model):
    last_name = models.CharField(
        _("Last name"),
        max_length=50
    )
    first_name = models.CharField(
        _("First name"),
        max_length=50
    )
    title = models.CharField(
        _("Title"),
        max_length=20,
        blank=True
    )
    company_name = models.CharField(
        _("Company name"),
        max_length=50,
        blank=True
    )
    street_address = models.CharField(
        _("Street address"),
        max_length=50,
        blank=True
    )
    zip_code = models.CharField(
        _("Zip code"),
        max_length=20,
        blank=True
    )
    city = models.CharField(
        _("City"),
        max_length=50,
        blank=True
    )
    phone_number = models.CharField(
        _("Phone number"),
        max_length=50,
        blank=True
    )
    mobile_number = models.CharField(
        _("Mobile number"),
        max_length=50,
        blank=True
    )
    email = models.EmailField(
        _("Email address"),
        max_length=50,
        blank=True
    )
    notes = models.TextField(
        _("Notes"),
        blank=True
    )

    class Meta:
        verbose_name = _("Customer")
        verbose_name_plural = _("Customers")
