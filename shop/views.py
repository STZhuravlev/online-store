from django.views.generic import DetailView, View
from .models import Seller
from django.shortcuts import render, redirect
from .service import SiteSettings
from django.conf import settings
from .forms import SiteSettingsForm
class SellerInfo(DetailView):
    model = Seller
    template_name = 'shop/seller.html'
    context_object_name = 'seller'

class SiteSettingsView(View):

    def get(self, request):
        site = SiteSettings(request)
        form = SiteSettingsForm()
        print(site.site_settings)
        for item, key in site.site_settings.items():
            print(item, key)
        return render(request, 'shop/site_settings.html', {'site': site, 'form': form})

    def post(self, request):
        site_settings = SiteSettings(request)
        form = SiteSettingsForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            site_settings.add(name=cd['name'],
                              value=cd['value'])
            site_settings.save()
            return redirect('settings')


class ViewSetting(View):
    def get(self, request):
        context = self.request.session.get(settings.ADMIN_SETTINGS_ID)
        print(context['PROMO_PER_PAGE'])
        print(context['first market'])
        return render(request, 'shop/view.html', {'context':context})


# Может делать только администратор магазина, владелец
# Сделать