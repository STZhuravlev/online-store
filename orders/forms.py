from django import forms
from .models import Order, DELIVERY_CHOICES, TYPE_CHOICES


class OrderUserCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'number']


class OrderDeliveryCreateForm(forms.Form):
    delivery = forms.ChoiceField(choices=DELIVERY_CHOICES)
    city = forms.CharField(max_length=100)
    address = forms.CharField(max_length=250)


class OrderPaymentCreateForm(forms.Form):
    payment = forms.ChoiceField(choices=TYPE_CHOICES)
