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

from django.conf.urls import url, include
from django.contrib import admin

urlpatterns = [
    url(r'^', include('bizwiz.common.urls')),
    url(r'^accounts/', include('bizwiz.accounts.urls')),
    url(r'^articles/', include('bizwiz.articles.urls')),
    url(r'^customers/', include('bizwiz.customers.urls')),
    url(r'^invoices/', include('bizwiz.invoices.urls')),
    url(r'^projects/', include('bizwiz.projects.urls')),
    url(r'^rebates/', include('bizwiz.rebates.urls')),
    url(r'^admin/', admin.site.urls),
]