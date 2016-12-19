"""Bizwiz application exceptions."""


class BizwizError(Exception):
    """Base class for all errors raised by Bizwiz."""


class IncorrectViewConfigurationError(BizwizError, ValueError):
    """The view is not fully or correctly set up."""
