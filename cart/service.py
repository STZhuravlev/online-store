from typing import List
from django.conf import settings
from django.shortcuts import get_object_or_404

from product.models import Offer
from decimal import Decimal
from promotions.discount_handlers import DISCOUNT_HANDLERS
from promotions.discount import promos_for_product, is_full_cart_discount


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

    def due(self):
        """
        Вычисляет сумму корзины с учетом скидки.
        """
        total_discount = Decimal(0)
        for product in self.cart:
            total_discount += self._get_best_discount(product)

        # return self.get_total_price() - total_discount
        return total_discount

    def total(self):
        return self.get_total_price() - self.due()

    def _get_best_discount(self, offer_id: str) -> Decimal:
        """
            Вычисляет приоритетную скидку.
            :param offer_id: id товара (предложения).
            :return: Приоритетная скидка.
        """
        all_discounts = self._get_discounts(offer_id)

        if all_discounts:
            return max(all_discounts)

        return Decimal(0)

    def _get_discounts(self, offer_id: str) -> List[Decimal]:
        """
            Возвращает список скидок на товар, для всех акций в которых
            он участвует.
            :param offer_id: id товара (предложения).
            :return: Список скидок.
        """
        result = []
        # Получаем продукт и его id
        offer = get_object_or_404(Offer, id=int(offer_id))
        product_id = offer.product.id

        # Получаем список акций для этого продукта
        promo_list = promos_for_product(product_id)
        # print(f"Список акций для товара {product_id}:", promo_list)

        # для каждой акции вычисляем скидку
        for promo in promo_list:
            # Определяем тип акции и применяем соответствующий обработчик
            # для вычисления скидки
            promo_code = promo.promo_type.code

            # Вычисление скидки для всех акций
            discount = Decimal(0)
            if promo_code in DISCOUNT_HANDLERS:
                handler = DISCOUNT_HANDLERS[promo_code]
                if promo_code == 5:
                    qty = len(self.cart)
                    total_price = self.get_total_price()
                    if is_full_cart_discount(qty=qty, total_price=total_price, promo=promo):
                        discount = handler(self.cart[offer_id], promo)
                elif promo_code in (1, 3, 4):
                    discount = handler(self.cart[offer_id], promo)
            result.append(discount)

            # price = float(self.cart[offer_id]['price'])
            # print(f"Акция: {promo}, товар {offer}, цена {price}, скидка {discount}")

        return result
