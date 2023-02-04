from django.shortcuts import render, redirect  # noqa F401
from django.views import generic
from django.core.cache import cache
from django.db.models import Prefetch
from django.conf import settings
from product.models import Product, Category, Offer, HistoryView, ProductProperty, Feedback, ProductImage
from product.services import get_category, BannersView, ImageView
from .forms import FeedbackForm
from django.urls import reverse
# Количество товаров из каталога, которые будут отображаться на странице
# CATALOG_PRODUCT_PER_PAGE = 6 для отображения страницы в стандартном десктопном браузере
CATALOG_PRODUCT_PER_PAGE = 6


# class BannersView(generic.TemplateView):
#     """Тест. Отображение баннеров"""
#     template_name = 'product/banners-view.html'
#
#     @staticmethod
#     def get_banners(qty: int = 3):
#         """ Возвращает список из qty активных баннеров. """
#         banners = Banner.objects.filter(is_active=True)
#         result = []
#         if banners.exists():
#             if 3 < qty < 1:
#                 qty = 3
#             if banners.count() < qty:
#                 qty = banners.count()
#             banners = list(banners)
#             result = sample(banners, k=qty)
#         return result
#
#     def get_context_data(self, qty: int = 3, **kwargs):
#         """ Добавляет в контекст список баннеров. Список кэшируется. """
#         context = super().get_context_data(**kwargs)
#         # TODO заменить в ключе имя на емейл
#         offers_cache_key = f'offers:{self.request.user.username}'
#         # Получаем список баннеров и кэшируем его
#         banner_list = self.get_banners(qty=qty)
#         cached_data = cache.get_or_set(offers_cache_key, banner_list, 1 * 60)
#         context['banners'] = cached_data
#         return context


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
        context['drawing'] = ImageView.get_image(product_id=self.object.id)
        context['property'] = Product.objects.\
            prefetch_related(
            Prefetch('property', queryset=ProductProperty.objects.select_related(
                'product', 'property').filter(product=self.object.id)))
        context['feedback'] = Feedback.objects.all().filter(product=self.object.id)
        context['feedback_form'] = FeedbackForm()
        histiry_view_list = HistoryView.objects.filter(product=self.object)
        if histiry_view_list:
            history_old = HistoryView.objects.get(product=self.object)
            history_old.save(update_fields=['view_at'])
        else:
            history_new = HistoryView(product=self.object)
            history_new.save()
        return context

    def form_valid(self, form, **kwargs):
        form.save(commit=False)
        if self.request.FILES:
            form.instance.image = self.request.FILES['image']
        form.instance.author = self.request.user
        form.instance.product_id = self.kwargs['pk']
        form.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        return self.render_to_response(self.get_context_data(form=form))


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


class FeedbackDetailView(generic.CreateView):

    """Детальное отображение продукта, отзывов и добавления отзыва"""

    model = Feedback
    form_class = FeedbackForm
    template_name = 'product/offer-detail.html'

    def get_success_url(self):
        return reverse('offer-detail', kwargs={'pk': self.object.product.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['offer'] = Offer.objects.filter(product=Offer.objects.get(id=self.kwargs['pk']).product)
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


class CatalogListView(generic.ListView):
    model = Product
    context_object_name = 'catalog'
    template_name = 'product/base-template-2.html'
    paginate_by = CATALOG_PRODUCT_PER_PAGE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = get_category()
        return context

    def get_queryset(self, *args, **kwargs):
        queryset = Product.objects.all()
        return queryset


class HistoryViewsView(generic.ListView):
    template_name = 'product/history-view.html'
    model = HistoryView

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        history_list = HistoryView.objects.all()[:5]
        context['history_list'] = history_list
        return context


class IndexView(generic.TemplateView):
    template_name = 'product/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['banners'] = BannersView.get_banners()
        context['categories'] = get_category()
        return context
