"""Business operations on articles."""
from bizwiz.articles.models import Article
from bizwiz.common.session_filter import get_session_filter


def get_session_filtered_articles(session, include_inactive=False):
    """Returns queryset according to optional filter set in session."""
    filtered_project = get_session_filter(session).project
    return get_articles_for_project(filtered_project, include_inactive)


def get_articles_for_project(project, include_inactive=False):
    """Returns articles of given project or all if project is not given."""
    if project:
        queryset = project.articles
    else:
        queryset = Article.objects.all()

    if not include_inactive:
        queryset = queryset.filter(inactive=False)

    return queryset


def apply_session_filter(session, articles):
    """If active, articles are added to filtered project and True is returned."""
    session_filter = get_session_filter(session)
    if session_filter.project:
        for article in articles:
            article.project_set.add(session_filter.project)
        return True
    return False
