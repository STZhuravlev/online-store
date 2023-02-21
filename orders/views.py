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
from .forms import OrderUserCreateForm, OrderPaymentCreateForm, OrderDeliveryCreateForm
from cart.service import Cart


class HistoryOrderView(generic.ListView):
    model = Order
    template_name = 'orders/history_order.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['orders'] = Order.objects.all()
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
    cart = Cart(request)
    if request.method == 'POST':
        form = OrderUserCreateForm(request.POST)
        if form.is_valid():
            if request.user.is_authenticated:
                form.fields['email'].widget.attrs['readonly'] = True
                form.fields['password1'].widget.attrs['disabled'] = True
                form.fields['password2'].widget.attrs['disabled'] = True
                order = Order.objects.create(first_name=form.cleaned_data.get('first_name'),
                                             last_name=form.cleaned_data.get('last_name'),
                                             email=request.user.email,
                                             number=form.cleaned_data.get('number'))
            else:
                # Если пользователь не авторизован, но существует
                if CustomUser.objects.filter(email=form.cleaned_data['email']).exists():
                    form._errors["email"] = ErrorList([_(u"Пользователь уже существует")])
                    # Выводить форму входа
                    return render(request, 'orders/new-order.html',
                                  {'cart': cart, 'form': form, 'categories': get_category()})
                # Если пользователь не авторизован и не существует
                else:
                    if form.cleaned_data.get('password1') == form.cleaned_data.get('password2'):
                        if form.cleaned_data.get('password1') == '':
                            form._errors["email"] = ErrorList(
                                [_(u"Данный пользователь не зарегистрирован, Введите пароль")]
                            )
                            return render(request, 'orders/new-order.html',
                                          {'cart': cart, 'form': form, 'categories': get_category()})
                        if len(form.cleaned_data.get('password1')) < 8:
                            form._errors["password1"] = ErrorList(
                                [_(u"Пароль должен быть длиннее 8 символов")]
                            )
                            return render(request, 'orders/new-order.html',
                                          {'cart': cart, 'form': form, 'categories': get_category()})
                        user = get_user_model().objects.create_user(first_name=form.cleaned_data.get('first_name'),
                                                                    last_name=form.cleaned_data.get('last_name'),
                                                                    email=form.cleaned_data.get('email'),
                                                                    password=form.cleaned_data.get('password1'))
                        user.save()
                        user = authenticate(email=form.cleaned_data.get('email'),
                                            password=form.cleaned_data.get('password1'))
                        login(request, user)
                        order = Order.objects.create(first_name=form.cleaned_data.get('first_name'),
                                                     last_name=form.cleaned_data.get('last_name'),
                                                     email=user.email,
                                                     number=form.cleaned_data.get('number'))
                    else:
                        form._errors["password1"] = ErrorList([_(u"Пароли не совпадают")])
                        return render(request, 'orders/new-order.html',
                                      {'cart': cart, 'form': form, 'categories': get_category()})
                # order = form.save()
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
        if request.user.is_authenticated:
            data = {'first_name': request.user.first_name,
                    'last_name': request.user.last_name,
                    'email': request.user.email,
                    }
            form = OrderUserCreateForm(data)
            form.fields['email'].widget.attrs['readonly'] = True
            form.fields['password1'].widget.attrs['disabled'] = True
            form.fields['password2'].widget.attrs['disabled'] = True
        else:
            form = OrderUserCreateForm
    return render(request, 'orders/new-order.html',
                  {'cart': cart, 'form': form, 'categories': get_category()})


# def order_create(request):
#     cart = Cart(request)
#     if request.method == 'POST':
#         form = OrderUserCreateForm(request.POST)
#         if form.is_valid():
#             order = Order.objects.create(first_name=form.cleaned_data.get('first_name'),
#                                          last_name=form.cleaned_data.get('last_name'),
#                                          email=form.cleaned_data.get('email'),
#                                          number = form.cleaned_data.get('number'))
#             for item in cart:
#                 OrderItem.objects.create(order=order,
#                                          offer=item['product'],
#                                          price=item['price'],
#                                          quantity=item['quantity'],
#                                          )
#             # очистка корзины
#             cart.clear()
#             return redirect('order_create_delivery', pk=order.pk)
#     else:
#         form = OrderUserCreateForm
#     return render(request, 'orders/new-order.html',
#                   {'cart': cart, 'form': form})


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
                  {'pk': order.pk, 'form': form, 'categories': get_category()})


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
    return render(request, 'orders/order-payment.html',
                  {'order': order, 'form': form, 'categories': get_category()})
