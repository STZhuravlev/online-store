# from django.shortcuts import render
from django.views import generic
# from .models import OrderItem
# from .forms import OrderCreateForm
# from cart.service import Cart
from orders.models import Order


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
    pass
    # cart = Cart(request)
    # if request.method == 'POST':
    #     form = OrderCreateForm(request.POST)
    #     if form.is_valid():
    #         order = form.save()
    #         for item in cart:
    #             OrderItem.objects.create(order=order,
    #                                      offer=item['product'],
    #                                      price=item['price'],
    #                                      quantity=item['quantity'],
    #                                      )
    #         # очистка корзины
    #         cart.clear()
    #         return render(request, 'orders/created.html',
    #                       {'order': order})
    # else:
    #     form = OrderCreateForm
    # return render(request, 'orders/new-order.html',
    #               {'cart': cart, 'form': form})
