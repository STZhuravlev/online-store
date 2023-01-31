from django.urls import path
from product import views


urlpatterns = [
    path('banners/', views.BannersView.as_view(), name='banners'),
    path('<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('category/', views.CategoryView.as_view(), name='category'),
    path('catalog/', views.CatalogListView.as_view(), name='catalog-view'),
    path('offer/<int:pk>/', views.OfferDetailView.as_view(), name='offer-detail'),
]
