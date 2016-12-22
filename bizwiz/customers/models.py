from django.db import models


class Customer(models.Model):
    last_name = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    title = models.CharField(max_length=20, blank=True)
    company_name = models.CharField(max_length=50, blank=True)
    street_address = models.CharField(max_length=50, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=50, blank=True)
    phone_number = models.CharField(max_length=50, blank=True)
    mobile_number = models.CharField(max_length=50, blank=True)
    email = models.EmailField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
