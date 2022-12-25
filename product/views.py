from random import sample
from django.shortcuts import render  # noqa F401
from django.views import generic
from django.core.cache import cache
from product.models import Banner, Product, Goods


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


class GoodsDetailView(generic.DetailView):
    model = Goods
    template_name = 'product/goods-detail.html'
    context_object_name = 'goods'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['goods_sellers'] = Goods.objects.filter(product=Goods.objects.get(id=self.kwargs['pk']).product)
        return context
