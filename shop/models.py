from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from users.models import CustomUser
from .singleton_model import SingletonModel


class Seller(models.Model):
    """Продавец"""
    user = models.OneToOneField(CustomUser, verbose_name=_('пользователь'), on_delete=models.CASCADE)
    name = models.CharField(max_length=128, verbose_name=_('имя продавца'))
    description = models.CharField(max_length=1024, verbose_name=_('описание'))
    address = models.CharField(max_length=128, verbose_name=_('адрес'))
    number = models.IntegerField(validators=[MinValueValidator(100000), MaxValueValidator(89999999999)],
                                 verbose_name=_('номер телефона'))

    class Meta:
        verbose_name = _('продавец')
        verbose_name_plural = _('продавцы')

    def __str__(self):
        return self.name


class SellerLogo(models.Model):
    """Логотип продавца"""
    seller = models.OneToOneField(Seller, verbose_name=_('продавец'),
                                  on_delete=models.CASCADE, related_name='logo')
    image = models.ImageField(upload_to='static/img/')

    class Meta:
        verbose_name = 'логотип продавца'
        verbose_name_plural = 'логотипы продавцов'

    def __str__(self):
        return self.seller.name

class AdminSettings(SingletonModel):
    tite_to_cahce = models.PositiveIntegerField(verbose_name='Время кэширования в днях', default=1)
    promo_per_page = models.PositiveIntegerField(verbose_name='Количество акция, отображаемых на странице', default=4)
    promo_products_per_page = models.PositiveIntegerField(verbose_name='Количество продуктов в акции, отображаемых на странице', default=4)

    def __str__(self):
        return 'Настройки'

    class Meta:
        verbose_name = 'Конфигурация'
        verbose_name_plural = 'Конфигурация'
