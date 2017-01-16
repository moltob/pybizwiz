import pytest

from bizwiz.common.session_filter import set_session_filter, SESSION_FILTER_KEY, PROJECT_KEY, \
    CUSTOMER_GROUP_KEY, get_session_filter
from bizwiz.projects.models import CustomerGroup, Project


@pytest.fixture
def project():
    p = Project(name='MyProject')
    p.save()
    c = CustomerGroup(name='TheGroup', project=p)
    c.save()
    return p


@pytest.mark.django_db
def test_project(project):
    session = {}
    set_session_filter(session, project.pk, 0)
    assert session[SESSION_FILTER_KEY][PROJECT_KEY] == project.pk
    assert CUSTOMER_GROUP_KEY not in session[SESSION_FILTER_KEY]

    data = get_session_filter(session)
    assert data.project == project
    assert data.customer_group is None
    assert project.name in data.label


@pytest.mark.django_db
def test_customer_group(project):
    session = {}
    customer_group = project.customergroup_set.first()
    set_session_filter(session, 0, customer_group.pk)
    assert session[SESSION_FILTER_KEY][CUSTOMER_GROUP_KEY] == customer_group.pk
    assert PROJECT_KEY not in session[SESSION_FILTER_KEY]

    data = get_session_filter(session)
    assert data.project == project
    assert data.customer_group == customer_group
    assert project.name in data.label
    assert customer_group.name in data.label


def test_empty():
    session = {}
    data = get_session_filter(session)
    assert not data.project
    assert not data.customer_group
    assert not data.label

@pytest.mark.django_db
def test_deleted_customer_group(project):
    session = {}
    customer_group = project.customergroup_set.first()
    set_session_filter(session, 0, customer_group.pk + 1)

    data = get_session_filter(session)
    assert not data.project
    assert not data.customer_group
    assert not data.label

@pytest.mark.django_db
def test_deleted_project(project):
    session = {}
    set_session_filter(session, project.pk + 1, 0)

    data = get_session_filter(session)
    assert not data.project
    assert not data.customer_group
    assert not data.label
