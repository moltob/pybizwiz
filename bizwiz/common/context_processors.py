from bizwiz.common.session_filter import get_session_filter
from bizwiz.projects.models import Project


def projects(request):
    """Returns project used by navigation menu for a logged in user."""
    # authentication ensured in template:
    return {
        'projects': Project.objects.order_by('-start_date'),
    }


def session_filter(request):
    return {
        'session_filter_label': get_session_filter(request.session).label
    }
