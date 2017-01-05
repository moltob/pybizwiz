import pytest
from django import forms

from bizwiz.customers.forms import UpdateForm
from bizwiz.customers.models import Salutation, Customer


@pytest.fixture
def completed_form():
    return UpdateForm({
        'salutation': Salutation.MR,
        'last_name': 'LAST_NAME',
        'first_name': 'FIRST_NAME'
    })


@pytest.fixture
def db_customers():
    c1 = Customer(first_name='FIRST_NAME', last_name='LAST_NAME', salutation=Salutation.MR)
    c1.save()
    c2 = Customer(first_name='FIRST_NAME', last_name='LAST_NAME', salutation=Salutation.MR)
    c2.save()
    c3 = Customer(first_name='FIRST_NAME2', last_name='LAST_NAME2', salutation=Salutation.MR)
    c3.save()
    c4 = Customer(first_name='FIRST_NAME3', last_name='LAST_NAME3', salutation=Salutation.MR)
    c4.save()
    return c1, c2, c3, c4


@pytest.mark.django_db
def test_update_form_valid(completed_form):
    f = UpdateForm()
    assert not f.is_valid()

    f = UpdateForm({
        'last_name': 'LAST_NAME',
        'first_name': 'FIRST_NAME'
    })
    assert not f.is_valid()

    assert completed_form.is_valid()


@pytest.mark.django_db
def test_update_form_new_customer_saved(completed_form):
    assert not completed_form.instance.pk
    completed_form.save()
    assert completed_form.instance.pk

    customer = Customer.objects.get(pk=completed_form.instance.pk)
    assert customer.first_name == 'FIRST_NAME'
    assert customer.last_name == 'LAST_NAME'
    assert customer.salutation == Salutation.MR


@pytest.mark.django_db
def test_update_form_validation_duplicate_found(db_customers, completed_form):
    # completed form with identical name is not accepted and duplicate is identified
    assert not completed_form.is_valid()
    assert not completed_form.instance.pk
    assert completed_form.errors
    assert completed_form.duplicates
    assert len(completed_form.duplicates) == 2
    assert set(completed_form.duplicates) == {db_customers[0], db_customers[1]}

    # marking duplicate as accepted allows saving form:
    completed_form.data['duplicate_accepted'] = True
    completed_form.full_clean()
    assert completed_form.is_valid()
    completed_form.save()

    assert Customer.objects.count() == 5


@pytest.mark.django_db
def test_update_form_validation_duplicate_unchanged(db_customers):
    # change second duplicate customer in DB to be no longer a duplicate:
    c = db_customers[1]
    f = UpdateForm(data=forms.model_to_dict(c), instance=c)
    assert f.is_valid()
    assert not f.has_changed()


@pytest.mark.django_db
def test_update_form_validation_duplicate_other_field_changed(db_customers):
    # change second duplicate customer in DB to be no longer a duplicate:
    c = db_customers[1]
    f = UpdateForm(data=forms.model_to_dict(c), instance=c)
    f.data['zip_code'] = '12345'
    assert f.is_valid()
    assert f.has_changed()
    assert f.instance.zip_code == '12345'

    f.save()
    assert Customer.objects.count() == 4


@pytest.mark.django_db
def test_update_form_validation_duplicate_fixed(db_customers):
    # change second duplicate customer in DB to be no longer a duplicate:
    c = db_customers[1]
    assert c.first_name == 'FIRST_NAME'

    f = UpdateForm(data=forms.model_to_dict(c), instance=c)
    f.data['first_name'] = 'CHANGED'
    assert f.is_valid()
    assert f.has_changed()
    assert c.first_name == 'CHANGED'

    f.save()
    assert Customer.objects.count() == 4
