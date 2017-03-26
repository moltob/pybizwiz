import os

BIZWIZ_BUILD_TAG_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'build-info'))
BIZWIZ_DEVELOPMENT_VERSION = 'DEV'


def get_version():
    try:
        with open(BIZWIZ_BUILD_TAG_FILE, 'rt') as build_tag_file:
            version = build_tag_file.read().strip()
    except FileNotFoundError:
        version = BIZWIZ_DEVELOPMENT_VERSION
    return version


BIZWIZ_VERSION = get_version()

if __name__ == '__main__':
    print(BIZWIZ_VERSION)
