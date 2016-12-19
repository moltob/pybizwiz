from django.conf.urls import url

from bizwiz.articles import views

urlpatterns = [
    url(r'^$', views.List.as_view(), {'show_inactive': False}, name='list'),
    url(r'^all/$', views.List.as_view(), {'show_inactive': True}, name='list_with_inactive'),
]
