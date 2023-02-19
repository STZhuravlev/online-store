"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('__debug__/', include('debug_toolbar.urls')),
    path('user/', include('users.urls')),
    path('product/', include('product.urls')),
    path('shop/', include('shop.urls')),
    path('comparison/', include('comparison.urls')),
    path('cart/', include('cart.urls')),
    path('orders/', include('orders.urls')),
    path('promos/', include('promotions.urls', namespace='promo')),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
