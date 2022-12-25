from django.shortcuts import render
from django.views.generic import CreateView, DetailView
from .models import Seller


class SellerInfo(DetailView):
    model = Seller
    template_name = 'shop/seller.html'
    context_object_name = 'seller'
