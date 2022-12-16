from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.contrib.auth.views import LogoutView
from .forms import CustomUserCreationForm


class SignUp(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('login')
    template_name = 'user/signup.html'


class LogoutUser(LogoutView):
    next_page = '/'
