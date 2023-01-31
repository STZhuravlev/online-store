from django.urls import path
from promotions.views import PromoListView


urlpatterns = [
    path('promo/', PromoListView.as_view(), name='promo-list'),

]
