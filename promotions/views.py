from django.core.paginator import Paginator
from django.views.generic import ListView, DetailView
from promotions.models import Promo
from product.models import Product
from product.services import get_category


PROMO_PER_PAGE = 4
PROMO_PRODUCTS_PER_PAGE = 4


class PromoListView(ListView):
    template_name = 'promotions/promo-list.html'
    paginate_by = PROMO_PER_PAGE
    queryset = Promo.objects.filter(is_active=True)
    context_object_name = 'promotions'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = get_category()
        return context


class PromoDetailView(DetailView):
    template_name = 'promotions/promo-detail.html'
    model = Promo
    context_object_name = 'promo'

    def get_related_products(self):
        product_list = self.object.promo2products.first()
        if hasattr(product_list, 'product'):
            product_list = product_list.product.all()
        else:
            product_list = Product.objects.all()
        paginator = Paginator(product_list, PROMO_PRODUCTS_PER_PAGE)
        page_number = self.request.GET.get('page')
        products = paginator.get_page(page_number)
        return products

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = get_category()
        products = self.get_related_products()
        context['products'] = products
        context['page_obj'] = products
        return context
