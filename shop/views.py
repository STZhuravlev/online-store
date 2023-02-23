from django.views.generic import DetailView, View
from .models import Seller
from django.shortcuts import render, redirect
from .service import SiteSettings
from .forms import SiteSettingsForm


class SellerInfo(DetailView):
    model = Seller
    template_name = 'shop/seller.html'
    context_object_name = 'seller'


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
