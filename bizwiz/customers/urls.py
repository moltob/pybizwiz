from django.urls import path

from bizwiz.customers import views

app_name = 'customers'

urlpatterns = [
    path('', views.List.as_view(), name='list'),
    path('create/', views.Create.as_view(), name='create'),
    path('edit/<int:pk>/', views.Update.as_view(), name='update'),
]
