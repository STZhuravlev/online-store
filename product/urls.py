from django.urls import path
from product import views

urlpatterns = [
    path('banners/', views.BannersView.as_view(), name='banners'),
    path('<int:pk>/', views.ProductDetailView.as_view(), name='product-detail'),
    path('category/', views.CategoryView.as_view(), name='category'),
    path('offer/<int:pk>/', views.OfferDetailView.as_view(), name='offer-detail'),
    path('history/', views.HistoryOrderView.as_view(), name='history'),
    path('history<int:pk>/', views.HistoryOrderDetailView.as_view(), name='history-detail'),
    path('neworder/', views.NewOrderView.as_view(), name='new-order'),
]
