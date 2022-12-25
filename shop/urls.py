from django.urls import path
from django.contrib.auth import views as auth_views
from .views import SellerInfo

urlpatterns = [
    path('seller/<int:pk>', SellerInfo.as_view(), name='seller-info'),
]
