from django.db import models
from django.utils.translation import ugettext_lazy as _


class Salutation:
    MR = 'MR'
    MRS = 'MRS'
    FAMILY = 'FAMILY'


class Customer(models.Model):
    last_name = models.CharField(
        _("Last name"),
        max_length=50
    )
    first_name = models.CharField(
        _("First name"),
        max_length=50
    )
    salutation = models.CharField(
        _("Salutation"),
        max_length=20,
        choices=(
            (Salutation.MR, _("Mr.")),
            (Salutation.MRS, _("Mrs.")),
            (Salutation.FAMILY, _("Family")),
        )
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

    def full_name(self):
        return '{}, {}'.format(self.last_name, self.first_name)

    def __str__(self):
        data = [self.full_name()]
        if self.company_name:
            data.append('({})'.format(self.company_name))
        if self.street_address or self.city:
            data.append('@ {}, {} {}'.format(self.street_address, self.zip_code, self.city))
        return ' '.join(data)
