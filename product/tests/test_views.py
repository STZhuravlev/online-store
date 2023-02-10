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
    Feedback,
)

from product.forms import FeedbackForm

from django.urls import reverse
from shop.models import Seller

NUMBER_OF_ITEMS = 10


class SettingsTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        user = get_user_model().objects.create_user(password='test1234', email='test1@test.ru')
        seller = Seller.objects.create(user=user, name='test1', description='test1',
                                       address='test', number=1234567)
        category = Category.objects.create(name='test')
        product = Product.objects.create(name='Утюг', description='классный утюг', category=category)
        Offer.objects.create(product=product, seller=seller, price=10.10)
        Feedback.objects.create(product=product, author=user, description='MyFeedbackTest', rating=3)


# class EntryTest(SettingsTest):
    # @classmethod
    # def setUpTestData(cls):
    #     user = get_user_model().objects.create_user(password='test1234', email='test1@test.ru')
    #     seller = Seller.objects.create(user=user, name='test1', description='test1',
    #                                    address='test', number=1234567)
    #     category = Category.objects.create(name='test')
    #     product = Product.objects.create(name='test', description='test', category=category)
    #     Offer.objects.create(product=product, seller=seller, price=10.10)

    # def test_one(self):
    #     url = reverse('banners')
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn('product/banners-view.html', response.template_name)

    # def test_two(self):
    #     url = reverse('offer-detail', kwargs={'pk': Offer.objects.get(price=10.10).id})
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn('product/offer-detail.html', response.template_name)
    #     self.assertContains(response, 'test')
    #
    # def test_three(self):
    #     url = reverse('product-detail', kwargs={'pk': Product.objects.get(name='Утюг').id})
    #     response = self.client.get(url)
    #     self.assertEqual(response.status_code, 200)
    #     self.assertIn('product/product-detail.html', response.template_name)
    #     # self.assertContains(response, 'Product Detail')


class CategoryViewsTest(TestCase):
    def test_category_page(self):
        url = reverse('category')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'product/category-view.html')


class FeedbackViewTest(SettingsTest):

    """Тестирование добавления отзыва к товару"""

    def setUp(self):
        self.product = Product.objects.get(pk=1)
        self.user = get_user_model().objects.first()
        self.url = reverse('offer-detail', args=(self.product.id,))

        self.feedback_image = '_aCwkDco.jpg'

        # self.feedback_image = SimpleUploadedFile(
        #     name='image_1.jpg', content=open(
        #         os.path.abspath(os.path.join("media/feedback_images/HakkaBlue3-primary-300Wx300H_aCwkDco.jpg")), 'rb'
        #     ).read(), content_type='image/jpeg'
        # )

    def test_offer_detail_page(self):

        """Проверка существования детальной страницы товара"""

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        print(f'[TEST][INFO] - get status_code {response.status_code}')

    def test_add_feedback(self):

        """Добавления отзыва к товару """

        self.client.login(email='test1@test.ru', password='test1234')

        data = {
            'product_id': self.product.id,
            'author_id': self.user.id,
            'description': 'test_description',
            'image': self.feedback_image,
            'rating': 5,
        }

        form = FeedbackForm(data)
        self.assertTrue(form.is_valid())
        print(f'[TEST][INFO] - form status {form.is_valid()}')

        response_post = self.client.post(self.url, data=data, follow=True)
        self.assertEqual(response_post.status_code, 200)

        feedback_count = Feedback.objects.count()
        self.assertEqual(feedback_count, 2)
        print(f'[TEST][INFO] - count feedback {feedback_count}')
