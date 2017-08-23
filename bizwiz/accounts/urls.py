from django.conf.urls import url, include
from django.contrib.auth import views as auth_views
from django.urls import reverse_lazy

from bizwiz.accounts.forms import login_helper

app_name = 'accounts'

urlpatterns = [
    url(r'^login/$', auth_views.LoginView.as_view(
        template_name='accounts/login.html',
        extra_context={'helper': login_helper},
    ), name='login'),
    url(r'^logout/$', auth_views.LogoutView.as_view(), name='logout'),
]
