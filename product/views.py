from random import sample
from django.shortcuts import render, redirect  # noqa F401
from django.views import generic
from django.core.cache import cache
from django.http import HttpResponse
from django.conf import settings
from product.models import Banner, Product, Category, Offer, HistoryView
from shop.models import Seller
from product.services import get_category, get_queryset_for_category, \
    apply_filter_to_catalog


# Количество товаров из каталога, которые будут отображаться на странице
# CATALOG_PRODUCT_PER_PAGE = 6 для отображения страницы в стандартном десктопном браузере
CATALOG_PRODUCT_PER_PAGE = 6


class BannersView(generic.TemplateView):
    """Тест. Отображение баннеров"""
    template_name = 'product/banners-view.html'

    @staticmethod
    def get_banners(qty: int = 3):
        """ Возвращает список из qty активных баннеров. """
        banners = Banner.objects.filter(is_active=True)
        result = []
        if banners.exists():
            if 3 < qty < 1:
                qty = 3
            if banners.count() < qty:
                qty = banners.count()
            banners = list(banners)
            result = sample(banners, k=qty)
        return result

    def get_context_data(self, qty: int = 3, **kwargs):
        """ Добавляет в контекст список баннеров. Список кэшируется. """
        context = super().get_context_data(**kwargs)
        # TODO заменить в ключе имя на емейл
        offers_cache_key = f'offers:{self.request.user.username}'
        # Получаем список баннеров и кэшируем его
        banner_list = self.get_banners(qty=qty)
        cached_data = cache.get_or_set(offers_cache_key, banner_list, 1 * 60)
        context['banners'] = cached_data
        return context


class ProductDetailView(generic.DetailView):
    model = Product
    template_name = 'product/product-detail.html'
    context_object_name = 'product'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        history_view_list = HistoryView.objects.filter(product=self.object)
        if history_view_list:
            history_old = HistoryView.objects.get(product=self.object)
            history_old.save(update_fields=['view_at'])
        else:
            history_new = HistoryView(product=self.object)
            history_new.save()
        return context


class CategoryView(generic.ListView):
    """Отображение категорий каталога"""
    template_name = 'product/category-view.html'
    model = Category
    context_object_name = 'category_list'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories_list = Category.objects.all()
        cached_data = cache.get_or_set("categories", categories_list, settings.CACHE_STORAGE_TIME)
        context['categories'] = cached_data
        return context


class OfferDetailView(generic.DetailView):
    model = Offer
    template_name = 'product/offer-detail.html'
    context_object_name = 'offer'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['offer_sellers'] = Offer.objects.filter(product=Offer.objects.get(id=self.kwargs['pk']).product)
        context['categories'] = get_category()
        return context


class HistoryViewsView(generic.ListView):
    template_name = 'product/history-view.html'
    model = HistoryView

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        history_list = HistoryView.objects.all()[:5]
        context['history_list'] = history_list
        return context


class ProductCatalogView(generic.ListView):
    """Отображает товары из заданной категории товаров,
    применяет к ним набор фильтров и сортировку."""
    model = Product
    context_object_name = 'catalog'
    template_name = 'product/base-template-2.html'
    paginate_by = CATALOG_PRODUCT_PER_PAGE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = get_category()
        context['current_category'] = self.request.GET.get('category', '')
        context['sellers'] = Seller.objects.all()
        return context

    def get_queryset(self):
        print(self.request.GET)
        category_id = self.request.GET.get('category', '')
        cache_key = f'products:{category_id}'

        # get queryset for selected category
        queryset = get_queryset_for_category(request=self.request)

        # put queryset to cache
        #cached_data = cache.get_or_set(cache_key, queryset, settings.CACHE_STORAGE_TIME)
        cached_data = cache.get_or_set(cache_key, queryset, 1)

        # apply filters parameters to products in catalog
        # insert if condition
        final_queryset = apply_filter_to_catalog(request=self.request,
                                                 queryset=cached_data)

        # apply sort parameters to products in catalog
        # insert method

        return final_queryset

