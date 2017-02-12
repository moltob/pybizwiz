"""Business operations on articles."""
from bizwiz.articles.models import Article
from bizwiz.common.session_filter import get_session_filter


def get_session_filtered_articles(session):
    """Returns queryset according to optional filter set in session."""
    filtered_project = get_session_filter(session).project
    if filtered_project:
        queryset = filtered_project.articles
    else:
        queryset = Article.objects.all()

    return queryset


def apply_session_filter(session, articles):
    """If active, articles are added to filtered project and True is returned."""
    session_filter = get_session_filter(session)
    if session_filter.project:
        for article in articles:
            article.project_set.add(session_filter.project)
        return True
    return False
