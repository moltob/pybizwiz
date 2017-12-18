from django.urls import path

from bizwiz.invoices import views

app_name = 'invoices'

urlpatterns = [
    path('', views.List.as_view(), name='list'),
    path('payable/', views.List.as_view(), {'subset': 'payable'}, name='list_payable'),
    path('taxable/', views.List.as_view(), {'subset': 'taxable'}, name='list_taxable'),
    path('create/', views.Create.as_view(), name='create'),
    path('edit/<int:pk>/', views.Update.as_view(), name='update'),
    path('print/invoice-<int:number>.pdf', views.Print.as_view(), name='print'),
    path('sales/', views.Sales.as_view(), name='sales'),
    path('sales/<int:year>/', views.List.as_view(), {'subset': 'year_paid'}, name='sales'),
    path('sales/<int:year>/articles/', views.ArticleSales.as_view(), name='sales_articles'),
]
