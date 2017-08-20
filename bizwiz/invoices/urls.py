from django.conf.urls import url

from bizwiz.invoices import views

app_name = 'invoices'

urlpatterns = [
    url(r'^$', views.List.as_view(), {'subset': None}, name='list'),
    url(r'^payable/$', views.List.as_view(), {'subset': 'payable'}, name='list_payable'),
    url(r'^taxable/$', views.List.as_view(), {'subset': 'taxable'}, name='list_taxable'),
    url(r'^create/$', views.Create.as_view(), name='create'),
    url(r'^edit/(?P<pk>[0-9]+)/$', views.Update.as_view(), name='update'),
    url(r'^print/invoice-(?P<number>[0-9]+).pdf$', views.Print.as_view(), name='print'),
]
