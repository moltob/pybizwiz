from django.conf.urls import url

from bizwiz.customers import views

app_name = 'customers'

urlpatterns = [
    url(r'^$', views.List.as_view(), name='list'),
    url(r'^create/$', views.Create.as_view(), name='create'),
    url(r'^edit/(?P<pk>[0-9]+)/$', views.Update.as_view(), name='update'),
]
