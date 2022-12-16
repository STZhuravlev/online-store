from django.contrib import admin  # noqa F401
from django.utils.translation import gettext_lazy as _
from product.models import Product, Banner


class ProductAdmin(admin.ModelAdmin):
    list_display = ['name']

    class Meta:
        verbose_name = _('товар')
        verbose_name_plural = _('товары')


class BannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'added_at', 'is_active']
    list_editable = ['is_active']

    class Meta:
        verbose_name = _('баннер')
        verbose_name_plural = _('баннеры')


admin.site.register(Product, ProductAdmin)
admin.site.register(Banner, BannerAdmin)
