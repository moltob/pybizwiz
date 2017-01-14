from bizwiz.projects.models import Project


def projects(request):
    """Returns project used by navigation menu for a logged in user."""
    # authentication ensured in template:
    return {
        'projects': Project.objects.order_by('-start_date'),
    }
