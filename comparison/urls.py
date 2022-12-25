from django.urls import path, include
from .views import comparce, add, remove_comparison, delete_comparison

app_name = 'comparison'

urlpatterns = [
    path('comparison/', include([
        path('disp', comparce, name='comparison'),
        path('<id>/add/', add, name='add'),
        path('<id>/remove', remove_comparison, name='remove'),
        path('delete/', delete_comparison, name='delete')

    ])),
]
