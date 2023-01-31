from django.shortcuts import render
from django.views.generic import ListView
from promotions.models import Promo
from product.services import get_category


PROMO_PER_PAGE = 4


class PromoListView(ListView):
    template_name = 'promotions/promo-list.html'
    paginate_by = PROMO_PER_PAGE
    queryset = Promo.objects.filter(is_active=True)
    context_object_name = 'promotions'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = get_category()
        return context
