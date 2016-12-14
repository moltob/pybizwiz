from django.conf.urls import url

from bizwiz.common import views

urlpatterns = [
    url(r'^$', views.Welcome.as_view(), name='index'),
]
