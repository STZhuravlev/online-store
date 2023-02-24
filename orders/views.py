from django.shortcuts import render, redirect
from django.views import generic
from django.shortcuts import get_object_or_404
from django.forms.utils import ErrorList
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate, login
# from django.contrib.auth.mixins import LoginRequiredMixin
from .models import OrderItem, Order
from users.models import CustomUser
from product.services import get_category
from .forms import OrderUserCreateForm, OrderPaymentCreateForm, OrderDeliveryCreateForm, OrderCardForm
from cart.service import Cart
from . import tasks
import redis
# from django.core.cache import cache
# from django.conf import settings
# from django.core.cache.backends.base import DEFAULT_TIMEOUT
#
# CACHE_TTL = getattr(settings, 'CACHE_TTL', DEFAULT_TIMEOUT)
# caching = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
caching = redis.Redis(host='docker.for.mac.localhost', port=6379, db=0, decode_responses=True)


class HistoryOrderView(generic.ListView):
    model = Order
    template_name = 'orders/history_order.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['orders'] = Order.objects.filter(email=self.request.user)
        context['categories'] = get_category()
        return context


class HistoryOrderDetailView(generic.DetailView):
    model = Order
    template_name = 'orders/history_order_detail.html'
    context_object_name = 'order'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = get_category()
        return context


def order_create(request):
    if request.method == 'POST':
        form = OrderUserCreateForm(request.POST)
        if form.is_valid():
            if request.user.is_authenticated:
                caching.set('first_name', form.cleaned_data.get('first_name'))
                caching.set('last_name', form.cleaned_data.get('last_name'))
                caching.set('email', request.user.email)
                caching.set('number', form.cleaned_data.get('number'))
            else:
                # Если пользователь не авторизован, но существует
                if CustomUser.objects.filter(email=form.cleaned_data['email']).exists():
                    form._errors["email"] = ErrorList([_(u"Пользователь уже существует")])
                    # Выводить форму входа
                    return render(request, 'orders/new-order.html',
                                  {'form': form, 'categories': get_category()})
                # Если пользователь не авторизован и не существует
                else:
                    if form.cleaned_data.get('password1') == form.cleaned_data.get('password2'):
                        if form.cleaned_data.get('password1') == '':
                            form._errors["email"] = ErrorList(
                                [_(u"Данный пользователь не зарегистрирован, Введите пароль")]
                            )
                            return render(request, 'orders/new-order.html',
                                          {'form': form, 'categories': get_category()})
                        if len(form.cleaned_data.get('password1')) < 8:
                            form._errors["password1"] = ErrorList(
                                [_(u"Пароль должен быть длиннее 8 символов")]
                            )
                            return render(request, 'orders/new-order.html',
                                          {'form': form, 'categories': get_category()})
                        user = get_user_model().objects.create_user(first_name=form.cleaned_data.get('first_name'),
                                                                    last_name=form.cleaned_data.get('last_name'),
                                                                    email=form.cleaned_data.get('email'),
                                                                    password=form.cleaned_data.get('password1'))
                        user.save()
                        user = authenticate(email=form.cleaned_data.get('email'),
                                            password=form.cleaned_data.get('password1'))
                        login(request, user)
                        caching.set('first_name', form.cleaned_data.get('first_name'))
                        caching.set('last_name', form.cleaned_data.get('last_name'))
                        caching.set('email', request.user.email)
                        caching.set('number', form.cleaned_data.get('number'))
                    else:
                        form._errors["password1"] = ErrorList([_(u"Пароли не совпадают")])
                        return render(request, 'orders/new-order.html',
                                      {'form': form, 'categories': get_category()})
                # order = form.save()
            return redirect('order_create_delivery')
    else:
        if request.user.is_authenticated:
            data = {'first_name': request.user.first_name,
                    'last_name': request.user.last_name,
                    'email': request.user.email,
                    }
            form = OrderUserCreateForm(data)
            form.fields['email'].widget.attrs['readonly'] = True
        else:
            form = OrderUserCreateForm
    return render(request, 'orders/new-order.html',
                  {'form': form, 'categories': get_category()})


def order_create_delivery(request):
    if request.method == 'POST':
        form = OrderDeliveryCreateForm(request.POST)
        if form.is_valid():
            caching.set('delivery', form.cleaned_data.get('delivery'))
            caching.set('city', form.cleaned_data.get('city'))
            caching.set('address', form.cleaned_data.get('address'))
            return redirect('order_type_payment')
    else:
        form = OrderDeliveryCreateForm
    return render(request, 'orders/order-delivery.html',
                  {'form': form, 'categories': get_category()})


def order_type_payment(request):
    if request.method == 'POST':
        form = OrderPaymentCreateForm(request.POST)
        if form.is_valid():
            caching.set('payment', form.cleaned_data.get('payment'))
            return redirect('order_create_payment')
    else:
        form = OrderPaymentCreateForm
    return render(request, 'orders/order-payment.html',
                  {'form': form, 'categories': get_category()})


def order_create_payment(request):
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderCardForm(request.POST)
        if form.is_valid():
            order = Order.objects.create(first_name=caching.get('first_name'),
                                         last_name=caching.get('last_name'),
                                         email=caching.get('email'),
                                         number=caching.get('number'),
                                         delivery=caching.get('delivery'),
                                         city=caching.get('city'),
                                         address=caching.get('address'),
                                         payment=caching.get('payment'),
                                         card_number=form.cleaned_data.get('card_number'))
            for item in cart.cart:
                OrderItem.objects.create(order=order,
                                         product=item,
                                         price=float(cart.cart[item]['price']),
                                         quantity=cart.cart[item]['quantity'],
                                         )
            cart.clear()
            caching.close()
            tasks.payment.delay(order.pk)
            return redirect('wait-payment', pk=order.pk)
    else:
        form = OrderCardForm()
    return render(request, 'orders/order.html',
                  {'form': form, 'categories': get_category()})


def wait_payment(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, 'orders/created.html', {'order': order})
