from django.shortcuts import render, redirect
from django.views import generic
from django.shortcuts import get_object_or_404
# from django.contrib.auth.mixins import LoginRequiredMixin
from .models import OrderItem, Order
from .forms import OrderUserCreateForm, OrderPaymentCreateForm, OrderDeliveryCreateForm
from cart.service import Cart


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
        form = OrderPaymentCreateForm(request.POST)
        if form.is_valid():
            order.payment = form.cleaned_data['payment']
            order.save()
            return render(request, 'orders/created.html')
    else:
        form = OrderPaymentCreateForm
    return render(request, 'orders/order-delivery.html',
                  {'order': order, 'form': form})
