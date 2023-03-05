from random import randint

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.http import HttpResponse
import datetime
from django.shortcuts import render, redirect  # noqa F401
from django.views import generic
from django.core.cache import cache
from django.urls import reverse
from django.db.models import Prefetch
from django.conf import settings

from .forms import FeedbackForm, UploadProductFileJsonForm
from shop.models import Seller

from config.settings_local import CACHE_STORAGE_BANNERS_TIME
from product.models import (
    Product,
    Category,
    Offer,
    HistoryView,
    ProductProperty,
    Feedback,
    ProductImage,
    LoggingImportFileModel,
)

from product.services import (
    get_category,
    get_queryset_for_category,
    apply_filter_to_catalog,
    apply_sorting_to_catalog,
    get_banners,
    BannersView,
    ImageView,
    get_favorite_categories,
    get_popular_products,
    get_limited_edition,
    upload_product_file,
)


# Количество товаров из каталога, которые будут отображаться на странице
CATALOG_PRODUCT_PER_PAGE = 6  # для отображения страницы в стандартном десктопном браузере


class ProductDetailView(generic.DetailView, generic.CreateView):
    model = Product
    template_name = 'product/product-detail.html'
    context_object_name = 'product'
    form_class = FeedbackForm

    def get_success_url(self):
        return reverse('product-detail', kwargs={'pk': self.object.product.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = get_category()
        context['drawing'] = ImageView.get_image(product_id=self.kwargs['pk'])
        context['property'] = Product.objects.\
            prefetch_related(
            Prefetch('property', queryset=ProductProperty.objects.select_related(
                'product', 'property').filter(product=self.kwargs['pk'])))
        context['feedback'] = Feedback.objects.all().filter(product=self.kwargs['pk'])
        context['feedback_form'] = FeedbackForm()
        histiry_view_list = HistoryView.objects.filter(product=Product.objects.get(id=self.kwargs['pk']))
        context['offer_seller'] = Offer.objects.all().filter(product=self.object.id)
        if histiry_view_list:
            history_old = HistoryView.objects.get(product=Product.objects.get(id=self.kwargs['pk']))
            history_old.save(update_fields=['view_at'])
        else:
            history_new = HistoryView(product=self.object, user=self.request.user)
            history_new.save()
        return context

    def form_valid(self, form, **kwargs):
        form.save(commit=False)
        if self.request.FILES:
            form.instance.image = self.request.FILES['image']
        form.instance.author = self.request.user
        form.instance.product_id = self.kwargs['pk']
        return super().form_valid(form)


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


class FeedbackDetailView(generic.DetailView, generic.CreateView):

    """Детальное отображение продукта, отзывов и добавления отзыва"""

    model = Offer
    form_class = FeedbackForm
    template_name = 'product/offer-detail.html'
    context_object_name = 'offer'

    def get_success_url(self):
        return reverse('offer-detail', kwargs={'pk': self.object.product.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['offers'] = Offer.objects.filter(product=Offer.objects.get(id=self.kwargs['pk']).product)
        context['categories'] = get_category()
        context['product_image'] = ProductImage.objects.filter(product=Offer.objects.get(id=self.kwargs['pk']).product)
        context['feedback'] = Feedback.objects.filter(product=Offer.objects.get(id=self.kwargs['pk']).product)
        return context

    def form_valid(self, form, **kwargs):
        form.save(commit=False)
        if self.request.FILES:
            form.instance.image = self.request.FILES['image']
        form.instance.author = self.request.user
        form.instance.product_id = self.kwargs['pk']
        return super().form_valid(form)


class HistoryViewsView(generic.ListView):
    template_name = 'product/history-view.html'
    model = HistoryView

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        history_list = HistoryView.objects.all()[:5]
        context['history_list'] = history_list
        return context


class MainPageView(generic.TemplateView):
    template_name = 'product/index-2.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # получает список категорий
        context['categories'] = get_category()

        # получает список баннеров
        cached_data = cache.get_or_set('banners',
                                       get_banners(),
                                       CACHE_STORAGE_BANNERS_TIME)
        context['banners'] = cached_data

        # получает список избранных категорий
        context['favorite'] = get_favorite_categories()

        # получает список популярных товаров
        context['popular'] = get_popular_products()

        # передает дату, до которой действует предложение дня
        next_day = datetime.datetime.today() + datetime.timedelta(days=1)
        next_day = next_day.strftime('%d.%m.%Y')
        context['next_day'] = next_day

        # получает предложение дня и список товаров ограниченного тиража
        day_offer, limited = get_limited_edition()
        context['day_offer'] = day_offer
        context['limited'] = limited

        return context


class ProductCatalogView(generic.ListView):
    """Отображает товары из заданной категории товаров,
    применяет к ним набор фильтров и сортировку."""
    model = Product
    context_object_name = 'catalog'
    template_name = 'product/product-catalog.html'
    paginate_by = CATALOG_PRODUCT_PER_PAGE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = get_category()
        context['current_category'] = self.request.GET.get('category', '')
        seller_list = Seller.objects.all()
        seller_cached = cache.get_or_set('seller_cache', seller_list, settings.CACHE_STORAGE_TIME)
        context['sellers'] = seller_cached

        return context

    def get_queryset(self):
        # category_id = self.request.GET.get('category', '')
        query_param = [f"{key}={value}" for key, value in self.request.GET.items() if key != 'page']
        if query_param:
            cache_key_2 = ''.join(query_param)
        else:
            cache_key_2 = 'blank'
        # cache_key = f'products:{category_id}'

        # get queryset for selected category
        queryset = get_queryset_for_category(request=self.request)

        # put queryset to cache
        # cached_data = cache.get_or_set(cache_key, queryset, settings.CACHE_STORAGE_TIME)

        # apply filters parameters to products in catalog
        filtered_queryset = apply_filter_to_catalog(request=self.request,
                                                    queryset=queryset)

        # apply sort parameters to products in catalog
        sorted_queryset = apply_sorting_to_catalog(request=self.request,
                                                   queryset=filtered_queryset)

        cached_data = cache.get_or_set(cache_key_2, sorted_queryset, settings.CACHE_STORAGE_TIME)

        return cached_data


# class IndexView(generic.TemplateView):
#     template_name = 'product/index.html'
#
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context['banners'] = BannersView.get_banners()
#         context['categories'] = get_category()
#         return context


class UploadProductFileView(PermissionRequiredMixin, generic.FormView):

    """Добавление продукта, автора и т.п. через файл формата JSON """

    template_name = 'product/upload_file.html'
    permission_required = ('users.seller_rights', )
    form_class = UploadProductFileJsonForm

    def handle_no_permission(self):
        return HttpResponse('Нету доступа')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = get_category()
        return context

    def form_valid(self, form, **kwargs):
        file = self.request.FILES['file_json']
        if file.name.endswith('.json'):
            seller = Seller.objects.get(user=self.request.user)
            file_name = f'{randint(1, 9999)}_{file.name}'

            try:
                upload_product_file(file=file, seller=seller, file_name=file_name)
                get_logger_error = LoggingImportFileModel.objects.filter(file_name=file_name, seller=seller)

                if get_logger_error:
                    return render(self.request, 'product/logger_error.html', {'logger_error': get_logger_error,
                                                                              'categories': get_category()})
                return redirect('catalog-view')
            except (TypeError, ValueError) as ex:
                LoggingImportFileModel.objects.create(
                    file_name=file_name,
                    seller=seller,
                    message=f'Ошибка парсинга файла: {ex} | {type(ex)}'
                )
                form.add_error(None, f'Ошибка: {ex} | {type(ex)}! Не корректно сформирован файл')
                return render(self.request, 'product/upload_file.html', context={'form': form,
                                                                                 'categories': get_category()})
        form.add_error(None, 'Кодировка файла должна быть формата JSON')
        return render(self.request, 'product/upload_file.html', context={'form': form, 'categories': get_category()})
