# from django.contrib.auth import get_user_model
# from django.test import TestCase
# from django.urls import reverse
# from orders.models import Order, OrderItem
# from product.models import Product, Offer
# from shop.models import Seller
#
#
# class HistoryTest(TestCase):
#
#     @classmethod
#     def setUpTestData(cls):
#         cls.user = get_user_model().objects.create_user(email='test@test.ru', password='12345')
#         user2 = get_user_model().objects.create_user(email='test2@test.ru', password='123452')
#         seller = Seller.objects.create(user=user2, name='test2', description='test1',
#                                        address='test', number=1234567)
#         product = Product.objects.create(name='test', description='test')
#         offer = Offer.objects.create(product=product, seller=seller, price=10.10)
#         order = Order.objects.create(first_name='test', last_name='test', email='test@test.ru',
#                                      address='test', number=7654321, city='test',
#                                      delivery='D', status='C')
#         OrderItem.objects.create(order=order, offer=offer, price=10.10)
#
#     def setUp(self) -> None:
#         self.client.login(email=self.user.email, password=self.user.password)
#
#     def test_history(self):
#         url = reverse('history')
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)
#         self.assertIn('orders/history_order.html', response.template_name)
#
#     def test_history_detail(self):
#         url = reverse('history-detail', kwargs={'pk': Order.objects.get(first_name='test').id})
#         response = self.client.get(url)
#         self.assertEqual(response.status_code, 200)
#         self.assertIn('orders/history_order_detail.html', response.template_name)
#
#     def test_order_create(self):
#         product = Product.objects.get(name='test').id
#         offer = Offer.objects.get(price=10.10).id
#         cart = self.client.session
#         cart[str(product)] = {'product': offer, 'quantity': 2, 'price': 10.50}
#         cart.save()
#         orders_before = len(Order.objects.all())
#         url = reverse('order_create')
#         data = {'first_name': 'test', 'last_name': 'test', 'email': 'test@test.ru', 'number': 654321}
#         response = self.client.post(url, data=data, follow=True)
#         orders_after = len(Order.objects.all())
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(orders_after - orders_before, 1)
#
#     def test_order_create_delivery(self):
#         order = Order.objects.all().last()
#         url = reverse('order_create_delivery', kwargs={'pk': order.pk})
#         data = {'delivery': 'A', 'city': 'test', 'address': 'test'}
#         response = self.client.post(url, data=data, follow=True)
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(order.city, 'test')
#
#     def test_order_create_payment(self):
#         order = Order.objects.all().last()
#         url = reverse('order_create_payment', kwargs={'pk': order.pk})
#         data = {'payment': 'C'}
#         response = self.client.post(url, data=data, follow=True)
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(order.payment, 'C')
