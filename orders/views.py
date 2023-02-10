from django.core.exceptions import PermissionDenied
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import generic
from django.shortcuts import get_object_or_404
from django.http import HttpResponseRedirect
# from django.contrib.auth.mixins import LoginRequiredMixin
from .models import OrderItem, Order
from .forms import OrderUserCreateForm, OrderPaymentCreateForm, OrderDeliveryCreateForm, OrderCardForm
from cart.service import Cart
from . import tasks

class HistoryOrderView(generic.ListView):
    model = Order
    template_name = 'orders/history_order.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['orders'] = Order.objects.all()
        return context


class HistoryOrderDetailView(generic.DetailView):
    model = Order
    template_name = 'orders/history_order_detail.html'
    context_object_name = 'order'


def order_create(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderUserCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            for item in cart:
                OrderItem.objects.create(order=order,
                                         offer=item['product'],
                                         price=item['price'],
                                         quantity=item['quantity'],
                                         )
            # очистка корзины
            cart.clear()
            return redirect('order_create_delivery', pk=order.pk)
    else:
        form = OrderUserCreateForm
    return render(request, 'orders/new-order.html',
                  {'cart': cart, 'form': form})


def order_create_delivery(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        form = OrderDeliveryCreateForm(request.POST)
        if form.is_valid():
            order.delivery = form.cleaned_data['delivery']
            order.city = form.cleaned_data['city']
            order.address = form.cleaned_data['address']
            order.save()
            return redirect('order_create_payment', pk=order.pk)
    else:
        form = OrderDeliveryCreateForm
    return render(request, 'orders/order-delivery.html',
                  {'pk': order.pk, 'form': form})


def order_create_payment(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == 'POST':
        form = OrderCardForm(request.POST)
        if form.is_valid():
            order.card_number = form.cleaned_data['card_number']
            order.save()
            tasks.payment.delay(pk)
            return redirect('wait-payment', pk=pk)
    else:
        form = OrderCardForm()
    return render(request, 'orders/order-delivery.html',
                  {'order': order, 'form': form})


def wait_payment(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, 'orders/created.html', {'order':order})



