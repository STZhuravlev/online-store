from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey
from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator


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

    def __str__(self):
        return self.name


class ProductProperty(models.Model):
    """Значение свойства продукта"""
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    property = models.ForeignKey(Property, on_delete=models.PROTECT, related_name='prod')
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

    name = models.CharField(max_length=100, verbose_name=_("категория"))
    icon = models.FileField(upload_to="images/icons/", verbose_name=_("иконка"), blank=True)
    active = models.BooleanField(choices=STATUS_CHOICE, default=False, verbose_name=_("активность"))
    parent = TreeForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name="children")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("категория")
        verbose_name_plural = _("категории")

    def save(self, *args, **kwargs):
        if not self.parent:
            pass
        elif self.parent.level >= 2:
            raise ValueError('Достигнута максимальная вложенность!')
        super(Category, self).save(*args, **kwargs)


class Offer(models.Model):
    """Товар"""
    product = models.ForeignKey("Product", on_delete=models.PROTECT, related_name='offers')
    seller = models.ForeignKey("shop.Seller", on_delete=models.PROTECT, related_name='sellers')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('цена'))
    added_at = models.DateTimeField(auto_created=True, auto_now=True, verbose_name=_('время добавления'))

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


class HistoryView(models.Model):
    """История просмотра товаров"""
    # user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    view_at = models.DateTimeField(auto_now=True, verbose_name=_('время просмотра'))
    product = models.ForeignKey(Product, verbose_name=_('товар'), on_delete=models.CASCADE, related_name='views')

    class Meta:
        ordering = ('-view_at',)
        verbose_name = _("история просмотров")
        verbose_name_plural = _("истории просмотров")

    def __str__(self):
        return self.product.name


class Feedback(models.Model):
    """Отзыв"""

    grate_list = [
        (1, '1 🌟'),
        (2, '2 🌟'),
        (3, '3 🌟'),
        (4, '4 🌟'),
        (5, '5 🌟'),
    ]

    product = models.ForeignKey(Product, verbose_name=_('продукт'), on_delete=models.PROTECT)
    author = models.ForeignKey(get_user_model(), verbose_name=_('автор'), on_delete=models.PROTECT)
    publication_date = models.DateTimeField(auto_now=True)
    rating = models.IntegerField(validators=[MaxValueValidator(5), MinValueValidator(1)], choices=grate_list,
                                 verbose_name=_('рейтинг'))
    description = models.TextField(max_length=2048, verbose_name=_('описание'))
    image = models.ImageField(upload_to='feedback_images/', blank=True, verbose_name=_('фотография'))

    class Meta:
        verbose_name = _('отзыв')
        verbose_name_plural = _('отзывы')

    def __str__(self):
        return self.product.name
