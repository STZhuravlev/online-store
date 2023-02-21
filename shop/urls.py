from django.urls import path
from .views import SellerInfo, SiteSettingsView, ViewSetting

urlpatterns = [
    path('seller/<int:pk>', SellerInfo.as_view(), name='seller-info'),
    path('settings', SiteSettingsView.as_view(), name='settings'),
    path('view', ViewSetting.as_view())

]
