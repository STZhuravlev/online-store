from django.contrib import admin  # noqa F401
from mptt.admin import MPTTModelAdmin
from product.models import Product, Banner, Category, Offer, Property, ProductProperty


class ProductAdmin(admin.ModelAdmin):
    list_display = ['name']


class BannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'added_at', 'is_active']
    list_editable = ['is_active']


class CategoryAdmin(MPTTModelAdmin):
    mptt_level_indent = 2
    list_display = ['name', 'active', 'parent']


class OfferAdmin(admin.ModelAdmin):
    list_display = ['product', 'seller', 'price']


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
