from django.urls import path
from product.views import ProductDetailView, CategoryView, FeedbackDetailView, \
    HistoryViewsView, ProductCatalogView, IndexView


urlpatterns = [
    path('<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('category/', CategoryView.as_view(), name='category'),
    path('offer/<int:pk>/', FeedbackDetailView.as_view(), name='offer-detail'),
    path('catalog/', ProductCatalogView.as_view(), name='catalog-view'),
    path('history_view/', HistoryViewsView.as_view(), name='history_view'),
    path('index/', IndexView.as_view(), name='index'),
]
