from django.urls import path

from bizwiz.rebates import views

app_name = 'rebates'

urlpatterns = [
    path('', views.Update.as_view(), {'subset': None}, name='update'),
]
