from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from promotions.models import PromoType, Promo, Promo2Product
from product.models import Product, Category
from shop.models import Seller
from promotions.views import PROMO_PER_PAGE


class PromoListViewTest(TestCase):
    """ Тесты отображения списка акций. """

    @classmethod
    def setUpTestData(cls):
        cls.url = f'/promos/promo/'
        cls.url_name = reverse('promotions:promo-list')
        # создаём акции: 6 активных, 1 неактивная
        promo_type_1 = PromoType.objects.create(name='promo type 1', code=10)
        promo_type_2 = PromoType.objects.create(name='promo type 2', code=20)
        for i in range(3):
            Promo.objects.create(name=f'promo {i + 1}',
                                 promo_type=promo_type_1,
                                 description='description',
                                 finished=timezone.now(),
                                 is_active=True)
        for i in range(3):
            Promo.objects.create(name=f'promo {i + 1}',
                                 promo_type=promo_type_2,
                                 description='description',
                                 finished=timezone.now(),
                                 is_active=True)
        # неактивная акция
        Promo.objects.create(name=f'promo non-active',
                             promo_type=promo_type_2,
                             description='description',
                             finished=timezone.now(),
                             is_active=False)
        # товары
        # user = get_user_model().objects.create_user(password='test1234',
        #                                             email='test1@test.ru')
        # seller = Seller.objects.create(user=user, name='test1', description='test1',
        #                                address='test', number=1234567890)
        category = Category.objects.create(name='test', active=True)
        # Product.objects.create(name='product 1', seller=seller, description='product description',
        #                        category=category)
        # Product.objects.create(name='product 2', seller=seller, description='product description',
        #                        category=category)

    def test_url_exists_at_correct_location(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_url_available_by_name(self):
        response = self.client.get(self.url_name)
        self.assertEqual(response.status_code, 200)

    def test_template_name_correct(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'promotions/promo-list.html')

    def test_template_takes_content(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['categories'])
        self.assertTrue(response.context['promotions'])

    def test_pagination_first_page(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertEqual(response.context['is_paginated'], True)
        self.assertEqual(len(response.context['promotions']), PROMO_PER_PAGE)

    def test_pagination_second_page(self):
        response = self.client.get(self.url + '?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertEqual(response.context['is_paginated'], True)
        self.assertEqual(len(response.context['promotions']), 2)
