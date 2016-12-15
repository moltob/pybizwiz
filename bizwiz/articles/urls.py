from django.conf.urls import url

from bizwiz.articles import views

urlpatterns = [
    url(r'^$', views.List.as_view(), name='list'),
]
