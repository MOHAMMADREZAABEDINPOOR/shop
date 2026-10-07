# -*- coding: utf-8 -*-
"""
EMBER · seed demo orders/payments spread over the last N days so the
dashboard KPIs, orders list and report charts visualize nicely.
Run:  python manage.py seed_demo_orders --count 160 --days 90
"""
import random
import uuid
from datetime import timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from accounts.models import User
from catalog.models import Product
from orders.models import Order, OrderItem
from payments.models import Payment
from catalog.ember_catalog_data import DEMO_ORDERS

DEMO_CUSTOMERS = [
    ("علی رضایی", "ali.dm@shop.local"),
    ("زهرا احمدی", "zahra.dm@shop.local"),
    ("محمد کریمی", "mohammad.dm@shop.local"),
    ("فاطمه موسوی", "fatemeh.dm@shop.local"),
    ("حسین نوری", "hossein.dm@shop.local"),
    ("مریم شریفی", "maryam.dm@shop.local"),
    ("امیر صادقی", "amir.dm@shop.local"),
    ("نگین رستمی", "negin.dm@shop.local"),
]

STATUS_WEIGHTS = [
    ("DELIVERED", 55), ("SHIPPED", 16), ("PROCESSING", 12), ("PAID", 14),
    ("AWAITING_PAYMENT", 12), ("PENDING", 6), ("CANCELLED", 12),
    ("RETURNED", 5), ("REFUNDED", 5),
]

PROVINCE_CITY = [
    ("تهران", "تهران"), ("البرز", "کرج"), ("اصفهان", "اصفهان"),
    ("فارس", "شیراز"), ("خراسان رضوی", "مشهد"), ("آذربایجان شرقی", "تبریز"),
]


class Command(BaseCommand):
    help = "Seed demo orders with items and payments over the last N days."

    def add_arguments(self, parser):
        parser.add_argument('--count', type=int, default=DEMO_ORDERS['count'])
        parser.add_argument('--days', type=int, default=DEMO_ORDERS['days'])

    def handle(self, *args, **options):
        rnd = random.Random(42)
        products = list(Product.objects.filter(is_active=True))
        if not products:
            self.stderr.write('No products found - run rebuild_catalog first.')
            return

        users = list(User.objects.filter(role='CUSTOMER', is_active=True))
        for name, email in DEMO_CUSTOMERS:
            if not User.objects.filter(email=email).exists():
                parts = name.split()
                u = User.objects.create_user(
                    email=email, password=None,
                    first_name=parts[0], last_name=parts[1] if len(parts) > 1 else '',
                )
                users.append(u)
        users = [u for u in users if not u.is_staff]
        if not users:
            self.stderr.write('No customer users available.')
            return

        now = timezone.now()
        n = int(options['count'])
        days = int(options['days'])
        created = 0

        with transaction.atomic():
            for i in range(n):
                t = now - timedelta(days=rnd.randint(0, days - 1),
                                    hours=rnd.randint(6, 22),
                                    minutes=rnd.randint(0, 59))
                user = rnd.choice(users)
                picks = rnd.sample(products, min(len(products), rnd.randint(1, 4)))

                subtotal = Decimal(0)
                lines = []
                for p in picks:
                    qty = rnd.randint(1, 2)
                    price = p.get_effective_price()
                    lines.append((p, qty, price))
                    subtotal += price * qty

                discount = Decimal(0)
                if rnd.random() < 0.28:
                    pct = Decimal(rnd.choice([5, 10, 15]))
                    discount = (subtotal * pct / 100).quantize(Decimal('1'))
                shipping = Decimal(0) if subtotal >= 500000 else Decimal(39000)
                grand = subtotal - discount + shipping

                # weighted status
                total_w = sum(w for _, w in STATUS_WEIGHTS)
                roll = rnd.randint(1, total_w)
                acc = 0
                status = 'DELIVERED'
                for st, w in STATUS_WEIGHTS:
                    acc += w
                    if roll <= acc:
                        status = st
                        break

                prov, city = rnd.choice(PROVINCE_CITY)
                number = 'ORD-%s-%05d' % (t.strftime('%Y%m%d'), i + 1)

                o = Order.objects.create(
                    order_number=number,
                    user=user,
                    shipping_name=user.get_full_name() or user.email,
                    shipping_phone='0912%07d' % rnd.randint(0, 9999999),
                    shipping_province=prov,
                    shipping_city=city,
                    shipping_postal_code='%010d' % rnd.randint(0, 9999999999),
                    shipping_address_line='خیابان نمونه، کوچه %d، پلاک %d' % (rnd.randint(1, 40), rnd.randint(1, 200)),
                    subtotal=subtotal,
                    discount_amount=discount,
                    shipping_cost=shipping,
                    tax_amount=Decimal(0),
                    grand_total=grand,
                    status=status,
                    shipping_method=rnd.choice(['اکسپرس', 'استاندارد', 'تحویل امروز']),
                    tracking_code=('TRK%08d' % rnd.randint(0, 99999999)) if status in ('SHIPPED', 'DELIVERED', 'RETURNED', 'REFUNDED') else '',
                )
                Order.objects.filter(pk=o.pk).update(created_at=t, updated_at=t)

                for p, qty, price in lines:
                    OrderItem.objects.create(
                        order=o, product=p, variant=None,
                        product_name=p.name, variant_name='',
                        unit_price=price, quantity=qty, total_price=price * qty,
                    )

                if status not in ('PENDING', 'AWAITING_PAYMENT', 'CANCELLED'):
                    Payment.objects.create(
                        order=o,
                        transaction_id=uuid.uuid4(),
                        gateway='sandbox',
                        amount=grand,
                        status='SUCCESSFUL',
                        tracking_number=str(rnd.randint(100000, 999999)),
                        idempotency_key='demo-%s' % uuid.uuid4().hex,
                        verified_at=t,
                    )
                created += 1

        self.stdout.write('seed_demo_orders: created %d orders (users: %d).' % (created, len(users)))
