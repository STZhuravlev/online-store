from django.urls import path, include
from .views import comparce, add, remove_comparison, delete_comparison

app_name = 'comparison'

urlpatterns = [
    path('comparison/', include([
        path('disp', comparce, name='comparison'),
        path('<id>/add/', add, name='comparison-add'),
        path('<id>/remove', remove_comparison, name='comparison-remove'),
        path('delete/', delete_comparison, name='comparison-delete')

    ])),
]
