from django.urls import path
from product.views import BannersView, ProductDetailView, CategoryView, OfferDetailView, ProductCatalogView
from product import views

urlpatterns = [
    path('banners/', BannersView.as_view(), name='banners'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('category/', CategoryView.as_view(), name='category'),
    path('offer/<int:pk>/', OfferDetailView.as_view(), name='offer-detail'),
    path('catalog/', ProductCatalogView.as_view(), name='catalog-view'),
]
