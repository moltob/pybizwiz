from django.urls import path

from bizwiz.articles import views

app_name = 'articles'

urlpatterns = [
    path('', views.List.as_view(), {'show_inactive': True}, name='list'),
    path('active/', views.List.as_view(), {'show_inactive': False}, name='list_active'),
    path('create/', views.Create.as_view(), name='create'),
    path('edit/<int:pk>/', views.Update.as_view(), name='update'),
]
