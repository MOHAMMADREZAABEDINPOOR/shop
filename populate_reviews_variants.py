import os
import random
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop_project.settings')
django.setup()

from catalog.models import Product, ProductVariant
from reviews.models import Review
from accounts.models import User

# Fetch or create customer accounts
customers = []
user_data = [
    ("ali.rezaei@example.com", "علی", "رضایی"),
    ("maryam.rad@example.com", "مریم", "راد"),
    ("hossein.m@example.com", "حسین", "محمدی"),
    ("zahra.karimi@example.com", "زهرا", "کریمی"),
    ("mehdi.amini@example.com", "مهدی", "امینی"),
    ("niloufar.s@example.com", "نیلوفر", "صادقی"),
    ("farhad.t@example.com", "فرهاد", "تهرانی"),
    ("sara.ahmadi@example.com", "سارا", "احمدی"),
]
for email, fn, ln in user_data:
    u, _ = User.objects.get_or_create(
        email=email,
        defaults={
            'first_name': fn,
            'last_name': ln,
            'role': User.Role.CUSTOMER,
            'is_verified': True
        }
    )
    customers.append(u)

REVIEWS_POOL = [
    ("کیفیت ساخت فراتر از انتظار", "از کیفیت مونتاژ و متریال واقعاً لذت بردم. بسته‌بندی عالی بود و در کمتر از ۲۴ ساعت رسید دستم.", 5),
    ("بهترین خرید امسالم بود", "عملکردش بی‌نظیره و اصالت فیزیکی کالا کاملاً مشخصه. پیشنهاد می‌کنم حتماً بخرید.", 5),
    ("ارزش خرید بسیار بالا", "توی این رنج قیمتی رقیبی نداره. کارایی باتری و سرعت پردازش عالیه.", 4),
    ("راضیم از سفارشم", "کیفیت ساخت خوبه و کاملاً طبق مشخصاتی که نوشته بود ارسال شد. گارانتی هم معتبره.", 4),
    ("طراحی خیلی مدرن و ارگونومیک", "بسیار خوش‌دست و سبکه و عملکرد روونی داره.", 5),
    ("بسته‌بندی پلمپ و اصالت قطعی", "کد اصالت سنجیده شد و کاملاً پلمپ کارخانه‌ای بود. متشکرم از فروشگاه آوانگارد.", 5),
    ("عالی و بدون نقص", "همه‌چیزش اوکیه، پیشنهاد می‌کنم برای استفاده روزمره و حرفه‌ای شک نکنید.", 5),
]

COLOR_VARIANTS = [
    ("مشکی تیتانیوم", "#1c1c1e"),
    ("خاکستری فضایی", "#48484a"),
    ("نقره‌ای متالیک", "#e5e5ea"),
    ("آبی اقیانوسی", "#0a84ff"),
    ("سفید صدفی", "#f2f2f7"),
    ("تیتانیوم نچرال", "#8e8e93"),
]

products = Product.objects.all()
reviews_to_create = []
variants_to_create = []

print(f"Adding reviews and variants to {products.count()} products...")

for p in products:
    # Reviews
    if not Review.objects.filter(product=p).exists():
        review_count = random.randint(1, 3)
        chosen_revs = random.sample(REVIEWS_POOL, review_count)
        chosen_users = random.sample(customers, review_count)
        for i in range(review_count):
            t, c, r = chosen_revs[i]
            u = chosen_users[i]
            reviews_to_create.append(Review(
                product=p,
                user=u,
                title=t,
                comment=c,
                rating=r,
                is_verified_buyer=(random.random() < 0.8),
                is_approved=True
            ))

    # Variants (for ~50% of products)
    if not ProductVariant.objects.filter(product=p).exists() and random.random() < 0.5:
        chosen_colors = random.sample(COLOR_VARIANTS, 2)
        for idx, (col_name, col_hex) in enumerate(chosen_colors):
            delta = p.base_price + Decimal((idx + 1) * 450000)
            variants_to_create.append(ProductVariant(
                product=p,
                sku=f"{p.sku}-V{idx+1}",
                name=f"رنگ {col_name}",
                price_override=delta if idx > 0 else None,
                stock=random.randint(3, 20),
                is_active=True
            ))

print(f"Bulk inserting {len(reviews_to_create)} reviews...")
Review.objects.bulk_create(reviews_to_create, batch_size=500)

print(f"Bulk inserting {len(variants_to_create)} variants...")
ProductVariant.objects.bulk_create(variants_to_create, batch_size=500)

print(f"Done! Total Reviews: {Review.objects.count()}, Total Variants: {ProductVariant.objects.count()}")
