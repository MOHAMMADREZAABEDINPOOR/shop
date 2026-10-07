from decimal import Decimal
from django.test import TestCase
from django.urls import reverse

from .models import Category, Brand, Product, ProductSpecification
from reviews.models import Review
from accounts.models import User


class CatalogFilteringTests(TestCase):
    """Advanced filtering & sorting behavior for the shop listing."""

    def setUp(self):
        self.category = Category.objects.create(name='موبایل', slug='mobile')
        self.brand_a = Brand.objects.create(name='اپل', slug='apple')
        self.brand_b = Brand.objects.create(name='سامسونگ', slug='samsung')

        self.p1 = Product.objects.create(
            name='آیفون ۱۶', slug='iphone-16', sku='IP16',
            category=self.category, brand=self.brand_a,
            base_price=Decimal('80000000'), sale_price=Decimal('70000000'),
            stock=5, is_available=True, is_active=True,
        )
        self.p2 = Product.objects.create(
            name='گلکسی S25', slug='galaxy-s25', sku='GS25',
            category=self.category, brand=self.brand_b,
            base_price=Decimal('60000000'),
            stock=0, is_available=False, is_active=True,
        )

    def make_review(self, product, rating, email):
        user = User.objects.create_user(email=email, password='Test@12345')
        return Review.objects.create(product=product, user=user, rating=rating, comment='خوب')

    def test_multi_brand_filter(self):
        Review.objects.all().delete()
        response = self.client.get(reverse('catalog:shop'), {'brands': 'apple,samsung'})
        self.assertEqual(response.status_code, 200)
        names = {p.name for p in response.context['products']}
        self.assertEqual(names, {'آیفون ۱۶', 'گلکسی S25'})

    def test_single_brand_filter(self):
        response = self.client.get(reverse('catalog:shop'), {'brands': 'apple'})
        names = {p.name for p in response.context['products']}
        self.assertEqual(names, {'آیفون ۱۶'})

    def test_min_rating_filter(self):
        self.make_review(self.p1, 5, 'r1@example.com')
        response = self.client.get(reverse('catalog:shop'), {'min_rating': '4'})
        names = {p.name for p in response.context['products']}
        self.assertIn('آیفون ۱۶', names)
        self.assertNotIn('گلکسی S25', names)

    def test_sort_by_rating_no_crash_with_min_rating(self):
        self.make_review(self.p1, 5, 'r2@example.com')
        response = self.client.get(reverse('catalog:shop'), {'min_rating': '3', 'sort': 'rating'})
        self.assertEqual(response.status_code, 200)

    def test_invalid_rating_value_ignored(self):
        response = self.client.get(reverse('catalog:shop'), {'min_rating': 'abc;DROP TABLE'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['total_count'], 2)


class ProductCompareViewTests(TestCase):
    """Side-by-side comparison matrix."""

    def setUp(self):
        self.category = Category.objects.create(name='لپ‌تاپ', slug='laptop')
        self.brand = Brand.objects.create(name='ایسوس', slug='asus')
        self.p1 = Product.objects.create(
            name='زارفای G14', slug='zephyrus-g14', sku='ZG14',
            category=self.category, brand=self.brand, base_price=Decimal('90000000'),
        )
        self.p2 = Product.objects.create(
            name='ویویobook', slug='vivobook', sku='VB1',
            category=self.category, brand=self.brand, base_price=Decimal('40000000'),
        )
        ProductSpecification.objects.create(product=self.p1, key='پردازنده', value='Ryzen 9')
        ProductSpecification.objects.create(product=self.p2, key='پردازنده', value='Ryzen 5')

    def test_compare_page_lists_both_products(self):
        url = reverse('catalog:compare') + f'?ids={self.p1.id},{self.p2.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['products']), 2)
        self.assertEqual(len(response.context['spec_rows']), 1)

    def test_compare_caps_at_three_products(self):
        extra = [
            Product.objects.create(
                name=f'کالا {i}', slug=f'item-{i}', sku=f'IT{i}',
                category=self.category, brand=self.brand, base_price=Decimal('1000'),
            ) for i in range(4)
        ]
        ids = ','.join(str(p.id) for p in [self.p1, self.p2] + extra)
        response = self.client.get(reverse('catalog:compare') + f'?ids={ids}')
        self.assertLessEqual(len(response.context['products']), 3)

    def test_compare_rejects_non_numeric_ids(self):
        response = self.client.get(reverse('catalog:compare') + '?ids=1,<script>,abc')
        self.assertEqual(response.status_code, 200)

    def test_compare_inactive_product_hidden(self):
        self.p2.is_active = False
        self.p2.save()
        response = self.client.get(reverse('catalog:compare') + f'?ids={self.p1.id},{self.p2.id}')
        self.assertEqual(len(response.context['products']), 1)
