from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey


class Product(models.Model):
    """Продукт"""
    name = models.CharField(max_length=128, verbose_name=_("наименование"))
    description = models.CharField(max_length=1024, verbose_name=_("описание"))
    seller = models.ManyToManyField("shop.Seller", through="Offer", verbose_name=_("продавец"))
    property = models.ManyToManyField("Property", through="ProductProperty", verbose_name=_("характеристики"))
    category = models.ForeignKey("Category", on_delete=models.CASCADE, blank=True, null=True, related_name="cat")

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


class Offer(models.Model):
    """Товар"""
    product = models.ForeignKey("Product", on_delete=models.PROTECT)
    seller = models.ForeignKey("shop.Seller", on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('цена'))

    def __str__(self):
        return self.product.name

    class Meta:
        verbose_name = _("товар")
        verbose_name_plural = _("товары")


class ProductImage(models.Model):
    """Фотографии продукта"""
    product = models.ForeignKey(Product, verbose_name=_('продукт'), on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='images/')

    class Meta:
        verbose_name = _('изображение продукта')
        verbose_name_plural = _('изображения продуктов')

    def __str__(self):
        return self.product.name
