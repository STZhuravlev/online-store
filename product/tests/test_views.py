from django.urls import reverse
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
)
from shop.models import Seller
from users.models import CustomUser
# from django.contrib.auth.models import User
# from pathlib import Path, PurePath

NUMBER_OF_ITEMS = 10


class EntryTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        user = CustomUser.objects.create(password='test1234', email='test1@test.ru')
        seller = Seller.objects.create(user=user, name='test1', description='test1',
                                       address='test', number=1234567)
        category = Category.objects.create(name='test')
        product = Product.objects.create(name='test', description='test', category=category)
        Offer.objects.create(product=product, seller=seller, price=10.10)

    def test_one(self):
        response = self.client.get(reverse('banners'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('product/banners-view.html', response.template_name)

    def test_two(self):
        response = self.client.get(reverse('offer-detail', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('product/offer-detail.html', response.template_name)
        self.assertContains(response, 'test')

    def test_three(self):
        response = self.client.get(reverse('product-detail', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('product/product-detail.html', response.template_name)
        self.assertContains(response, 'Product Detail')
