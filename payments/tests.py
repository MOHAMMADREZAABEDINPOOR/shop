import uuid
from decimal import Decimal
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from accounts.models import User
from catalog.models import Category, Product
from orders.models import Order, OrderItem
from payments.models import Payment
from payments.gateways import (
    SandboxPaymentGateway, ZarinpalPaymentGateway, get_payment_gateway
)

class PaymentGatewayAndIdempotencyTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.customer = User.objects.create_user(
            email="payer@shop.local",
            password="Password1234!",
            first_name="Payer",
            last_name="Test"
        )
        self.category = Category.objects.create(name="Audio", slug="audio")
        self.product = Product.objects.create(
            name="Earbuds",
            slug="earbuds",
            sku="EAR-01",
            category=self.category,
            base_price=Decimal('100000'),
            stock=10,
            is_active=True
        )
        self.order = Order.objects.create(
            order_number="ORD-PAY-1111",
            user=self.customer,
            shipping_name="Payer",
            shipping_phone="09121111111",
            shipping_province="Tehran",
            shipping_city="Tehran",
            shipping_postal_code="1234567890",
            shipping_address_line="Line 1",
            subtotal=Decimal('100000'),
            grand_total=Decimal('100000'),
            status=Order.OrderStatus.AWAITING_PAYMENT
        )
        OrderItem.objects.create(
            order=self.order,
            product=self.product,
            product_name="Earbuds",
            unit_price=Decimal('100000'),
            quantity=1,
            total_price=Decimal('100000')
        )
        self.payment = Payment.objects.create(
            order=self.order,
            gateway='sandbox',
            amount=self.order.grand_total,
            idempotency_key="TEST-IDEMP-KEY-1"
        )

    def test_payment_verification_success(self):
        # Callback with success
        res = self.client.post(reverse('payments:verify', kwargs={'transaction_id': self.payment.transaction_id}), {
            'action': 'success',
            'card_number': '6037-9918-1234-5678'
        })
        self.assertEqual(res.status_code, 302)

        self.payment.refresh_from_db()
        self.order.refresh_from_db()

        self.assertEqual(self.payment.status, Payment.PaymentStatus.SUCCESSFUL)
        self.assertEqual(self.order.status, Order.OrderStatus.PAID)
        self.assertTrue(self.payment.tracking_number.startswith("TRX-"))

    def test_duplicate_callback_idempotency(self):
        """Second callback must not alter status or cause duplicated actions."""
        # 1st callback
        self.client.post(reverse('payments:verify', kwargs={'transaction_id': self.payment.transaction_id}), {
            'action': 'success'
        })
        self.payment.refresh_from_db()
        first_tracking = self.payment.tracking_number

        # 2nd duplicate callback
        res_second = self.client.post(reverse('payments:verify', kwargs={'transaction_id': self.payment.transaction_id}), {
            'action': 'success'
        })
        self.assertEqual(res_second.status_code, 302)

        self.payment.refresh_from_db()
        # Tracking number remains identical and state is preserved
        self.assertEqual(self.payment.tracking_number, first_tracking)
        self.assertEqual(self.payment.status, Payment.PaymentStatus.SUCCESSFUL)

    def test_payment_cancellation_restores_inventory(self):
        """If buyer cancels in gateway, order is cancelled and reserved inventory is restored."""
        # Deduct product stock in checkout simulation (10 -> 9)
        self.product.stock = 9
        self.product.save()

        self.client.post(reverse('payments:verify', kwargs={'transaction_id': self.payment.transaction_id}), {
            'action': 'cancel'
        })

        self.order.refresh_from_db()
        self.payment.refresh_from_db()
        self.product.refresh_from_db()

        self.assertEqual(self.payment.status, Payment.PaymentStatus.CANCELLED)
        self.assertEqual(self.order.status, Order.OrderStatus.CANCELLED)
        # Stock restored to 10!
        self.assertEqual(self.product.stock, 10)


class PaymentGatewayFactoryTests(TestCase):
    """Gateway resolver selection & secure fallback behavior."""

    @override_settings(PAYMENT_GATEWAY_DEFAULT='sandbox')
    def test_default_resolves_sandbox(self):
        self.assertIsInstance(get_payment_gateway(), SandboxPaymentGateway)

    @override_settings(PAYMENT_GATEWAY_DEFAULT='zarinpal', ZARINPAL_MERCHANT_ID='mid-123')
    def test_zarinpal_selected_when_configured(self):
        gateway = get_payment_gateway()
        self.assertIsInstance(gateway, ZarinpalPaymentGateway)
        self.assertEqual(gateway.merchant_id, 'mid-123')

    @override_settings(PAYMENT_GATEWAY_DEFAULT='zarinpal', ZARINPAL_MERCHANT_ID='')
    def test_zarinpal_without_credentials_falls_back_to_sandbox(self):
        """Unconfigured production gateway must never crash checkout."""
        self.assertIsInstance(get_payment_gateway(), SandboxPaymentGateway)

    @override_settings(PAYMENT_GATEWAY_DEFAULT='unknown-gateway')
    def test_unknown_gateway_falls_back_to_sandbox(self):
        self.assertIsInstance(get_payment_gateway(), SandboxPaymentGateway)
