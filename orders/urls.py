from django.urls import path
from orders import views

urlpatterns = [
    path('history/', views.HistoryOrderView.as_view(), name='history'),
    path('history<int:pk>/', views.HistoryOrderDetailView.as_view(), name='history-detail'),
    path('create/', views.order_create, name='order_create'),
    path('create/delivery/<int:pk>/', views.order_create_delivery, name='order_create_delivery'),
    path('create/payment/<int:pk>/', views.order_create_payment, name='order_create_payment'),
]
