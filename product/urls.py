from django.urls import path
from product import views

urlpatterns = [
    path('<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('category/', views.CategoryView.as_view(), name='category'),
    path('offer/<int:pk>/', views.OfferDetailView.as_view(), name='offer-detail'),
    path('catalog', views.CatalogListView.as_view(), name='catalog-view'),
    path('index', views.IndexView.as_view(), name='index'),
]
