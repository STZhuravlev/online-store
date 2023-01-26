from django.contrib import admin  # noqa F401
from django.utils.translation import gettext_lazy as _
from mptt.admin import MPTTModelAdmin
from product.models import Product, Banner, Category, Offer, ProductProperty, \
    Feedback, HistoryView, ProductImage, Property


class ProductInLine(admin.TabularInline):
    model = Product.property.through


class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', ]
    inlines = [ProductInLine, ]

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
    list_display = ['name', 'active', 'parent', 'icon']

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


class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'image']

    class Meta:
        verbose_name = _('изображение продукта')
        verbose_name_plural = _('изображения продуктов')


class HistoryViewAdmin(admin.ModelAdmin):
    """ТЕСТ истории просмотра"""
    list_display = ['product', 'view_at']

    class Meta:
        verbose_name = _('история просмотров')
        verbose_name_plural = _('истории просмотров')


class FeedbackAdmin(admin.ModelAdmin):
    list_display = ['product', 'author', 'publication_date', 'rating', 'description', 'image']


admin.site.register(Product, ProductAdmin)
admin.site.register(Banner, BannerAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Offer, OfferAdmin)
admin.site.register(ProductProperty, ProductPropertyAdmin)
admin.site.register(ProductImage, ProductImageAdmin)
admin.site.register(HistoryView, HistoryViewAdmin)
admin.site.register(Property, PropertyAdmin)
admin.site.register(Feedback, FeedbackAdmin)
