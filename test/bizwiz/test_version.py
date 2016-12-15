from bizwiz.version import Version


def test_version_string():
    v = Version(1, 2, 3)
    assert str(v) == '1.2.3'
