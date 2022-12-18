from django.contrib import admin  # noqa F401
from django.utils.translation import gettext_lazy as _
from mptt.admin import MPTTModelAdmin
from product.models import Product, Banner, Category, Price, Goods


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
    mptt_level_indent = 2
    list_display = ['category', 'active', 'parent']

    class Meta:
        verbose_name = _('категория')
        verbose_name_plural = _('категории')


class PriceAdmin(admin.ModelAdmin):
    list_display = ['price', 'discount_price']

    class Meta:
        verbose_name = _('цена')
        verbose_name_plural = _('цены')


class GoodsAdmin(admin.ModelAdmin):
    list_display = ['name', 'product', 'image', 'description', 'price']

    class Meta:
        verbose_name = _('товар')
        verbose_name_plural = _('товары')


admin.site.register(Product, ProductAdmin)
admin.site.register(Banner, BannerAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Price, PriceAdmin)
admin.site.register(Goods, GoodsAdmin)
