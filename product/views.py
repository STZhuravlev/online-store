from django.shortcuts import render, redirect  # noqa F401
from django.views import generic, View
from django.core.cache import cache
from django.urls import reverse
from django.db.models import Prefetch
from django.conf import settings
from product.services import get_category, get_queryset_for_category, \
    apply_filter_to_catalog, BannersView, ImageView, upload_product_file
from .forms import FeedbackForm, UploadProductFileJsonForm
from shop.models import Seller
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


class UploadProductFileView(View):

    """Добавление продукта, автора и т.п. через файл формата JSON """

    def get(self, request):

        form = UploadProductFileJsonForm()
        return render(request, 'product/upload_file.html', context={'form': form, 'categories': get_category()})

    def post(self, request):

        form_file = UploadProductFileJsonForm(request.POST, request.FILES)
        file = request.FILES['file_json']

        if form_file.is_valid() and file.name.endswith('.json'):

            seller = Seller.objects.get(user=self.request.user)

            try:
                upload_product_file(file=file, seller=seller, file_name=file.name)
                return redirect('catalog-view')
            except Exception as ex:
                LoggingImportFileModel.objects.create(
                    seller=seller,
                    message=f'Ошибка парсинга файла: {ex} | {type(ex)}'
                )
                form_file.add_error(None, f'Ошибка: {ex}! Не корректно сформирован файл')
                return render(request, 'product/upload_file.html', context={'form': form_file,
                                                                            'categories': get_category()})
        print('Не валидно')
        form_file.add_error(None, 'Кодировка файла должна быть формата JSON')
        return render(request, 'product/upload_file.html', context={'form': form_file, 'categories': get_category()})


    # def post(self, request):
    #
    #     form_file = UploadProductFileJsonForm(request.POST, request.FILES)
    #     file = request.FILES['file_json']
    #
    #     if form_file.is_valid() and file.name.endswith('.json'):
    #
    #         seller = Seller.objects.get(user=self.request.user)
    #
    #         try:
    #             file_read = form_file.cleaned_data['file_json'].read()
    #             file_json = json.loads(file_read.decode('utf-8'))
    #
    #             for i_category in file_json['category']:
    #                 category = UploadProductFile.get_category(name=i_category)
    #
    #                 for j_product in file_json['category'][i_category]:
    #                     product = UploadProductFile.get_object_or_none(Product, name=j_product['name'])
    #
    #                     if not product:
    #                         try:
    #                             product = Product.objects.create(
    #                                 name=j_product['name'],
    #                                 description=j_product['description'],
    #                                 category=category
    #                             )
    #                         except Exception as ex:
    #                             LoggingImportFileModel.objects.create(
    #                                 seller=seller,
    #                                 message=f'Ошибка при создании экземпляра модели product: {ex} | {type(ex)}'
    #                             )
    #                             continue
    #
    #                         try:
    #                             if j_product.get('image'):
    #                                 # Проблемы с отображением фото товара если URL ссылкой
    #                                 ProductImage.objects.create(
    #                                     product=product,
    #                                     image=j_product['image']
    #                                 )
    #                         except Exception as ex:
    #                             LoggingImportFileModel.objects.create(
    #                                 seller=seller,
    #                                 message=f'Ошибка при создании экземпляра модели product_image: {ex} | {type(ex)}'
    #                             )
    #                             continue
    #
    #                     try:
    #                         if j_product.get('offer'):
    #                             Offer.objects.create(
    #                                 product=product,
    #                                 seller=seller,
    #                                 price=j_product['offer']['price']
    #                             )
    #                     except Exception as ex:
    #                         LoggingImportFileModel.objects.create(
    #                             seller=seller,
    #                             message=f'Ошибка при создании экземпляра модели offer: {ex} | {type(ex)}'
    #                         )
    #                         continue
    #
    #             return redirect('/product/catalog/')
    #         except KeyError as ex:
    #             LoggingImportFileModel.objects.create(
    #                 seller=seller,
    #                 message=f'Ошибка парсинга файла: {ex} | {type(ex)}'
    #             )
    #             form_file.add_error(None, f'Ошибка: {ex}! Не корректно сформирован файл')
    #             return render(request, 'product/upload_file.html', context={'form': form_file})
    #
    #     form_file.add_error(None, 'Кодировка файла должна быть формата JSON')
    #     return render(request, 'product/upload_file.html', context={'form': form_file})
