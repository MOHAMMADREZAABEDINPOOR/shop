import json
import datetime
from decimal import Decimal
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from accounts.models import User, Address
from catalog.models import Category, Product
from cart.models import Cart, CartItem
from orders.models import Order, Coupon

class CheckoutAndOrderIntegrityTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.customer = User.objects.create_user(
            email="buyer@shop.local",
            password="Password1234!",
            first_name="Buyer",
            last_name="Test"
        )
        self.other_user = User.objects.create_user(
            email="intruder@shop.local",
            password="Password1234!",
            first_name="Intruder",
            last_name="Test"
        )
        self.address = Address.objects.create(
            user=self.customer,
            title="Office",
            receiver_name="Buyer Test",
            receiver_phone="09121234567",
            province="Tehran",
            city="Tehran",
            postal_code="1112223334",
            address_line="Tower 5, Floor 2",
            is_default=True
        )
        self.category = Category.objects.create(name="Gadgets", slug="gadgets")
        self.product = Product.objects.create(
            name="Smart Speaker",
            slug="smart-speaker",
            sku="SPK-01",
            category=self.category,
            base_price=Decimal('500000'),
            stock=5,
            is_active=True
        )
        # Promotional Coupon
        now = timezone.now()
        self.coupon = Coupon.objects.create(
            code="SAVE10",
            discount_type=Coupon.DiscountType.PERCENTAGE,
            discount_value=Decimal('10'),
            min_order_amount=Decimal('100000'),
            start_date=now - datetime.timedelta(days=1),
            end_date=now + datetime.timedelta(days=10),
            is_active=True
        )

    def test_valid_checkout_atomic_inventory_reduction(self):
        self.client.login(username='buyer@shop.local', password='Password1234!')
        cart = Cart.objects.create(user=self.customer, is_active=True)
        CartItem.objects.create(cart=cart, product=self.product, quantity=2)

        # Submit checkout
        res = self.client.post(reverse('orders:checkout'), {
            'address_id': self.address.id,
            'shipping_method': 'پست پیشتاز'
        })
        self.assertEqual(res.status_code, 302)

        # Inventory must be reduced from 5 to 3
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 3)

        # Order must exist with snapshots
        order = Order.objects.filter(user=self.customer).first()
        self.assertIsNotNone(order)
        self.assertEqual(order.subtotal, Decimal('1000000'))
        self.assertEqual(order.shipping_name, "Buyer Test")
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.items.first().product_name, "Smart Speaker")

    def test_checkout_fails_on_insufficient_stock(self):
        """Cannot oversell beyond real stock."""
        self.client.login(username='buyer@shop.local', password='Password1234!')
        cart = Cart.objects.create(user=self.customer, is_active=True)
        # Attempt to order 10 when stock is only 5
        CartItem.objects.create(cart=cart, product=self.product, quantity=10)

        res = self.client.post(reverse('orders:checkout'), {
            'address_id': self.address.id
        })
        # Must redirect back to cart with error
        self.assertEqual(res.status_code, 302)
        self.assertEqual(Order.objects.count(), 0)
        # Stock untouched
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 5)

    def test_order_idor_access_protection(self):
        """Intruder cannot inspect another user's order invoice."""
        order = Order.objects.create(
            order_number="ORD-TEST-9999",
            user=self.customer,
            shipping_name="Buyer",
            shipping_phone="09121234567",
            shipping_province="Tehran",
            shipping_city="Tehran",
            shipping_postal_code="1112223334",
            shipping_address_line="Address",
            subtotal=Decimal('500000'),
            grand_total=Decimal('500000')
        )

        self.client.login(username='intruder@shop.local', password='Password1234!')
        res = self.client.get(reverse('accounts:order_detail', kwargs={'order_number': order.order_number}))
        self.assertEqual(res.status_code, 404)
