from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from promotions.models import PromoType, Promo, Promo2Product
from product.models import Product, Category, Offer
from shop.models import Seller
from promotions.views import PROMO_PRODUCTS_PER_PAGE


class PromoDetailViewTest(TestCase):
    """ Тесты отображения детальной страницы акции. """

    @classmethod
    def setUpTestData(cls):
        # создаём акцию
        promo_type_1 = PromoType.objects.create(name='promo type 1', code=10)
        promo = Promo.objects.create(name='promo 1',
                                     promo_type=promo_type_1,
                                     description='description',
                                     finished=timezone.now(),
                                     is_active=True)
        # создаём продукты и привязываем их к акции
        user = get_user_model().objects.create_user(password='test1234',
                                                    email='test1@test.ru')
        seller = Seller.objects.create(user=user, name='test1', description='test1',
                                       address='test', number=1234567890)
        category = Category.objects.create(name='test', active=True)
        for i in range(1, 7):
            product = Product.objects.create(name=f'product {i}',
                                             description='product description',
                                             category=category)
            Offer.objects.create(product=product, seller=seller, price=1000)
        # urls
        cls.pk = promo.id
        cls.url = f'/promos/promo/{promo.id}/'
        cls.url_name = reverse('promotions:promo-detail', args=[promo.id])

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
        self.assertTemplateUsed(response, 'promotions/promo-detail.html')

    def test_template_takes_content(self):
        """Тест на передачу в шаблон контекста"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['categories'])
        self.assertTrue(response.context['promo'])
        self.assertTrue(response.context['page_obj'])

    def test_pagination_first_page(self):
        """Тест, что пагинатор получает все товары из каталога и
        передает заданное кол-во на страницу 1"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('page_obj' in response.context)
        self.assertEqual(len(response.context['page_obj']), PROMO_PRODUCTS_PER_PAGE)

    def test_pagination_second_page(self):
        """Тест, что пагинатор получает все товары из каталога и
        передает оставшееся кол-во на страницу 2"""
        response = self.client.get(self.url + '?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertTrue('page_obj' in response.context)
        self.assertEqual(len(response.context['page_obj']), 2)

    def test_correct_product_list(self):
        """Тест, что передаются только товары, связанные с акцией"""
        # привязываем к акции один товар
        product = Product.objects.first()
        promo = Promo.objects.first()
        promo2product = Promo2Product.objects.create(promo=promo)
        promo2product.product.add(product)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['page_obj']), 1)
