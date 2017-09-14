from django.conf.urls import url

from bizwiz.common import views

app_name = 'common'

urlpatterns = [
    url(r'^$', views.Welcome.as_view(), name='index'),
    url(r'^changelog$', views.Changelog.as_view(), name='changelog'),
    url(r'^session-filter/$', views.SessionFilter.as_view(), name='session-filter'),
]
