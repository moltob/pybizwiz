"""
WSGI config for bwsite project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.10/howto/deployment/wsgi/
"""
import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bwsite.settings")
application = get_wsgi_application()

# import _after_ django is initialized
import logging
from bizwiz.version import BIZWIZ_VERSION

_logger = logging.getLogger(__name__)
_logger.info('************************************************************************************')
_logger.info('* Starting Bizwiz, version %s' % BIZWIZ_VERSION)
_logger.info('************************************************************************************')
