from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from promotions.models import PromoType, Promo
from product.models import Category
from promotions.views import PROMO_PER_PAGE


class PromoListViewTest(TestCase):
    """ Тесты отображения списка акций. """

    @classmethod
    def setUpTestData(cls):
        cls.url = '/promos/promo/'
        cls.url_name = reverse('promotions:promo-list')
        # создаём акции: 6 активных, 1 неактивную
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
        Promo.objects.create(name='promo non-active',
                             promo_type=promo_type_2,
                             description='description',
                             finished=timezone.now(),
                             is_active=False)
        Category.objects.create(name='test', active=True)

    def test_url_exists_at_correct_location(self):
        """Тест на доступность страницы по url"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_url_available_by_name(self):
        """Тест на доступность страницы по name"""
        response = self.client.get(self.url_name)
        self.assertEqual(response.status_code, 200)

    def test_template_name_correct(self):
        """Тест, что страница использует заданный http-шаблон"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'promotions/promo-list.html')

    def test_template_takes_content(self):
        """Тест на передачу в шаблон контекста"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['categories'])
        self.assertTrue(response.context['promotions'])

    def test_pagination_first_page(self):
        """Тест, что пагинатор получает список акций и
        передает заданное кол-во на страницу 1"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertEqual(response.context['is_paginated'], True)
        self.assertEqual(len(response.context['promotions']), PROMO_PER_PAGE)

    def test_pagination_second_page(self):
        """Тест, что пагинатор получает список акций и
        передает оставшееся кол-во на страницу 2"""
        response = self.client.get(self.url + '?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('is_paginated' in response.context)
        self.assertEqual(response.context['is_paginated'], True)
        self.assertEqual(len(response.context['promotions']), 2)
