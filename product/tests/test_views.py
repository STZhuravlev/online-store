from django.contrib.auth import get_user_model
from django.test import (
    TestCase,
    # RequestFactory,
)
# from django.core.files.uploadedfile import SimpleUploadedFile
# from django.urls import reverse
from product.models import (
    Product,
    # ProductProperty,
    # Property,
    # Banner,
    Category,
    Offer,
    Order,
    OrderStatus,
    DeliveryType,
    PaymentType
)

from django.urls import reverse
from shop.models import Seller

NUMBER_OF_ITEMS = 10


class EntryTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = get_user_model().objects.create_user(password='test1234', email='test1@test.ru')
        seller = Seller.objects.create(user=user, name='test1', description='test1',
                                       address='test', number=1234567)
        category = Category.objects.create(name='test')
        product = Product.objects.create(name='test', description='test', category=category)
        Offer.objects.create(product=product, seller=seller, price=10.10)

    def test_one(self):
        url = reverse('banners')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('product/banners-view.html', response.template_name)

    def test_two(self):
        url = reverse('offer-detail', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('product/offer-detail.html', response.template_name)
        self.assertContains(response, 'test')

    def test_three(self):
        url = reverse('product-detail', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('product/product-detail.html', response.template_name)
        self.assertContains(response, 'Product Detail')


class CategoryViewsTest(TestCase):
    def test_category_page(self):
        url = reverse('category')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'product/category-view.html')


class HistoryTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = get_user_model().objects.create_user(password='test1234', email='test1@test.ru')
        # seller = Seller.objects.create(user=user, name='test1', description='test1',
        #                                address='test', number=1234567)
        # category = Category.objects.create(name='test')
        # product = Product.objects.create(name='test', description='test', category=category)
        # Offer.objects.create(product=product, seller=seller, price=10.10)
        type = PaymentType.objects.create(name='test')
        status = OrderStatus.objects.create(name='test')
        delivery = DeliveryType.objects.create(name='test')
        Order.objects.create(user=user, delivery=delivery, type=type, status=status, address='test')

    def test_history(self):
        url = reverse('history')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('product/history_order.html', response.template_name)

    def test_history_detail(self):
        url = reverse('history-detail', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('product/history_order_detail.html', response.template_name)
