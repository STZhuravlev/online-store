from django.core.cache import cache
from django.conf import settings
from django.db.models import QuerySet, Q
from django.http import HttpRequest
from product.models import Category, Product


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
                prefetch_related('seller'). \
                filter(category__tree_id=category.tree_id).\
                only('name', 'seller__name', 'category_id')
        else:  # if child category, select products of this category
            queryset = Product.objects. \
                select_related('category'). \
                prefetch_related('seller'). \
                filter(category=category_id).\
                only('name', 'seller__name', 'category_id')
    else:  # if category isn't passed in query-string
        queryset = Product.objects. \
            prefetch_related('seller'). \
            only('name', 'seller__name', 'category_id')

    return queryset


def apply_filter_to_catalog(request: HttpRequest, queryset: QuerySet) -> QuerySet:
    """
    Возвращает отфильтрованный список товаров в выбранной категории товаров
    :param request: HTTP request, в query-string которого указаны параметры сортировки
    :param queryset: список товаров в выбранной категории товаров
    :return:
    """
    print(0)
    for item in queryset:
        print(type(item))
        print(item.id, item.seller.all())
    # filter for price
    price = request.GET.get('price')
    if price is not None:
        price_from, price_to = map(int, price.split(';'))
        queryset = queryset.filter(Q(offers__price__gte=price_from) &
                                   Q(offers__price__lte=price_to))
    print(1)
    for item in queryset:
        print(type(item))
        print(item.id, item.seller.all())
    # filter for seller
    seller = request.GET.get('seller')

    if seller is not None:
        queryset = queryset.filter(seller__name=seller)
    for item in queryset:
        print(type(item))
        print(item.id, item.seller.all())

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
