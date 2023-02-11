from random import sample
from django.core.cache import cache
from django.conf import settings
from django.db.models import QuerySet, Q, Avg
from django.http import HttpRequest
from product.models import Category, Product, Banner, ProductImage


def get_category(cache_key: str = None,
                 cache_time: int = settings.CACHE_STORAGE_TIME) -> QuerySet:
    """
    Возвращает кэшированный список активных категорий
    :param cache_key: ключ кеша
    :param cache_time: время кэширования в секундах
    :return:
    """
    categories = Category.objects.filter(active=True)
    if cache_key is None:
        cache_key = 'categories'
    cached_data = cache.get_or_set(cache_key, categories, cache_time)
    return cached_data


def get_queryset_for_category(request: HttpRequest) -> QuerySet:
    """
    Возвращает список продуктов в заданной категории товаров.
    Если категория не задана, возвращает список всех продуктов.
    :param request: HTTP request, в query-string которого содержится название категории товара
    :return: QuerySet
    """
    category_id = request.GET.get('category', '')

    if category_id:  # if category is passed in query-string
        category = Category.objects.get(id=category_id)
        parent = category.parent
        if parent is None:  # if root category, select products of full tree category
            queryset = Product.objects. \
                select_related('category'). \
                filter(category__tree_id=category.tree_id).all()
        else:  # if child category, select products of this category
            queryset = Product.objects. \
                select_related('category'). \
                filter(category=category_id).all()
    else:  # if category isn't passed in query-string
        queryset = Product.objects. \
            select_related('category').all()
    # select required fields and add average price on seller
    if queryset:
        queryset = queryset. \
            values('id', 'name', 'images__image', 'category__name'). \
            annotate(avg_price=Avg('offers__price')). \
            order_by('avg_price')

    return queryset


def apply_filter_to_catalog(request: HttpRequest, queryset: QuerySet) -> QuerySet:
    """
    Возвращает отфильтрованный список товаров в выбранной категории товаров
    :param request: HTTP request, в query-string которого указаны параметры сортировки
    :param queryset: список товаров в выбранной категории товаров
    :return:
    """
    # filter for price
    price = request.GET.get('price')
    if price:
        price_from, price_to = map(int, price.split(';'))
        queryset = queryset.filter(Q(offers__price__gte=price_from) &
                                   Q(offers__price__lte=price_to))

    # filter for seller
    seller = request.GET.get('seller')
    if seller:
        queryset = queryset.filter(seller__name=seller)

    # filter for title
    title = request.GET.get('title')
    if title:
        queryset = queryset.filter(name__icontains=title)

    # filter for free delivery
    delivery = request.GET.get('deliv')
    if delivery == 'on':
        pass

    # filter for product in stock
    stock = request.GET.get('stock')
    if stock == 'on':
        pass

    return queryset


class BannersView:
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


class ImageView:
    @staticmethod
    def get_image(product_id):
        context = ProductImage.objects.filter(product=product_id).all()
        return context
