"""Configuration of pytest-django."""
import os

import django
from django.conf import settings

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bwsite.settings")


def pytest_configure():
    settings.DEBUG = False
    #settings.PASSWORD_HASHERS = (
    #    'django.contrib.auth.hashers.MD5PasswordHasher',
    #)
    django.setup()
