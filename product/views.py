from random import sample
from django.shortcuts import render  # noqa F401
from django.views import generic
from django.core.cache import cache

from django.conf import settings
from product.models import Banner, Product, Category, Offer, ProductImage


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


class CategoryView(generic.ListView):
    """Тест. Отображение категорий каталога"""
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
        return context


class CatalogListView(generic.ListView):
    model = Product
    context_object_name = 'catalog'
    #template_name = 'product/catalog-view.html'
    template_name = 'product/base-template-2.html'
    paginate_by = 6

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories_list = Category.objects.all()
        context['categories'] = categories_list
        return context

    def get_queryset(self, *args, **kwargs):
        print(self.kwargs)
        queryset = Product.objects.all()
        return queryset

class HomeView(generic.TemplateView):
    template_name = 'product/base-template-1.html'

class CatalogView(generic.TemplateView):
    template_name = 'product/base-template-2.html'
