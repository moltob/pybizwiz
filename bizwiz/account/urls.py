from django.conf.urls import url, include
from django.contrib.auth import views as auth_views

from bizwiz.account.forms import login_helper

urlpatterns = [
    url(r'^login/$', auth_views.login, {
        'template_name': 'account/login.html',
        'extra_context': {'helper': login_helper},
    }, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout'),
]
