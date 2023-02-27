from django.core.paginator import Paginator
from django.db.models import Avg
from django.views.generic import ListView, DetailView
from promotions.models import Promo
from product.models import Product
from product.services import get_category
from django.conf import settings


# Количество акция, отображаемых на странице
# PROMO_PER_PAGE = 4
# Количество продуктов в акции, отображаемых на странице
# PROMO_PRODUCTS_PER_PAGE = 4


class PromoListView(ListView):
    template_name = 'promotions/promo-list.html'
    # paginate_by = PROMO_PER_PAGE
    queryset = Promo.objects.filter(is_active=True)
    context_object_name = 'promotions'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = get_category()
        return context

    def get_paginate_by(self, queryset):
        promo_per_page = self.request.session.get(settings.ADMIN_SETTINGS_ID)
        if promo_per_page is None or promo_per_page.get('PROMO_PER_PAGE') is None:
            paginator = settings.PROMO_PER_PAGE
        else:
            paginator = promo_per_page['PROMO_PER_PAGE']
        return paginator


class PromoDetailView(DetailView):
    template_name = 'promotions/promo-detail.html'
    model = Promo
    context_object_name = 'promo'

    def get_related_products(self):
        product_list = self.object.promo2products.first()
        if hasattr(product_list, 'product'):
            product_list = product_list.product. \
                select_related('category'). \
                annotate(avg_price=Avg('offers__price'))
        else:
            product_list = Product.objects.\
                select_related('category'). \
                annotate(avg_price=Avg('offers__price')).all()
        promo_product_per_page = self.request.session.get(settings.ADMIN_SETTINGS_ID)
        if promo_product_per_page is None or promo_product_per_page.get('PROMO_PRODUCTS_PER_PAGE') is None:
            count_per_page = settings.PROMO_PRODUCTS_PER_PAGE
        else:
            count_per_page = promo_product_per_page['PROMO_PRODUCTS_PER_PAGE']
        paginator = Paginator(product_list.order_by('id'), count_per_page)
        page_number = self.request.GET.get('page')
        products = paginator.get_page(page_number)
        return products

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = get_category()
        products = self.get_related_products()
        context['page_obj'] = products
        return context
