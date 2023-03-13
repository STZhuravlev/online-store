# Модуль для описания обработчиков для вычисления скидок для всех типов акций
from decimal import Decimal
from promotions.models import Promo
from product.models import Offer
from cart.service import Cart


def discount_on_product(product_info: dict, promo: Promo) -> Decimal:
    """
    Возвращает скидку на товар или категорию товаров.
    :param product_info: Информация о цене и кол-ве единиц товара в корзине.
    :param promo: Информация об акции.
    :return: Величина скидки на товар по данной акции.
    """
    price = Decimal(product_info['price'])
    if promo.discount != 0:
        return price * promo.discount / 100
    elif promo.fix_discount != 0:
        return promo.fix_discount

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
    if promo.quantity == 0 or qty <= promo.quantity:
        return Decimal(0)

    price = Decimal(product_info['price'])
    if promo.discount != 0:
        return price * qty * promo.discount / 100
    elif promo.fix_discount != 0:
        return promo.fix_discount


def is_full_cart_discount(cart: Cart, promo: Promo) -> bool:
    """
    Проверяет, может ли быть применена к товарам в корзине,
    скидка на всю корзину.
    :param cart: Корзина со списком товаров в ней.
    :param promo: Информация об акции.
    :return:
    """
    if promo.amount == 0 and promo.quantity == 0:
        return False

    # общая сумма товаров в корзине
    total_price = sum(
        [product['quantity'] * Decimal(product['price'])
         for product in cart.cart]
    )
    # необходимо купить N наименований товара на заданную сумму
    if promo.amount != 0 and promo.quantity != 0:
        if len(cart.cart) >= promo.quantity and total_price >= promo.amount:
            return True
    # необходимо купить товаров на заданную сумму
    elif promo.amount != 0:
        if total_price >= promo.amount:
            return True
    # необходимо купить N наименований товара не зависимо от суммы
    elif promo.quantity != 0:
        if len(cart.cart) >= promo.quantity:
            return True

    return False


def discount_on_cart(product_info: dict, promo: Promo) -> Decimal:
    """
    Возвращает скидку на товар по типу акции "На всю корзину".
    :param product_info: Информация о цене и кол-ве единиц товара в корзине.
    :param promo: Информация об акции.
    :return: Величина скидки на товар по данной акции.
    """
    price = Decimal(product_info['price'])
    if promo.discount != 0:
        return price * promo.discount
    elif promo.fix_discount != 0:
        return promo.fix_discount

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
