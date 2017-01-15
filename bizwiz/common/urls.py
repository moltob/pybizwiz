from django.conf.urls import url

from bizwiz.common import views

urlpatterns = [
    url(r'^$', views.Welcome.as_view(), name='index'),
    url(r'^session-filter/$', views.SessionFilter.as_view(), name='session-filter'),
]
