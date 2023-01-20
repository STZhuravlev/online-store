from django import forms
from django.utils.translation import gettext_lazy as _
from product.models import DeliveryType


class OrderForm(forms.Form):
    delivery = forms.ModelChoiceField(queryset=DeliveryType.objects.all())
    address = forms.CharField(max_length=150, help_text=_('адрес доставки'))
