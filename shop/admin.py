from django.contrib import admin  # noqa F401
from django.utils.translation import gettext_lazy as _
from shop.models import Seller, SellerLogo


class SellerAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'description', 'address', 'number']

    class Meta:
        verbose_name = _('продавец')
        verbose_name_plural = _('продавцы')


class SellerLogoAdmin(admin.ModelAdmin):
    pass

    class Meta:
        verbose_name = _('логотип продавца')
        verbose_name_plural = _('логотипы продавцов')


admin.site.register(Seller, SellerAdmin)
admin.site.register(SellerLogo, SellerLogoAdmin)
