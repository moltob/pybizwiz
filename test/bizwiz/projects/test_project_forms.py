import pytest

from bizwiz.articles.models import Article
from bizwiz.customers.models import Customer
from bizwiz.projects.forms import CustomerGroupFormset
from bizwiz.projects.models import Project


@pytest.fixture
def project():
    p = Project(name='MyProject')
    p.save()
    return p


@pytest.fixture
def customer1():
    c = Customer(first_name='F', last_name='L')
    c.save()
    return c


def management_form_data(*, min_num=1, max_num=1000, initial=0, total=1):
    return {
        'customergroup_set-MIN_NUM_FORMS': '%d' % min_num,
        'customergroup_set-MAX_NUM_FORMS': '%d' % max_num,
        'customergroup_set-INITIAL_FORMS': '%d' % initial,
        'customergroup_set-TOTAL_FORMS': '%d' % total,
    }


def customer_group_data(pos, name, project_, customer):
    return {
        'customergroup_set-%d-name' % pos: name,
        'customergroup_set-%d-project' % pos: str(project_.pk),
        'customergroup_set-%d-customers' % pos: [str(customer.pk)],
    }


@pytest.mark.django_db
def test_customer_group_formset_valid(project, customer1):
    data = management_form_data(total=2)
    data.update(customer_group_data(0, 'Blaue Gruppe', project, customer1))
    data.update(customer_group_data(1, 'Rote Gruppe', project, customer1))
    fs = CustomerGroupFormset(data, instance=project)
    assert fs.is_valid(), fs.errors


@pytest.mark.django_db
def test_customer_group_formset_empty(project):
    data = management_form_data(total=0)
    fs = CustomerGroupFormset(data, instance=project)
    assert not fs.is_valid()
    assert fs.non_form_errors()


@pytest.mark.django_db
def test_customer_group_formset_name_duplicate(project, customer1):
    data = management_form_data(total=3)
    data.update(customer_group_data(0, 'Blaue Gruppe', project, customer1))
    data.update(customer_group_data(1, 'Rote Gruppe', project, customer1))
    data.update(customer_group_data(2, 'Rote Gruppe', project, customer1))
    fs = CustomerGroupFormset(data, instance=project)
    assert not fs.is_valid()
    assert fs.non_form_errors()


