from django.urls import path
from product.views import BannersView, ProductDetailView, CategoryView, OfferDetailView, \
    CategoryDetailView, HistoryViewsView

urlpatterns = [
    path('banners/', BannersView.as_view(), name='banners'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('category/', CategoryView.as_view(), name='category'),
    path('offer/<int:pk>/', OfferDetailView.as_view(), name='offer-detail'),
    path("category/<int:pk>", CategoryDetailView.as_view(), name='category_detail'),
    path('history_view/', HistoryViewsView.as_view(), name='history_view'),

]
