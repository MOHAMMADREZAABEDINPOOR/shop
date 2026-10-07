import json
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import User
from catalog.models import Category, Product
from cart.models import Cart, CartItem

class CartFlowAndMergeTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="shopper@shop.local",
            password="Password1234!",
            first_name="Shopper",
            last_name="Test"
        )
        self.category = Category.objects.create(name="Tech", slug="tech")
        self.product = Product.objects.create(
            name="Wireless Mouse",
            slug="wireless-mouse",
            sku="MOUSE-01",
            category=self.category,
            base_price=Decimal('200000'),
            sale_price=Decimal('180000'),
            stock=10,
            is_active=True
        )

    def test_add_and_update_cart(self):
        # Guest adds product
        res = self.client.post(
            reverse('cart:api_add'),
            json.dumps({'product_id': self.product.id, 'quantity': 2}),
            content_type='application/json'
        )
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(data['cart_item_count'], 2)

        # Update cart quantity
        cart = Cart.objects.filter(is_active=True).first()
        item = cart.items.first()
        res_update = self.client.post(
            reverse('cart:api_update', kwargs={'item_id': item.id}),
            json.dumps({'action': 'increase'}),
            content_type='application/json'
        )
        self.assertEqual(res_update.status_code, 200)
        self.assertEqual(res_update.json()['item_quantity'], 3)

    def test_guest_cart_merges_on_login(self):
        # 1. Guest adds item
        self.client.post(
            reverse('cart:api_add'),
            json.dumps({'product_id': self.product.id, 'quantity': 3}),
            content_type='application/json'
        )

        # 2. Login
        self.client.post(reverse('accounts:login'), {
            'email': 'shopper@shop.local',
            'password': 'Password1234!'
        })

        # 3. Verify user's cart now owns the 3 items
        user_cart = Cart.objects.filter(user=self.user, is_active=True).first()
        self.assertIsNotNone(user_cart)
        self.assertEqual(user_cart.get_item_count(), 3)
