from unittest import mock

import pytest

from bizwiz.version import get_version, BIZWIZ_DEVELOPMENT_VERSION


def test__version__development():
    mock_open = mock.MagicMock(side_effect=FileNotFoundError)
    with mock.patch('bizwiz.version.open', mock_open):
        assert get_version() == BIZWIZ_DEVELOPMENT_VERSION


@pytest.mark.parametrize(('tag',), [
    ('v4.2.1.43', ),
    ('v4.2.1.43\n', ),
    ('v4.2.1.43\n\n', ),
])
def test__version__production(tag):
    with mock.patch('bizwiz.version.open', mock.mock_open(read_data=tag)):
        assert get_version() == 'v4.2.1.43'
