"""bwsite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
import logging

from django.conf.urls import url, include
from django.contrib import admin

from bizwiz.version import BIZWIZ_VERSION

urlpatterns = [
    url(r'^', include('bizwiz.common.urls', namespace='common')),
    url(r'^accounts/', include('bizwiz.accounts.urls', namespace='accounts')),
    url(r'^articles/', include('bizwiz.articles.urls', namespace='articles')),
    url(r'^customers/', include('bizwiz.customers.urls', namespace='customers')),
    url(r'^invoices/', include('bizwiz.invoices.urls', namespace='invoices')),
    url(r'^projects/', include('bizwiz.projects.urls', namespace='projects')),
    url(r'^admin/', admin.site.urls),
]

_logger = logging.getLogger(__name__)
_logger.info('************************************************************************************')
_logger.info('* Starting Bizwiz, version %s' % BIZWIZ_VERSION)
_logger.info('************************************************************************************')
