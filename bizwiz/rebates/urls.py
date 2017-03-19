from django.conf.urls import url

from bizwiz.rebates import views

urlpatterns = [
    url(r'^$', views.Update.as_view(), {'subset': None}, name='update'),
]
