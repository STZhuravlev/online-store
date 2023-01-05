from django.test import TestCase
from django.urls import reverse


class ViewsTest(TestCase):
    def test_category_page(self):
        url = reverse('category')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'product/category-view.html')