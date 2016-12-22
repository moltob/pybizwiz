from django.contrib.auth import mixins
from django.shortcuts import render
from django.views import generic

from bizwiz.common.views import OrderedListViewMixin
from bizwiz.customers.models import Customer


class List(mixins.LoginRequiredMixin, OrderedListViewMixin, generic.ListView):
    model = Customer
    ordering = 'last_name'
    paginate_by = 15
