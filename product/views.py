from django.shortcuts import render, redirect  # noqa F401
from django.views import generic
from django.core.cache import cache
from django.urls import reverse
from django.db.models import Prefetch
from django.conf import settings
from product.services import (
    get_category,
    get_queryset_for_category,
    apply_filter_to_catalog,
    BannersView,
    ImageView
)
from .forms import FeedbackForm
from shop.models import Seller
from product.models import (
    Product,
    Category,
    Offer,
    HistoryView,
    ProductProperty,
    Feedback,
    ProductImage
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
    template_name = 'product/product-catalog.html'
    paginate_by = CATALOG_PRODUCT_PER_PAGE

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = get_category()
        context['current_category'] = self.request.GET.get('category', '')
        context['sellers'] = Seller.objects.all()
        history_list = HistoryView.objects.all()[:5]
        context['history_list'] = history_list
        return context

    def get_queryset(self):
        category_id = self.request.GET.get('category', '')
        cache_key = f'products:{category_id}'

        # get queryset for selected category
        queryset = get_queryset_for_category(request=self.request)

        # put queryset to cache
        cached_data = cache.get_or_set(cache_key, queryset, settings.CACHE_STORAGE_TIME)

        # apply filters parameters to products in catalog
        # insert if condition
        final_queryset = apply_filter_to_catalog(request=self.request,
                                                 queryset=cached_data)

        # apply sort parameters to products in catalog
        # insert method

        return final_queryset


class IndexView(generic.TemplateView):
    template_name = 'product/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['banners'] = BannersView.get_banners()
        context['categories'] = get_category()
        return context
