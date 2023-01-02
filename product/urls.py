from django.urls import path
from product.views import BannersView, ProductDetailView, OfferDetailView

urlpatterns = [
    path('banners/', BannersView.as_view(), name='banners'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('offer/<int:pk>/', OfferDetailView.as_view(), name='offer-detail'),
]
