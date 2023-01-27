from django.db import models
from django.utils.translation import gettext_lazy as _

STATUS_CHOICES = (
    ('W', _('ожидание ответа от продавца')),
    ('A', _('продавец принял заказ')),
    ('M', _('упаковка на складе')),
    ('S', _('в пути')),
    ('F', _('прибыл в пункт выдачи')),
)
DELIVERY_CHOICES = (
    ('D', _('обычная доставка')),
    ('A', _('самовывоз')),
)
TYPE_CHOICES = (
    ('C', _('оплата картой')),
)


class Order(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField()
    offer1 = models.ManyToManyField("product.Offer", through="OrderItem", verbose_name=_("продукт"))
    address = models.CharField(max_length=250)
    postal_code = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    paid = models.BooleanField(default=False)
    delivery = models.CharField(max_length=1, choices=DELIVERY_CHOICES, default='D', verbose_name='тип доставки')
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='W', verbose_name='статус заказа')
    payment = models.CharField(max_length=1, choices=TYPE_CHOICES, default='C', verbose_name='тип оплаты')

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'

    def __str__(self):
        return 'Order {}'.format(self.id)

    def get_total_cost(self):
        return sum(item.get_cost() for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.PROTECT)
    offer1 = models.ForeignKey('product.Offer', related_name='order_items', on_delete=models.PROTECT)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return '{}'.format(self.id)

    def get_cost(self):
        return self.price * self.quantity
