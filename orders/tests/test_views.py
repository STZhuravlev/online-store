from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from orders.models import Order
from product.models import Product, Offer
from shop.models import Seller


class HistoryTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = get_user_model().objects.create_user(email='test@test.ru', password='12345')
        user2 = get_user_model().objects.create_user(email='test2@test.ru', password='123452')
        seller = Seller.objects.create(user=user2, name='test2', description='test1',
                                       address='test', number=1234567)
        product = Product.objects.create(name='test', description='test')
        Offer.objects.create(product=product, seller=seller, price=10.10)
        Order.objects.create(first_name='test', last_name='test', email='test@test.ru',
                             address='test', postal_code='test', city='test',
                             delivery='D', status='C')

    def setUp(self) -> None:
        self.client.login(email=self.user.email, password=self.user.password)

    def test_history(self):
        url = reverse('history')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('orders/history_order.html', response.template_name)

    def test_history_detail(self):
        url = reverse('history-detail', kwargs={'pk': Order.objects.get(first_name='test').id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('orders/history_order_detail.html', response.template_name)

    # def test_order_create(self):
    #     url = reverse('order_create')
    #     cart = [{'offer': 1, 'price': 10.50, 'quantity': 2}, ]
    #     data={'first_name': 'test', 'last_name': 'test', 'email': 'test@test.ru',
    #             'address': 'test', 'postal_code': 'test', 'city': 'test', 'delivery': 'D', 'payment': 'C'}
    #     response = self.client.post(url, data=data, follow=True)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn('orders/new-order.html', response.template_name)
