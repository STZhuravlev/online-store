from django.urls import path
from django.contrib.auth import views as auth_views
from .views import SignUp,  LogoutUser

urlpatterns = [
    path('register', SignUp.as_view(), name='signup'),

    path('logout', LogoutUser.as_view(), name='logout'),
    path('password_change', auth_views.PasswordChangeView.as_view()),
    path('password_change/done', auth_views.PasswordChangeDoneView.as_view()),
    path('password_reset', auth_views.PasswordResetView.as_view()),
    path('password_reset/done', auth_views.PasswordChangeDoneView.as_view()),


]
