from django.conf.urls import url

from bizwiz.articles import views

urlpatterns = [
    url(r'^active/$', views.List.as_view(), {'show_inactive': False}, name='list_active'),
    url(r'^$', views.List.as_view(), {'show_inactive': True}, name='list'),
    url(r'^edit/(?P<pk>[0-9]+)/$', views.Update.as_view(), name='update'),
]
