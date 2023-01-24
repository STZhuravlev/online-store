from django.contrib import admin  # noqa F401
from django.utils.translation import gettext_lazy as _
from mptt.admin import MPTTModelAdmin
from product.models import (
    Product,
    Banner,
    Category,
    Offer,
    Property,
    ProductProperty,
)


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


class CategoryAdmin(MPTTModelAdmin):
    list_display = ['name', 'active', 'parent']

    class Meta:
        verbose_name = _('категория')
        verbose_name_plural = _('категории')


class OfferAdmin(admin.ModelAdmin):
    list_display = ['product', 'seller', 'price']

    class Meta:
        verbose_name = _('цена')
        verbose_name_plural = _('цены')


class PropertyAdmin(admin.ModelAdmin):
    list_display = ['name', ]


class ProductPropertyAdmin(admin.ModelAdmin):
    list_display = ['product', 'property', 'value']


admin.site.register(Product, ProductAdmin)
admin.site.register(Banner, BannerAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Offer, OfferAdmin)
admin.site.register(ProductProperty, ProductPropertyAdmin)
admin.site.register(Property, PropertyAdmin)
