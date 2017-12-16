from django.urls import path

from bizwiz.common import views

app_name = 'common'

urlpatterns = [
    path('', views.Welcome.as_view(), name='index'),
    path('changelog/', views.Changelog.as_view(), name='changelog'),
    path('session-filter/', views.SessionFilter.as_view(), name='session-filter'),
]
