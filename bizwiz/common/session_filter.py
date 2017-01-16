"""All query data can be filtered by session wide project or customer group filters."""
import collections

import logging
from django.contrib.sessions.backends import base

from bizwiz.projects.models import CustomerGroup, Project

SESSION_FILTER_KEY = 'session-filter'
PROJECT_KEY = 'project'
CUSTOMER_GROUP_KEY = 'customer-group'

SessionFilterData = collections.namedtuple('SessionFilterData', 'project customer_group label')

_logger = logging.getLogger(__name__)


def get_session_filter(session) -> SessionFilterData:
    """Returns session filtered project, customergroup and label."""
    f = session.get(SESSION_FILTER_KEY)

    project = None
    customer_group = None
    label = ''

    if f:
        customer_group_pk = f.get(CUSTOMER_GROUP_KEY, 0)
        project_pk = f.get(PROJECT_KEY, 0)
        if customer_group_pk:
            customer_group = CustomerGroup.objects.get(pk=customer_group_pk)
            project = customer_group.project
            label = '{}, {}'.format(project.name, customer_group.name)
        elif project_pk:
            project = Project.objects.get(pk=project_pk)
            label = project.name

    return SessionFilterData(project, customer_group, label)


def set_session_filter(session, project_pk: int, customer_group_pk: int):
    if customer_group_pk:
        _logger.info('Setting session filter to customer group %s.' % customer_group_pk)
        session[SESSION_FILTER_KEY] = {CUSTOMER_GROUP_KEY: int(customer_group_pk)}
    elif project_pk:
        _logger.info('Setting session filter to project %s.' % project_pk)
        session[SESSION_FILTER_KEY] = {PROJECT_KEY: int(project_pk)}
    else:
        _logger.info('Clearing session filter.')
        del session[SESSION_FILTER_KEY]
