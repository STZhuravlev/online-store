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
)

from django.urls import reverse
from shop.models import Seller
# from django.contrib.auth.models import User
# from pathlib import Path, PurePath

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

#     def test_exist_entry_list(self):
#         response = self.client.get('/entres/')
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'app_media/entry_list.html')
#
#     def test_entry_count(self):
#         response = self.client.get('/entres/')
#         self.assertEqual(response.status_code,
#         200)
#         self.assertTrue(len(response.context['entres']) == NUMBER_OF_ITEMS)
#
#     def test_one_entry(self):
#         response = self.client.get('/entry_detail1/')
#         self.assertEqual(response.status_code, 200)
#         self.assertTemplateUsed(response, 'app_media/entry_detail.html')
#         self.assertEqual(response.context['object'].name, 'Запись 0')
#
# class UploadTest(TestCase):
#     def setUp(self) -> None:
#         user = User.objects.create_user(
#             username='test123', email='passwordTest123@bk.ru', password='passwordTest123'
#         )
#         response = self.client.post('/login/', {'username': 'test123', 'password': 'passwordTest123'}, follow=True)
#
#     def test_upload_entry(self):
#         cwd = Path.cwd()
#         image_jpg = open(PurePath.joinpath(cwd, 'app_media', 'tests', 'tests_file', 'image.jpg'), "rb")
#         image = SimpleUploadedFile(image_jpg.name, image_jpg.read())
#         response = self.client.post(
#             '/upload_entry/', {'name': 'Запись', 'description': 'Описание', 'images': image}, follow=True
#         )
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(EntryImage.objects.all().count(), 1)

    def test_two(self):
        url = reverse('offer-detail', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('product/offer-detail.html', response.template_name)
        self.assertContains(response, 'test')

    # def test_three(self):
    #     url = reverse('product-detail', kwargs={'pk': 1})
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn('product/product-detail.html', response.template_name)
    #     self.assertContains(response, 'Product Detail')


class CategoryViewsTest(TestCase):
    def test_category_page(self):
        url = reverse('category')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'product/category-view.html')
