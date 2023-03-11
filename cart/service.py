from django.conf import settings
from product.models import Offer
from decimal import Decimal


class Cart:

    def __init__(self, request):
        """
        Инициализация корзины
        """
        self.session = request.session
        cart = self.session.get(settings.CART_SESSION_ID)
        if not cart:
            cart = self.session[settings.CART_SESSION_ID] = {}
        self.cart = cart

    def add(self, offer, quantity=1, update_quantity=False):
        """
        Добавить товар в корзину или обновить его кол-во
        """
        offer_id = str(offer.id)
        if offer_id not in self.cart:
            self.cart[offer_id] = {'quantity': 0,
                                   'price': str(offer.price)}
        if update_quantity:
            self.cart[offer_id]['quantity'] = quantity
        else:
            self.cart[offer_id]['quantity'] += quantity
        self.save()

    def save(self):
        self.session[settings.CART_SESSION_ID] = self.cart
        self.session.modified = True

    def remove(self, offer):
        """
        Удаление товара из корзины.
        """
        offer_id = str(offer.id)
        if offer_id in self.cart:
            del self.cart[offer_id]
            self.save()

    def __iter__(self):
        """
        Перебор элементов в корзине и получение продуктов из базы данных.
        """
        offer_ids = self.cart.keys()
        offers = Offer.objects.filter(id__in=offer_ids)
        for offer in offers:
            self.cart[str(offer.id)]['product'] = offer

        for item in self.cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item

    def __len__(self):
        """
        Подсчет всех товаров в корзине.
        """
        return sum(item['quantity'] for item in self.cart.values())

    def get_total_price(self):
        """
        Подсчет стоимости товаров в корзине.
        """
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())

    def clear(self):
        """
        Удаление корзины из сессии
        """
        del self.session[settings.CART_SESSION_ID]
        self.session.modified = True

    def get_total_quantity(self):
        return sum(item['quantity'] for item in self.cart.values())

    def add_quantity(self, offer):
        offer_id = str(offer.id)
        quantity = 1
        self.cart[offer_id]['quantity'] += quantity
        self.save()

    def remove_quantity(self, offer):
        offer_id = str(offer.id)
        quantity = 1
        self.cart[offer_id]['quantity'] -= quantity
        if self.cart[offer_id]['quantity'] == 0:
            del self.cart[offer_id]
        self.save()
