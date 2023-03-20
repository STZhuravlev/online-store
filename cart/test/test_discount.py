from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase, tag, RequestFactory
from django.conf import settings
from django.utils import timezone

from product.models import Category, Product, Offer
from promotions.models import PromoType, Promo, Promo2Product
from shop.models import Seller
from users.models import CustomUser
from cart.service import Cart


@tag('discount')
class DiscountInCartTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = CustomUser.objects.create_user(email='test@test.ru', password='12345', phone='9787470000')

        # Создается структура таблиц БД
        # --- категории товаров
        create_category()

        # --- продавцы
        create_sellers()

        # --- товары
        create_products()

        # --- предложения
        create_offers()

        # --- акции
        create_promotions()

    def setUp(self) -> None:
        session = self.client.session
        session[settings.CART_SESSION_ID] = []
        factory = RequestFactory()
        request = factory.get('/cart/cart')
        request.session = session
        self.cart = Cart(request)
        # offers = Offer.objects.all()
        # for offer in offers:
        #     self.cart.add(offer, quantity=1)

    def test_cart_create(self):
        """Проверка создания корзины."""
        self.assertIsInstance(self.cart, Cart)

    def test_discount_on_product(self):
        """Проверка расчета скидки на товар, если задана фиксированная сумма скидки."""
        offer = Offer.objects.select_related('product').get(product__name='apple')
        # активируем акцию
        promo = Promo.objects.get(name='product fix discount')
        promo.is_active = True
        promo.save()
        # добавляем 1 товар в корзину
        self.cart.add(offer, quantity=1)
        # вычисляем скидку и сумму к оплате
        discount = self.cart.total_discount()
        due = self.cart.due()
        for_due = self.cart.get_total_price() - discount
        self.assertEqual(discount, promo.fix_discount)
        self.assertEqual(due, for_due)

        # добавляем еще 2 товара в корзину
        self.cart.add(offer, quantity=2)
        # вычисляем скидку и сумму к оплате
        discount = self.cart.total_discount()
        due = self.cart.due()
        for_due = self.cart.get_total_price() - discount
        self.assertEqual(discount, promo.fix_discount * 3)
        self.assertEqual(due, for_due)

    def test_discount_on_product_2(self):
        """Проверка расчета скидки на товар, если задана скидка в процентах."""
        offer = Offer.objects.select_related('product').get(product__name='apple')
        # активируем акцию
        promo = Promo.objects.get(name='product discount')
        promo.is_active = True
        promo.save()
        # добавляем 1 товар в корзину
        self.cart.add(offer, quantity=1)
        # вычисляем скидку и сумму к оплате
        discount = self.cart.total_discount()
        promo_discount = offer.price * promo.discount / 100
        due = self.cart.due()
        for_due = self.cart.get_total_price() - discount
        self.assertEqual(discount, promo_discount)
        self.assertEqual(due, for_due)

        # добавляем еще 2 товара в корзину
        self.cart.add(offer, quantity=2)
        # вычисляем скидку и сумму к оплате
        discount = self.cart.total_discount()
        promo_discount = offer.price * promo.discount / 100
        due = self.cart.due()
        for_due = self.cart.get_total_price() - discount
        self.assertEqual(discount, promo_discount * 3)
        self.assertEqual(due, for_due)

    def test_discount_on_product_3(self):
        """Проверка расчета приоритетной скидки на товар."""
        offer = Offer.objects.select_related('product').get(product__name='apple')
        # активируем акцию
        promo_1 = Promo.objects.get(name='product discount')
        promo_1.is_active = True
        promo_1.save()
        promo_2 = Promo.objects.get(name='product fix discount')
        promo_2.is_active = True
        promo_2.save()
        # добавляем 1 товар в корзину
        self.cart.add(offer, quantity=1)
        # вычисляем скидку и сумму к оплате
        discount = self.cart.total_discount()
        promo_discount = max([
            offer.price * promo_1.discount / 100,
            promo_2.fix_discount
        ])
        due = self.cart.due()
        for_due = self.cart.get_total_price() - discount
        self.assertEqual(discount, promo_discount)
        self.assertEqual(due, for_due)

    def test_discount_on_plus_one(self):
        """Проверка расчета скидки на акцию 1+1."""
        offer = Offer.objects.select_related('product').get(product__name='melon')
        # активируем акцию
        promo = Promo.objects.get(name='promo 1+1')
        promo.is_active = True
        promo.save()
        for i in range(1, 5):
            with self.subTest(i=i):
                # добавляем 1 товар в корзину
                self.cart.add(offer, quantity=1)
                # вычисляем скидку и сумму к оплате
                discount = self.cart.total_discount()
                due = self.cart.due()
                promo_discount = (self.cart.cart[str(offer.id)]["quantity"] // (promo.quantity + 1)) * \
                    offer.price
                for_due = self.cart.get_total_price() - discount
            self.assertEqual(discount, promo_discount)
            self.assertEqual(due, for_due)

    def test_discount_on_plus_one_2(self):
        """Проверка расчета скидки на акцию 2+1."""
        offer = Offer.objects.select_related('product').get(product__name='melon')
        # активируем акцию
        promo = Promo.objects.get(name='promo 2+1')
        # добавляем 1 товар в корзину
        self.cart.add(offer, quantity=1)
        promo.is_active = True
        promo.save()
        for i in range(1, 6):
            with self.subTest(i=i):
                # добавляем 1 товар в корзину
                self.cart.add(offer, quantity=1)
                # вычисляем скидку и сумму к оплате
                discount = self.cart.total_discount()
                due = self.cart.due()
                promo_discount = (self.cart.cart[str(offer.id)]["quantity"] // (promo.quantity + 1)) * \
                    offer.price
                for_due = self.cart.get_total_price() - discount
            self.assertEqual(discount, promo_discount)
            self.assertEqual(due, for_due)


def create_category():
    """Создаются категории"""
    Category.objects.create(name='fruits', active=True)


def create_sellers():
    """Создает продавца"""
    user_1 = get_user_model().objects.create_user(password='test1234',
                                                  email='test1@test.ru',
                                                  phone="9787470001")
    Seller.objects.create(user=user_1, name='Shop1', description='test1',
                          address='test', number=1234567890)
    # user_2 = get_user_model().objects.create_user(password='test1234tests',
    #                                               email='test1@mail.ru',
    #                                               phone="9787470002")


def create_products():
    """Создает товары."""
    category_1 = Category.objects.get(name="fruits")

    products = [Product(name='banana',
                        description='description',
                        category=category_1),
                Product(name='apple',
                        description='description',
                        category=category_1),
                Product(name='orange',
                        description='description',
                        category=category_1),
                Product(name='pear',
                        description='description',
                        category=category_1),
                Product(name='melon',
                        description='description',
                        category=category_1),
                ]

    Product.objects.bulk_create(products)


def create_offers():
    """Создает предложения."""
    seller = Seller.objects.first()

    apple = Product.objects.get(name='apple')
    pear = Product.objects.get(name='pear')
    banana = Product.objects.get(name='banana')
    melon = Product.objects.get(name='melon')
    orange = Product.objects.get(name='orange')

    offers = [Offer(product=apple,
                    seller=seller,
                    price=50),
              Offer(product=pear,
                    seller=seller,
                    price=100),
              Offer(product=banana,
                    seller=seller,
                    price=120),
              Offer(product=melon,
                    seller=seller,
                    price=300),
              Offer(product=orange,
                    seller=seller,
                    price=80),
              ]

    Offer.objects.bulk_create(offers)


def create_promotions():
    """Создает акции."""
    promo_type_1 = PromoType.objects.create(name='promo type 1', code=1)
    # promo_type_2 = PromoType.objects.create(name='promo type 2', code=2)
    promo_type_3 = PromoType.objects.create(name='promo type 3', code=3)
    promo_type_4 = PromoType.objects.create(name='promo type 4', code=4)
    promo_type_5 = PromoType.objects.create(name='promo type 5', code=5)

    # акция на товар категорию товара code=10
    promo = Promo.objects.create(name='product discount',
                                 promo_type=promo_type_1,
                                 description='description',
                                 finished=timezone.now(),
                                 is_active=False,
                                 discount=5)

    promo2product = Promo2Product.objects.create(promo=promo)
    products = Product.objects.filter(name='apple')
    for product in products:
        promo2product.product.add(product)

    # акция на товар категорию товара code=10
    promo = Promo.objects.create(name='product fix discount',
                                 promo_type=promo_type_1,
                                 description='description',
                                 finished=timezone.now(),
                                 is_active=False,
                                 fix_discount=10)

    promo2product = Promo2Product.objects.create(promo=promo)
    products = Product.objects.filter(name='apple')
    for product in products:
        promo2product.product.add(product)

    # акция N+1 code=3
    promo = Promo.objects.create(name='promo 1+1',
                                 promo_type=promo_type_3,
                                 description='description',
                                 finished=timezone.now(),
                                 is_active=False,
                                 quantity=1)

    promo2product = Promo2Product.objects.create(promo=promo)
    products = Product.objects.filter(name='melon')
    for product in products:
        promo2product.product.add(product)

    # акция N+1 code=3
    promo = Promo.objects.create(name='promo 2+1',
                                 promo_type=promo_type_3,
                                 description='description',
                                 finished=timezone.now(),
                                 is_active=False,
                                 quantity=2)

    promo2product = Promo2Product.objects.create(promo=promo)
    products = Product.objects.filter(name='melon')
    for product in products:
        promo2product.product.add(product)

    # акция на N единиц товара code=4
    promo = Promo.objects.create(name='amount discount',
                                 promo_type=promo_type_4,
                                 description='description',
                                 finished=timezone.now(),
                                 is_active=False,
                                 discount=10,
                                 quantity=10)

    # акция на N единиц товара code=4
    promo = Promo.objects.create(name='amount fix discount',
                                 promo_type=promo_type_4,
                                 description='description',
                                 finished=timezone.now(),
                                 is_active=False,
                                 fix_discount=100,
                                 quantity=10)

    # акция на всю корзину code=5
    promo = Promo.objects.create(name='cart',
                                 promo_type=promo_type_5,
                                 description='description',
                                 finished=timezone.now(),
                                 is_active=False,
                                 discount=10,
                                 quantity=5,
                                 amount=Decimal(1000))
