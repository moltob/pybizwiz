from unittest import mock

from bizwiz.articles.views import apply_session_filter


@mock.patch('bizwiz.articles.views.get_session_filter')
def test_apply_session_filter_none(mock_get_session_filter):
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


@mock.patch('bizwiz.articles.views.get_session_filter')
def test_apply_session_filter_project(mock_get_session_filter):
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
