# Модуль для описания обработчиков для вычисления скидок для всех типов акций
from decimal import Decimal
from promotions.models import Promo
from product.models import Offer
# from cart.service import Cart


def discount_on_product(product_info: dict, promo: Promo) -> Decimal:
    """
    Возвращает скидку на товар или категорию товаров.
    :param product_info: Информация о цене и кол-ве единиц товара в корзине.
    :param promo: Информация об акции.
    :return: Величина скидки на товар по данной акции.
    """
    price = Decimal(product_info['price'])
    if promo.discount != 0:
        return price * product_info['quantity'] * promo.discount / 100
    elif promo.fix_discount != 0:
        return promo.fix_discount * product_info['quantity']

    return Decimal(0)


def is_discount_on_set(product: Offer, promo: Promo) -> bool:
    """
    Проверяет, может ли быть применена акция "На комплект"
    :param cart:
    :param promo:
    :return:
    """
    # Список товаров в акции
    # product_list = promo.promo2products.product().select_related('category')
    # if product in product_list:
    return False


def discount_on_sets(product_info: dict, promo: Promo) -> Decimal:
    """
    Возвращает скидку на набор товаров в корзине.
    :param product_info: Информация о цене и кол-ве единиц товара в корзине.
    :param promo: Информация об акции.
    :return: Величина скидки на товар по данной акции.
    """
    return Decimal(0)


def free_product_discount(product_info: dict, promo: Promo) -> Decimal:
    """
    Возвращает скидку для акции N+1 - 1 товар бесплатно.
    :param product_info: Информация о цене и кол-ве единиц товара в корзине.
    :param promo: Информация об акции.
    :return: Величина скидки на товар по данной акции.
    """
    qty = product_info['quantity']
    if promo.quantity == 0 or qty <= promo.quantity:
        return Decimal(0)

    return (qty // (promo.quantity + 1)) * Decimal(product_info['price'])


def discount_on_amount(product_info: dict, promo: Promo) -> Decimal:
    """
    Возвращает скидку при покупке N единиц товара.
    :param product_info: Информация о цене и кол-ве единиц товара в корзине.
    :param promo: Информация об акции.
    :return: Величина скидки на товар по данной акции.
    """
    qty = product_info['quantity']

    price = Decimal(product_info['price'])
    if promo.discount != 0 and qty >= promo.quantity:
        return price * qty * promo.discount / 100
    elif promo.fix_discount != 0 and qty >= promo.quantity:
        return promo.fix_discount

    return Decimal(0)


def discount_on_cart(product_info: dict, promo: Promo) -> Decimal:
    """
    Возвращает скидку на товар по типу акции "На всю корзину".
    :param product_info: Информация о цене и кол-ве единиц товара в корзине.
    :param promo: Информация об акции.
    :return: Величина скидки на товар по данной акции.
    """
    price = Decimal(product_info['price'])
    if promo.discount != 0:
        return price * product_info['quantity'] * promo.discount / 100

    return Decimal(0)


calculator_1 = discount_on_product
calculator_2 = discount_on_sets
calculator_3 = free_product_discount
calculator_4 = discount_on_amount
calculator_5 = discount_on_cart

DISCOUNT_HANDLERS = {
    1: calculator_1,
    2: calculator_2,
    3: calculator_3,
    4: calculator_4,
    5: calculator_5,
}
