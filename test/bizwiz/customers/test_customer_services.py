from unittest import mock

from bizwiz.customers.services import apply_session_filter


@mock.patch('bizwiz.customers.services.get_session_filter')
def test_apply_session_filter_none(mock_get_session_filter):
    session_filter = mock.Mock()

    session_filter.project = None
    session_filter.customer_group = None
    session_filter.label = None

    mock_get_session_filter.return_value = session_filter

    assert not apply_session_filter(mock.sentinel.SESSION, mock.sentinel.CUSTOMER)


@mock.patch('bizwiz.customers.services.get_session_filter')
def test_apply_session_filter_project(mock_get_session_filter):
    session_filter = mock.Mock()

    session_filter.project = mock.sentinel.PROJECT
    session_filter.customer_group = None
    session_filter.label = mock.sentinel.LABEL

    mock_get_session_filter.return_value = session_filter

    assert not apply_session_filter(mock.sentinel.SESSION, mock.sentinel.CUSTOMER)


@mock.patch('bizwiz.customers.services.get_session_filter')
def test_apply_session_filter_customer_group(mock_get_session_filter):
    session_filter = mock.Mock()

    session_filter.project = mock.sentinel.PROJECT
    session_filter.customer_group = mock.MagicMock()
    session_filter.label = mock.sentinel.LABEL

    mock_get_session_filter.return_value = session_filter

    assert apply_session_filter(mock.sentinel.SESSION, mock.sentinel.CUSTOMER)
    session_filter.customer_group.customers.add.assert_called_once_with(mock.sentinel.CUSTOMER)
