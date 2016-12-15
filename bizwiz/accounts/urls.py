from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

from bizwiz.accounts.forms import login_helper

urlpatterns = [
    url(r'^login/$', auth_views.login, {
        'template_name': 'accounts/login.html',
        'extra_context': {'helper': login_helper},
    }, name='login'),
    url(r'^logout/$', auth_views.logout, name='logout'),
]
