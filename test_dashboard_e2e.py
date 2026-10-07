"""End-to-end dashboard coverage using Django's test Client (no live server needed)."""
from django.test import TestCase
from django.urls import reverse

from accounts.models import User
from catalog.models import Category, Product


class DashboardE2ETest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin = User.objects.create_superuser(
            email="admin@shop.local",
            password="AdminPass1234!",
            first_name="Admin",
            last_name="Test",
        )
        category = Category.objects.create(name="تست", slug="test-cat")
        cls.product = Product.objects.create(
            name="کالای تستی",
            slug="test-product",
            sku="TEST-001",
            category=category,
            base_price=1000000,
            stock=10,
            is_available=True,
        )

    def test_dashboard_flows(self):
        logged_in = self.client.login(email="admin@shop.local", password="AdminPass1234!")
        self.assertTrue(logged_in, "Admin login failed")

        resp = self.client.get(reverse("dashboard:products"))
        self.assertEqual(resp.status_code, 200)

        resp = self.client.get(reverse("dashboard:product_create"))
        self.assertEqual(resp.status_code, 200)

        product = self.product

        resp = self.client.get(reverse("dashboard:product_edit", kwargs={"pk": product.id}))
        self.assertEqual(resp.status_code, 200)

        resp = self.client.post(
            reverse("dashboard:product_quick_discount", kwargs={"pk": product.id}),
            {"discount_percent": "20"},
        )
        self.assertIn(resp.status_code, (200, 302))
        product.refresh_from_db()
        self.assertEqual(product.discount_percent, 20)
        self.assertIsNotNone(product.sale_price)
