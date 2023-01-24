from django.urls import path
from orders import views

urlpatterns = [
    path('history/', views.HistoryOrderView.as_view(), name='history'),
    path('history<int:pk>/', views.HistoryOrderDetailView.as_view(), name='history-detail'),
    path('create/', views.order_create, name='order_create'),
]
