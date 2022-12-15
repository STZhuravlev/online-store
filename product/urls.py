from django.urls import path
from product.views import BannersView, ProductDetailView

urlpatterns = [
    path('banners/', BannersView.as_view(), name='banners'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
]
