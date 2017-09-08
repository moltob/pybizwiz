from django.conf.urls import url

from bizwiz.invoices import views

app_name = 'invoices'

urlpatterns = [
    url(r'^$', views.List.as_view(), name='list'),
    url(r'^payable/$', views.List.as_view(), {'subset': 'payable'}, name='list_payable'),
    url(r'^taxable/$', views.List.as_view(), {'subset': 'taxable'}, name='list_taxable'),
    url(r'^create/$', views.Create.as_view(), name='create'),
    url(r'^edit/(?P<pk>[0-9]+)/$', views.Update.as_view(), name='update'),
    url(r'^print/invoice-(?P<number>[0-9]+).pdf$', views.Print.as_view(), name='print'),
    url(r'^sales/$', views.Sales.as_view(), name='sales'),
    url(r'^sales/(?P<year>\d{4})/$', views.List.as_view(), {'subset': 'year_paid'}, name='sales'),
    url(r'^sales/(?P<year>\d{4})/articles/$', views.ArticleSales.as_view(), name='sales_articles'),
]
