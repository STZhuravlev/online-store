from django.urls import path, include
from .views import CartView, CartAdd, CartRemove, CartDelete


app_name = 'cart'


urlpatterns = [
    path('', include([
        path('cart', CartView.as_view(), name='cart'),
        path('<id>/add/', CartAdd.as_view(), name='cart-add'),
        path('<id>/remove', CartRemove.as_view(), name='cart-remove'),
        path('delete/', CartDelete.as_view(), name='cart-delete')
    ])),
]
