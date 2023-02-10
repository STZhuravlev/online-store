from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views import View
from django.views.generic import DetailView, ListView

from product.models import HistoryView
from users.forms import CustomUserChangeForm
from users.models import CustomUser
from .models import Seller


class SellerInfo(DetailView):
    model = Seller
    template_name = 'shop/seller.html'
    context_object_name = 'seller'


class AccauntView(ListView):
    template_name = 'shop/accaunt.html'
    model = HistoryView

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        histories = HistoryView.objects.filter(user=self.request.user)[:3]
        context['histories'] = histories
        return context


class AccauntEditView(View):

    def get(self, request):
        accaunt_form = CustomUserChangeForm(instance=request.user)
        return render(request, 'shop/accaunt_edit.html', context={'accaunt_form': accaunt_form})

    def post(self, request):
        accaunt_form = CustomUserChangeForm(request.POST, files=request.FILES, instance=request.user)
        if accaunt_form.is_valid():
            pas_first = request.POST.get("password")
            pas_second = request.POST.get("passwordReply")
            user_accaunt = CustomUser.objects.get(email=request.user)
            accaunt_form.save()
            if pas_first == pas_second and pas_first != '':
                # pass
                user_accaunt.set_password(pas_first)
                user_accaunt.save()
                user = authenticate(username=request.user, password=pas_first)
                login(request, user)
            messages.success(request, 'Профиль успешно изменён')
            return HttpResponseRedirect('accaunt_edit')
        else:
            return render(request, 'shop/accaunt_edit.html', {'accaunt_form': accaunt_form})
