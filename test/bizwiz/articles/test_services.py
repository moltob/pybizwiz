from unittest import mock

import pytest

from bizwiz.articles.models import Article
from bizwiz.articles.services import apply_session_filter, get_session_filtered_articles


@mock.patch('bizwiz.articles.services.get_session_filter')
def test__apply_session_filter__none(mock_get_session_filter):
    session_filter = mock.Mock()

    session_filter.project = None
    session_filter.customer_group = None
    session_filter.label = None

    mock_get_session_filter.return_value = session_filter

    mock_article1 = mock.MagicMock()
    mock_article2 = mock.MagicMock()

    assert not apply_session_filter(mock.sentinel.SESSION, [mock_article1, mock_article2])
    assert not mock_article1.project_set.add.called
    assert not mock_article2.project_set.add.called


@mock.patch('bizwiz.articles.services.get_session_filter')
def test__apply_session_filter__project(mock_get_session_filter):
    session_filter = mock.Mock()

    session_filter.project = mock.sentinel.PROJECT
    session_filter.customer_group = None
    session_filter.label = mock.sentinel.LABEL

    mock_get_session_filter.return_value = session_filter

    mock_article1 = mock.MagicMock()
    mock_article2 = mock.MagicMock()

    assert apply_session_filter(mock.sentinel.SESSION, [mock_article1, mock_article2])
    mock_article1.project_set.add.assert_called_once_with(mock.sentinel.PROJECT)
    mock_article2.project_set.add.assert_called_once_with(mock.sentinel.PROJECT)


@pytest.fixture
def articles():
    new_articles = [
        Article(name='A', price=1, inactive=False),
        Article(name='B', price=2, inactive=True),
        Article(name='C', price=3, inactive=True),
    ]
    for a in new_articles:
        a.save()
    return new_articles


@pytest.mark.django_db
def test__get_session_filtered_articles__all(articles):
    returned_articles = get_session_filtered_articles(session={}, include_inactive=True)
    assert len(returned_articles) == 3

    for a in articles:
        assert a in returned_articles


@pytest.mark.django_db
def test__get_session_filtered_articles__active(articles):
    returned_articles = get_session_filtered_articles(session={})
    assert len(returned_articles) == 1

    assert not articles[0].inactive
    assert articles[0] in returned_articles
