from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey


class Product(models.Model):
    """Продукт"""
    name = models.CharField(max_length=512, verbose_name=_("наименование"))
    property = models.ManyToManyField("Property", through="ProductProperty", verbose_name=_("характеристики"))

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """ Возвращает урл на продукт """
        return reverse('product-detail', args=[str(self.id)])


class Property(models.Model):
    """Свойство продукта"""
    name = models.CharField(max_length=512, verbose_name=_("наименование"))


class ProductProperty(models.Model):
    """Значение свойства продукта"""
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    property = models.ForeignKey(Property, on_delete=models.PROTECT)
    value = models.CharField(max_length=128, verbose_name=_("значение"))


class Banner(models.Model):
    """ Баннеры. """
    title = models.CharField(max_length=128, verbose_name=_('заголовок'))
    brief = models.CharField(max_length=512, verbose_name=_('краткое описание'))
    icon = models.ImageField(upload_to='files/', verbose_name=_('изображение'))
    added_at = models.DateTimeField(auto_created=True, auto_now=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='banners')
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        """ Возвращает урл на продукт """
        return self.product.get_absolute_url()


class Category(MPTTModel):
    """Категория продукта"""
    STATUS_CHOICE = [
        (True, _("Активна")),
        (False, _("Не активна")),
    ]

    category = models.CharField(max_length=100, verbose_name=_("категория"))
    icon = models.ImageField(upload_to="files/icons", verbose_name=_("иконка"), blank=True)
    active = models.BooleanField(choices=STATUS_CHOICE, default=False, verbose_name=_("активность"))
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name="children")

    def __str__(self):
        return self.category

    class Meta:
        verbose_name = _("категория")
        verbose_name_plural = _("категории")


class Price(models.Model):
    """Цена"""
    price = models.IntegerField(verbose_name=_('цена'))
    discount_price = models.IntegerField(default=None, verbose_name=_('цена со скидкой'))


class Goods(models.Model):
    """Товар"""
    name = models.CharField(max_length=512, verbose_name=_("наименование"))
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    image = models.ImageField(upload_to='images/goods_pictures', verbose_name=_('изображение'))
    description = models.TextField(max_length=2048, verbose_name=_('описание'))
    price = models.ForeignKey(Price, verbose_name=_('цена'), on_delete=models.PROTECT)
