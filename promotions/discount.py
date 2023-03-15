from typing import List
from decimal import Decimal
from django.db.models import Q, QuerySet
from django.shortcuts import get_object_or_404

# from cart.service import Cart
from product.models import Offer
from promotions.models import Promo
from promotions.discount_handlers import DISCOUNT_HANDLERS


def promos_for_product(product_id: int) -> QuerySet:
    """
    Возвращает список акций, в которых участвует товар.
    :param product_id: id товара
    :return:
    """
    promo_list = Promo.objects.filter(is_active=True).\
        filter(Q(promo2products__product=product_id) | Q(promo_type__code=5))

    return promo_list


def is_full_cart_discount(qty: int, total_price: Decimal, promo: Promo) -> bool:
    """
    Проверяет, может ли быть применена к товарам в корзине,
    скидка на всю корзину.
    :param qty: Количество наименований товаров в корзине.
    :param total_price: Общая стоимость корзины.
    :param promo: Информация об акции.
    :return:
    """
    if promo.amount == 0 and promo.quantity == 0:
        return False

    # необходимо купить N наименований товара на заданную сумму
    if promo.amount != 0 and promo.quantity != 0:
        if qty >= promo.quantity and total_price >= promo.amount:
            return True
    # необходимо купить товаров на заданную сумму
    elif promo.amount != 0:
        if total_price >= promo.amount:
            return True
    # необходимо купить N наименований товара не зависимо от суммы
    elif promo.quantity != 0:
        if qty >= promo.quantity:
            return True

    return False

# def get_discounts(cart: Cart, offer_id: str) -> List[Decimal]:
#     """
#     Возвращает список скидок на товар, для всех акций в которых
#     он участвует.
#     :param cart: Корзина.
#     :param offer_id: id товара (предложения).
#     :return: Список скидок.
#     """
#     result = []
#     # Получаем продукт и его id
#     offer = get_object_or_404(Offer, id=int(offer_id))
#     product_id = offer.product.id
#
#     # Получаем список акций для этого продукта
#     promo_list = promos_for_product(product_id)
#     print(f"Список акций для товара {product_id}:", promo_list)
#
#     # для каждой акции вычисляем скидку
#     for promo in promo_list:
#         # Определяем тип акции и применяем соответствующий обработчик
#         # для вычисления скидки
#         promo_code = promo.promo_type.code
#
#         # Вычисление скидки для всех акций
#         discount = Decimal(0)
#         if promo_code in DISCOUNT_HANDLERS:
#             handler = DISCOUNT_HANDLERS[promo_code]
#             if promo_code in (1, 3, 4):
#                 discount = handler(cart.cart[offer_id], promo)
#             elif promo_code in (2, 5):
#                 discount = Decimal(0)
#         result.append(discount)
#
#         price = float(cart.cart[offer_id]['price'])
#         print(f"Акция: {promo}, товар {offer}, цена {price}, скидка {discount}")
#
#     return result


# def get_best_discount(cart: Cart, offer_id: str) -> Decimal:
#     """
#     Вычислить приоритетную скидку.
#     :param cart: Корзина.
#     :param offer_id: id товара (предложения).
#     :return: Приоритетная скидка.
#     """
#     all_discounts = get_discounts(cart, offer_id)
#
#     if all_discounts:
#         return max(all_discounts)
#
#     return Decimal(0)


# def get_discount_for_all_products(cart: Cart) -> Decimal:
#     """Вычислить скидку на все товары в корзине."""
#     print(cart.cart)
#     total_discount = Decimal(0)
#     for product in cart.cart:
#         total_discount += get_best_discount(cart, product)
#
#     return total_discount



"""
class Customer(NamedTuple):
    name: str
    fidelity: int
    
class LineItem(NamedTuple):
    product: str
    quantity: int
    price: Decimal
    
    def total(self) -> Decimal:
        return self.price * self.quantity
        
class Order(NamedTuple): # контекст
    customer: Customer
    cart: Sequence[LineItem]
    promotion: Optional['Promotion'] = None
    
    def total(self) -> Decimal:
        totals = (item.total() for item in self.cart)
        return sum(totals, start=Decimal(0))
        
    def due(self) -> Decimal:
        if self.promotion is None:
            discount = Decimal(0)
        else:
            discount = self.promotion.discount(self)
        return self.total() - discount
        
    def __repr__(self):
        return f'<Order total: {self.total():.2f} due: {self.due():.2f}>'
"""