import datetime
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import transaction
from accounts.models import User, Address
from catalog.models import Category, Brand, Product, ProductVariant, ProductSpecification, ProductImage
from orders.models import Coupon
from core.models import SiteSetting, Banner
from reviews.models import Review

class Command(BaseCommand):
    help = "Populates realistic, rich seed data for development and testing."

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Seeding initial database with rich marketplace data..."))

        with transaction.atomic():
            # 1. Site Settings
            site_settings, _ = SiteSetting.objects.get_or_create(id=1)
            site_settings.site_name = "فروشگاه اینترنتی آوانگارد"
            site_settings.site_tagline = "خرید آسان، قیمت بی‌رقیب، اصالت قطعی کالا"
            site_settings.phone = "021-88990011"
            site_settings.email = "info@avangard.local"
            site_settings.address = "تهران، میدان ونک، خیابان ولیعصر، برج فناوری آوانگارد، طبقه ۵"
            site_settings.currency = "تومان"
            site_settings.free_shipping_threshold = Decimal('600000')
            site_settings.standard_shipping_cost = Decimal('45000')
            site_settings.save()

            # 2. Users
            admin_user, _ = User.objects.get_or_create(
                email="admin@shop.local",
                defaults={
                    'first_name': 'مدیر',
                    'last_name': 'سیستم',
                    'role': User.Role.SUPERADMIN,
                    'is_staff': True,
                    'is_superuser': True,
                    'is_verified': True,
                }
            )
            admin_user.set_password("AdminPass1234!")
            admin_user.save()

            staff_user, _ = User.objects.get_or_create(
                email="staff@shop.local",
                defaults={
                    'first_name': 'رضا',
                    'last_name': 'کارشناس انبار',
                    'role': User.Role.STAFF,
                    'is_staff': True,
                    'is_verified': True,
                }
            )
            staff_user.set_password("StaffPass1234!")
            staff_user.save()

            customer1, _ = User.objects.get_or_create(
                email="customer1@shop.local",
                defaults={
                    'first_name': 'سارا',
                    'last_name': 'احمدی',
                    'phone_number': '09121112233',
                    'role': User.Role.CUSTOMER,
                    'is_verified': True,
                }
            )
            customer1.set_password("CustomerPass1234!")
            customer1.save()

            customer2, _ = User.objects.get_or_create(
                email="customer2@shop.local",
                defaults={
                    'first_name': 'محمد',
                    'last_name': 'کاظمی',
                    'phone_number': '09123334455',
                    'role': User.Role.CUSTOMER,
                    'is_verified': True,
                }
            )
            customer2.set_password("CustomerPass1234!")
            customer2.save()

            # Addresses for Customer 1
            Address.objects.get_or_create(
                user=customer1,
                title="منزل",
                defaults={
                    'receiver_name': 'سارا احمدی',
                    'receiver_phone': '09121112233',
                    'province': 'تهران',
                    'city': 'تهران',
                    'postal_code': '1998765432',
                    'address_line': 'خیابان سهروردی شمالی، کوچه آزادی، پلاک ۱۲، واحد ۴',
                    'is_default': True
                }
            )

            # 3. Categories
            cat_digital, _ = Category.objects.get_or_create(
                slug="digital",
                defaults={'name': 'کالای دیجیتال', 'icon': '📱', 'order': 1}
            )
            cat_mobile, _ = Category.objects.get_or_create(
                slug="mobile",
                defaults={'name': 'گوشی موبایل', 'parent': cat_digital, 'order': 1}
            )
            cat_laptop, _ = Category.objects.get_or_create(
                slug="laptop",
                defaults={'name': 'لپ‌تاپ و تبلت', 'parent': cat_digital, 'order': 2}
            )
            cat_accessories, _ = Category.objects.get_or_create(
                slug="accessories",
                defaults={'name': 'لوازم جانبی دیجیتال', 'parent': cat_digital, 'order': 3}
            )

            cat_home, _ = Category.objects.get_or_create(
                slug="home-kitchen",
                defaults={'name': 'لوازم خانگی و آشپزخانه', 'icon': '☕', 'order': 2}
            )
            cat_coffee, _ = Category.objects.get_or_create(
                slug="coffee-makers",
                defaults={'name': 'اسپرسوساز و قهوه‌ساز', 'parent': cat_home, 'order': 1}
            )
            cat_tv, _ = Category.objects.get_or_create(
                slug="tvs",
                defaults={'name': 'تلویزیون و سینمای خانگی', 'parent': cat_home, 'order': 2}
            )

            cat_fashion, _ = Category.objects.get_or_create(
                slug="fashion",
                defaults={'name': 'مد و پوشاک', 'icon': '⌚', 'order': 3}
            )
            cat_watches, _ = Category.objects.get_or_create(
                slug="watches",
                defaults={'name': 'ساعت و اکسسوری', 'parent': cat_fashion, 'order': 1}
            )

            # 4. Brands
            brand_apple, _ = Brand.objects.get_or_create(slug="apple", defaults={'name': 'اپل (Apple)'})
            brand_samsung, _ = Brand.objects.get_or_create(slug="samsung", defaults={'name': 'سامسونگ (Samsung)'})
            brand_sony, _ = Brand.objects.get_or_create(slug="sony", defaults={'name': 'سونی (Sony)'})
            brand_delonghi, _ = Brand.objects.get_or_create(slug="delonghi", defaults={'name': 'دلونگی (Delonghi)'})
            brand_xiaomi, _ = Brand.objects.get_or_create(slug="xiaomi", defaults={'name': 'شیائومی (Xiaomi)'})
            brand_philips, _ = Brand.objects.get_or_create(slug="philips", defaults={'name': 'فیلیپس (Philips)'})

            # 5. Products & Variants
            # Product 1: iPhone 16 Pro Max (Variable with Variants)
            p_iphone, _ = Product.objects.get_or_create(
                slug="iphone-16-pro-max",
                defaults={
                    'name': 'گوشی موبایل اپل مدل iPhone 16 Pro Max',
                    'sku': 'IPHONE-16-PM',
                    'category': cat_mobile,
                    'brand': brand_apple,
                    'short_description': 'پرچم‌دار قدرتمند اپل با تراشه بی‌نظیر A18 Pro، بدنه تیتانیومی درجه ۵ و دکمه اختصاصی Camera Control.',
                    'description': 'آیفون ۱۶ پرو مکس با نمایشگر ۶.۹ اینچی Super Retina XDR، سیستم دوربین حرفه‌ای ۴۸ مگاپیکسلی و باتری با شارژدهی فوق‌العاده، تجربه‌ای بی‌نقص از عکاسی، گیمینگ و کاربری حرفه‌ای را ارائه می‌دهد.',
                    'base_price': Decimal('98500000'),
                    'sale_price': Decimal('94900000'),
                    'discount_percent': 4,
                    'stock': 12,
                    'is_featured': True,
                    'is_bestseller': True,
                    'is_new_arrival': True,
                }
            )
            ProductVariant.objects.get_or_create(
                product=p_iphone,
                sku='IPHONE-16-PM-256-BLK',
                defaults={
                    'name': '۲۵۶ گیگابایت - تیتانیوم مشکی',
                    'price_override': Decimal('94900000'),
                    'stock': 7,
                    'is_active': True
                }
            )
            ProductVariant.objects.get_or_create(
                product=p_iphone,
                sku='IPHONE-16-PM-512-NAT',
                defaults={
                    'name': '۵۱۲ گیگابایت - تیتانیوم نچرال',
                    'price_override': Decimal('109500000'),
                    'stock': 5,
                    'is_active': True
                }
            )
            ProductSpecification.objects.get_or_create(product=p_iphone, key="تراشه پردازنده", defaults={'value': 'Apple A18 Pro (3nm)'})
            ProductSpecification.objects.get_or_create(product=p_iphone, key="فناوری صفحه نمایش", defaults={'value': 'LTPO Super Retina XDR OLED ۱۲۰ هرتز'})
            ProductSpecification.objects.get_or_create(product=p_iphone, key="دوربین اصلی", defaults={'value': 'سه‌گانه ۴۸ + ۴۸ + ۱۲ مگاپیکسل با زوم ۵ برابری'})

            # Product 2: Samsung Galaxy S24 Ultra
            p_s24, _ = Product.objects.get_or_create(
                slug="samsung-galaxy-s24-ultra",
                defaults={
                    'name': 'گوشی موبایل سامسونگ مدل Galaxy S24 Ultra 5G',
                    'sku': 'SAMSUNG-S24-ULTRA',
                    'category': cat_mobile,
                    'brand': brand_samsung,
                    'short_description': 'همراه با قلم هوشمند S-Pen و هوش مصنوعی پیشرفته Galaxy AI و دوربین ۲۰۰ مگاپیکسلی.',
                    'description': 'گلکسی S24 اولترا با فریم تیتانیومی مقاوم، شیشه محافظ Gorilla Armor با ضدبازتاب نور و تراشه اسنپ‌دراگون ۸ نسل ۳ اوج مهندسی سامسونگ است.',
                    'base_price': Decimal('78000000'),
                    'sale_price': Decimal('73500000'),
                    'discount_percent': 6,
                    'stock': 15,
                    'is_featured': True,
                    'is_bestseller': True,
                }
            )
            ProductSpecification.objects.get_or_create(product=p_s24, key="پردازنده", defaults={'value': 'Qualcomm Snapdragon 8 Gen 3 for Galaxy'})
            ProductSpecification.objects.get_or_create(product=p_s24, key="رزولوشن دوربین", defaults={'value': '۲۰۰ مگاپیکسل واید + ۵۰ مگاپیکسل پریسکوپ'})

            # Product 3: MacBook Pro M3
            Product.objects.get_or_create(
                slug="macbook-pro-14-m3",
                defaults={
                    'name': 'لپ‌تاپ ۱۴ اینچی اپل مدل MacBook Pro با تراشه M3 Pro',
                    'sku': 'MBP-14-M3-PRO',
                    'category': cat_laptop,
                    'brand': brand_apple,
                    'short_description': 'قدرت پردازشی خیره‌کننده با ۱۸ گیگابایت حافظه یکپارچه و ۵۱۲ گیگابایت SSD فوق‌سریع.',
                    'description': 'مک‌بوک پرو ۱۴ اینچ انتخابی بی‌همتا برای برنامه‌نویسان، ادیتورهای ویدیویی و طراحان گرافیک حرفه‌ای با بازدهی مصرف انرژی شگفت‌انگیز.',
                    'base_price': Decimal('135000000'),
                    'sale_price': Decimal('129000000'),
                    'discount_percent': 4,
                    'stock': 4,
                    'is_featured': True,
                }
            )

            # Product 4: Sony WH-1000XM5 Headphone
            Product.objects.get_or_create(
                slug="sony-wh-1000xm5",
                defaults={
                    'name': 'هدفون بی‌سیم نویز کنسلینگ سونی مدل WH-1000XM5',
                    'sku': 'SONY-WH-1000XM5',
                    'category': cat_accessories,
                    'brand': brand_sony,
                    'short_description': 'برترین سیستم حذف نویز فعال (Active Noise Cancelling) جهان با کیفیت صدای بی‌نظیر Hi-Res.',
                    'description': 'هدفون سونی با طراحی فوق‌سبک ارگونومیک و شارژدهی ۳۰ ساعته باتری، شفاف‌ترین تجربه شنیداری را به شما هدیه می‌دهد.',
                    'base_price': Decimal('18500000'),
                    'sale_price': Decimal('16900000'),
                    'discount_percent': 9,
                    'stock': 20,
                    'is_bestseller': True,
                }
            )

            # Product 5: Delonghi Dedica Coffee Maker
            Product.objects.get_or_create(
                slug="delonghi-dedica-ec685",
                defaults={
                    'name': 'اسپرسوساز خانگی دلونگی مدل Dedica EC685',
                    'sku': 'DELONGHI-EC685',
                    'category': cat_coffee,
                    'brand': brand_delonghi,
                    'short_description': 'طراحی باریک و شیک تمام استیل، پمپ ۱۵ بار ایتالیایی با نازل بخار حرفه‌ای برای فوم شیر.',
                    'description': 'با دلونگی ددیکا در هر لحظه یک شات اسپرسوی غلیظ، کاپوچینو یا لاته با کرمای غنی و استاندارد کافه‌ای تهیه کنید.',
                    'base_price': Decimal('9800000'),
                    'sale_price': Decimal('8900000'),
                    'discount_percent': 9,
                    'stock': 18,
                    'is_bestseller': True,
                }
            )

            # Product 6: Apple Watch Series 9
            Product.objects.get_or_create(
                slug="apple-watch-series-9",
                defaults={
                    'name': 'ساعت هوشمند اپل مدل Apple Watch Series 9 Aluminum 45mm',
                    'sku': 'AW-SERIES-9-45',
                    'category': cat_watches,
                    'brand': brand_apple,
                    'short_description': 'مجهز به ژست حرکتی نوین Double Tap، سنسورهای سلامتی سنجش اکسیژن و نوار قلب.',
                    'description': 'ساعت هوشمند اپل واچ ۹ با پردازنده دو هسته‌ای S9 SiP و صفحه نمایش ۲۰۰۰ نیتی روشن‌ترین و هوشمندترین ساعت مچی ورزشی است.',
                    'base_price': Decimal('22500000'),
                    'sale_price': Decimal('20900000'),
                    'discount_percent': 7,
                    'stock': 8,
                    'is_featured': True,
                    'is_new_arrival': True,
                }
            )

            # Product 7: Philips Electric Coffee Drip Maker
            Product.objects.get_or_create(
                slug="philips-hd7459",
                defaults={
                    'name': 'قهوه‌ساز فیلتری فیلیپس مدل HD7459',
                    'sku': 'PHILIPS-HD7459',
                    'category': cat_coffee,
                    'brand': brand_philips,
                    'short_description': 'دارای قوری شیشه‌ای پیرکس، تایمر دیجیتال قابل برنامه‌ریزی و سیستم ضدچکّه.',
                    'description': 'تهیه آسان و خودکار قهوه فرانسه تازه با عطر و طعم فوق‌العاده برای دورهمی‌های خانوادگی و اداری.',
                    'base_price': Decimal('4200000'),
                    'sale_price': Decimal('3750000'),
                    'discount_percent': 11,
                    'stock': 25,
                }
            )

            # Product 8: Xiaomi 20000mAh Power Bank
            Product.objects.get_or_create(
                slug="xiaomi-power-bank-20000",
                defaults={
                    'name': 'پاوربانک ۲۰۰۰۰ میلی‌آمپر ساعتی شیائومی مدل 50W Fast Charge',
                    'sku': 'XIAOMI-PB-20000',
                    'category': cat_accessories,
                    'brand': brand_xiaomi,
                    'short_description': 'پشتیبانی از شارژ فوق‌سریع ۵۰ وات برای انواع گوشی‌های هوشمند، تبلت و لپ‌تاپ‌های تایپ سی.',
                    'description': 'باتری لیتیوم پلیمری با دوام، خروجی سه‌گانه و محافظت ۹ لایه در برابر نوسانات ولتاژ و حرارت.',
                    'base_price': Decimal('2600000'),
                    'sale_price': Decimal('2250000'),
                    'discount_percent': 13,
                    'stock': 35,
                    'is_bestseller': True,
                }
            )

            # 6. Promotional Coupons
            now = timezone.now()
            Coupon.objects.get_or_create(
                code='WELCOME10',
                defaults={
                    'discount_type': Coupon.DiscountType.PERCENTAGE,
                    'discount_value': Decimal('10'),
                    'min_order_amount': Decimal('100000'),
                    'max_discount_amount': Decimal('200000'),
                    'start_date': now,
                    'end_date': now + datetime.timedelta(days=365),
                    'usage_limit': 1000,
                    'usage_per_user': 1,
                    'is_active': True,
                }
            )

            Coupon.objects.get_or_create(
                code='SUPER50',
                defaults={
                    'discount_type': Coupon.DiscountType.FIXED,
                    'discount_value': Decimal('50000'),
                    'min_order_amount': Decimal('250000'),
                    'start_date': now,
                    'end_date': now + datetime.timedelta(days=365),
                    'usage_limit': 500,
                    'usage_per_user': 2,
                    'is_active': True,
                }
            )

            # 7. Customer Reviews
            Review.objects.get_or_create(
                product=p_iphone,
                user=customer1,
                defaults={
                    'rating': 5,
                    'title': 'خرید فوق‌العاده و اصالت ۱۰۰٪ کالا',
                    'comment': 'گوشی با بسته‌بندی عالی و پلمپ رسمی رسید. رنگ تیتانیوم نچرال بسیار چشم‌نواز است و سرعت اجرای برنامه‌ها شگفت‌انگیز است. تحویل هم کمتر از ۲۴ ساعت انجام شد.',
                    'is_verified_buyer': True,
                    'is_approved': True,
                }
            )

            Review.objects.get_or_create(
                product=p_s24,
                user=customer2,
                defaults={
                    'rating': 5,
                    'title': 'بهترین پرچم‌دار اندرویدی بازار',
                    'comment': 'قلم اس‌پن عالیه، هوش مصنوعی سامسونگ بسیار کاربردی است و عکس‌های شب کیفیت بی‌نظیری دارند.',
                    'is_verified_buyer': True,
                    'is_approved': True,
                }
            )

            # 8. Banners
            Banner.objects.update_or_create(
                position='hero',
                defaults={
                    'title': 'پرچم‌داران دنیای دیجیتال، بدون واسطه و با گارانتی معتبر',
                    'subtitle': 'آیفون ۱۶ پرو مکس، گلکسی اس ۲۴ اولترا و جدیدترین لپ‌تاپ‌های دنیا با ارسال فوری و تحویل اکسپرس',
                    'image': 'banners/hero_main.jpg',
                    'link_url': '/shop/',
                    'button_text': 'مشاهده محصولات منتخب',
                    'order': 1,
                    'is_active': True
                }
            )
            Banner.objects.update_or_create(
                position='middle_dual_1',
                defaults={
                    'title': 'جدیدترین گجت‌های هوشمند ۲۰۲۶',
                    'subtitle': 'تا ۳۰٪ تخفیف روی تمامی لوازم جانبی و ابزارهای تکنولوژی',
                    'image': 'banners/banner_gadgets.jpg',
                    'link_url': '/shop/?category=accessories',
                    'button_text': 'مشاهده تخفیف‌ها',
                    'order': 2,
                    'is_active': True
                }
            )
            Banner.objects.update_or_create(
                position='middle_dual_2',
                defaults={
                    'title': 'کیفیت صدای بی‌نظیر های‌فای',
                    'subtitle': 'بهترین هدفون‌ها و اسپیکرهای حرفه‌ای با ضمانت تعویض',
                    'image': 'banners/banner_audio.jpg',
                    'link_url': '/shop/?category=accessories',
                    'button_text': 'خرید سیستم صوتی',
                    'order': 3,
                    'is_active': True
                }
            )
            Banner.objects.update_or_create(
                position='special_offer',
                defaults={
                    'title': 'جشنواره فصل فناوری و لوازم خانگی لوکس',
                    'subtitle': 'ارسال رایگان برای تمام سفارش‌های بالای ۵۰۰ هزار تومان با کد تخفیف WELCOME10',
                    'image': 'banners/banner_special.jpg',
                    'link_url': '/shop/?discount=1',
                    'button_text': 'خرید شگفت‌انگیز',
                    'order': 4,
                    'is_active': True
                }
            )

            # 9. Product Images
            images_map = {
                'iphone-16-pro-max': 'products/iphone-16-pro-max.jpg',
                'samsung-galaxy-s24-ultra': 'products/samsung-galaxy-s24-ultra.jpg',
                'macbook-pro-14-m3': 'products/macbook-pro-14-m3.jpg',
                'sony-wh-1000xm5': 'products/sony-wh-1000xm5.jpg',
                'delonghi-dedica-ec685': 'products/delonghi-dedica-ec685.jpg',
                'apple-watch-series-9': 'products/apple-watch-series-9.jpg',
                'philips-hd7459': 'products/philips-hd7459.jpg',
                'xiaomi-power-bank-20000': 'products/xiaomi-power-bank-20000.jpg',
            }
            for slug, img_path in images_map.items():
                try:
                    prod = Product.objects.get(slug=slug)
                    ProductImage.objects.update_or_create(
                        product=prod,
                        is_feature=True,
                        defaults={'image': img_path, 'alt_text': prod.name, 'order': 1}
                    )
                except Product.DoesNotExist:
                    pass


        self.stdout.write(self.style.SUCCESS("[OK] Seed data created successfully!"))
        self.stdout.write(self.style.SUCCESS(
            "\nTest Accounts Credentials:\n"
            "Super Admin: admin@shop.local / AdminPass1234!\n"
            "Warehouse Staff: staff@shop.local / StaffPass1234!\n"
            "Customer 1: customer1@shop.local / CustomerPass1234!\n"
            "Customer 2: customer2@shop.local / CustomerPass1234!\n"
            "Coupons: WELCOME10, SUPER50\n"
        ))
