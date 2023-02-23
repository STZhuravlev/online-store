from django.views.generic import DetailView, View
from product.services import get_category
from product.models import Offer
from .models import Seller
from orders.models import OrderItem
from .service import SiteSettings
from .forms import SiteSettingsForm
from django.shortcuts import render, redirect


class SellerInfo(DetailView):
    model = Seller
    template_name = 'shop/seller.html'
    context_object_name = 'seller'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        popular = {}
        popular_queryset = OrderItem.objects.filter(offer__seller_id=self.object.id). \
            values_list('offer__id', 'quantity')
        for i in popular_queryset:
            if i[0] in popular:
                popular[str(i[0])] += int(i[1])
            else:
                popular[str(i[0])] = int(i[1])
        context['popular'] = Offer.objects.filter(pk__in=sorted(popular, reverse=True)[:10])
        context['categories'] = get_category()
        return context

class SiteSettingsView(View):

    def get(self, request):
        site = SiteSettings(request)
        form = SiteSettingsForm()
        name = ['PROMO_PER_PAGE', 'PROMO_PRODUCTS_PER_PAGE', 'CATALOG_PRODUCT_PER_PAGE', 'CACHE_STORAGE_TIME']
        return render(request, 'shop/site_settings.html', {'site': site, 'form': form, 'name': name})

    def post(self, request):
        site_settings = SiteSettings(request)
        form = SiteSettingsForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            site_settings.add(name=cd['name'],
                              value=cd['value'])
            site_settings.save()
            return redirect('settings')