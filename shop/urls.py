from django.urls import path
from .views import SellerInfo

urlpatterns = [
    path('seller/<int:pk>', SellerInfo.as_view(), name='seller-info'),
]
