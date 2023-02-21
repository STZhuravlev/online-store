from django import forms


class SiteSettingsForm(forms.Form):
    name = forms.CharField(max_length=50, label='Название настройки')
    value = forms.IntegerField(label='Значение')