"""Bizwiz application exceptions."""
from django.core.exceptions import ImproperlyConfigured


class BizwizError(Exception):
    """Base class for all errors raised by Bizwiz."""


class IncorrectViewConfigurationError(BizwizError, ImproperlyConfigured):
    """The view is not fully or correctly set up."""
