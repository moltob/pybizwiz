"""Business level operations on customers."""
from bizwiz.common.session_filter import get_session_filter
from bizwiz.customers.models import Customer


def get_session_filtered_customers(session):
    """Return customers optionally filtered by currently active session."""

    session_filter = get_session_filter(session)
    filtered_project = session_filter.project
    filtered_customer_group = session_filter.customer_group
    if filtered_customer_group:
        queryset = Customer.objects.filter(customergroup=filtered_customer_group)
    elif filtered_project:
        queryset = Customer.objects.filter(customergroup__project=filtered_project)
    else:
        queryset = Customer.objects.all()

    return queryset


def apply_session_filter(session, customer):
    """If session filter is set, add customer to curently active customer group."""

    session_filter = get_session_filter(session)
    customer_group = session_filter.customer_group
    if customer_group:
        customer_group.customers.add(customer)
        return True

    return False
