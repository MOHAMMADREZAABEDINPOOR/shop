import os
import random
import shutil
import urllib.request
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify

from catalog.models import Category, Brand, Product, ProductVariant, ProductImage, ProductSpecification
from reviews.models import Review
from accounts.models import User

class Command(BaseCommand):
    help = "Generates over 1,000 richly detailed, realistic e-commerce products with multi-angle images, specifications, reviews, and variants."

    def handle(self, *args, **options):
        self.stdout.write("Starting massive catalog scale-up (1,000+ realistic products)...")

        # 1. Download multi-angle image bank
        self.setup_angle_images()

        # 2. Setup categories and brands
        categories_map, brands_map = self.setup_categories_and_brands()

        # 3. Create customers for reviews
        customers = self.setup_review_users()

        # 4. Generate 1,000+ rich products
        self.generate_products(categories_map, brands_map, customers)

        total_products = Product.objects.count()
        total_images = ProductImage.objects.count()
        total_specs = ProductSpecification.objects.count()
        total_reviews = Review.objects.count()

        self.stdout.write(f"\n[OK] Catalog scale-up completed successfully!")
        self.stdout.write(f"Total Products in DB: {total_products:,}")
        self.stdout.write(f"Total Product Images in DB: {total_images:,}")
        self.stdout.write(f"Total Specifications in DB: {total_specs:,}")
        self.stdout.write(f"Total Customer Reviews in DB: {total_reviews:,}")

    def setup_angle_images(self):
        angles_dir = os.path.join("media", "products", "angles")
        os.makedirs(angles_dir, exist_ok=True)

        angle_downloads = {
            "phone_front.jpg": "https://images.unsplash.com/photo-1592750475338-74b7b21085ab?w=800&q=80",
            "phone_back.jpg": "https://images.unsplash.com/photo-1610945265064-0e34e5519bbf?w=800&q=80",
            "phone_angle.jpg": "https://images.unsplash.com/photo-1511707171634-5f897ff02aa9?w=800&q=80",
            "phone_lifestyle.jpg": "https://images.unsplash.com/photo-1580910051074-3eb694886505?w=800&q=80",

            "laptop_front.jpg": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=800&q=80",
            "laptop_angle.jpg": "https://images.unsplash.com/photo-1611186871348-b1ce696e52c9?w=800&q=80",
            "laptop_keyboard.jpg": "https://images.unsplash.com/photo-1588872657578-7efd1f1555ed?w=800&q=80",

            "audio_front.jpg": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=800&q=80",
            "audio_earbuds.jpg": "https://images.unsplash.com/photo-1590658268037-6bf12165a8df?w=800&q=80",
            "audio_angle.jpg": "https://images.unsplash.com/photo-1546435770-a3e426bf472b?w=800&q=80",

            "watch_front.jpg": "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=800&q=80",
            "watch_strap.jpg": "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800&q=80",
            "watch_angle.jpg": "https://images.unsplash.com/photo-1579586337278-3befd40fd17a?w=800&q=80",

            "coffee_front.jpg": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=800&q=80",
            "coffee_detail.jpg": "https://images.unsplash.com/photo-1517256064527-09c73fc73e38?w=800&q=80",
            "coffee_drip.jpg": "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=800&q=80",

            "acc_powerbank.jpg": "https://images.unsplash.com/photo-1583863788434-e58a36330cf0?w=800&q=80",
            "acc_cable.jpg": "https://images.unsplash.com/photo-1609091839311-d5365f9ff1c5?w=800&q=80",

            "game_controller.jpg": "https://images.unsplash.com/photo-1600080972464-8e5f35f63d08?w=800&q=80",
            "game_keyboard.jpg": "https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=800&q=80",
            "game_mouse.jpg": "https://images.unsplash.com/photo-1615663245857-ac93bb7c39e7?w=800&q=80",

            "tv_screen.jpg": "https://images.unsplash.com/photo-1593784991095-a205069470b6?w=800&q=80",
        }

        headers = {'User-Agent': 'Mozilla/5.0'}
        for filename, url in angle_downloads.items():
            filepath = os.path.join(angles_dir, filename)
            if not os.path.exists(filepath):
                try:
                    req = urllib.request.Request(url, headers=headers)
                    with urllib.request.urlopen(req, timeout=10) as resp, open(filepath, 'wb') as f:
                        shutil.copyfileobj(resp, f)
                except Exception as e:
                    # If download fails, copy fallback from products
                    fallback = os.path.join("media", "products", "iphone-16-pro-max.jpg")
                    if os.path.exists(fallback):
                        shutil.copyfile(fallback, filepath)

    def setup_categories_and_brands(self):
        cats_data = [
            ("digital", "کالای دیجیتال", "📱", [
                ("mobile", "گوشی موبایل"),
                ("laptop", "لپ‌تاپ و اولترابوک"),
                ("tablet", "تبلت و کتابخوان"),
                ("accessories", "لوازم جانبی دیجیتال"),
                ("audio", "هدفون، هندزفری و اسپیکر"),
            ]),
            ("gaming", "کنسول و تجهیزات گیمینگ", "🎮", [
                ("consoles", "کنسول بازی"),
                ("gaming-gear", "کیبورد، ماوس و هدست گیمینگ"),
            ]),
            ("wearables", "ساعت و گجت پوشیدنی", "⌚", [
                ("watches", "ساعت هوشمند"),
                ("smart-bands", "مچ‌بند ورزشی و سلامتی"),
            ]),
            ("home-kitchen", "لوازم خانگی و آشپزخانه", "☕", [
                ("coffee-makers", "اسپرسوساز و قهوه‌ساز"),
                ("kitchen-appliances", "لوازم برقی آماده‌سازی غذا"),
            ]),
            ("tv-video", "تلویزیون و صوتی تصویری", "📺", [
                ("tvs", "تلویزیون و سینمای خانگی"),
            ]),
        ]

        cats_map = {}
        for main_slug, main_name, icon, subs in cats_data:
            parent, _ = Category.objects.get_or_create(
                slug=main_slug,
                defaults={'name': main_name, 'icon': icon, 'is_active': True}
            )
            cats_map[main_slug] = parent
            for sub_slug, sub_name in subs:
                sub_cat, _ = Category.objects.get_or_create(
                    slug=sub_slug,
                    defaults={'name': sub_name, 'parent': parent, 'is_active': True}
                )
                cats_map[sub_slug] = sub_cat

        brands_data = [
            ("apple", "اپل (Apple)"),
            ("samsung", "سامسونگ (Samsung)"),
            ("xiaomi", "شیائومی (Xiaomi)"),
            ("sony", "سونی (Sony)"),
            ("asus", "ایسوس (Asus)"),
            ("lenovo", "لنوو (Lenovo)"),
            ("dell", "دل (Dell)"),
            ("hp", "اچ‌پی (HP)"),
            ("delonghi", "دلونگی (Delonghi)"),
            ("philips", "فیلیپس (Philips)"),
            ("bosch", "بوش (Bosch)"),
            ("jbl", "جی‌بی‌ال (JBL)"),
            ("marshall", "مارشال (Marshall)"),
            ("anker", "انکر (Anker)"),
            ("google", "گوگل (Google)"),
            ("lg", "ال‌جی (LG)"),
            ("razer", "ریزر (Razer)"),
            ("logitech", "لاجیتک (Logitech)"),
            ("garmin", "گارمین (Garmin)"),
            ("baseus", "باسئوس (Baseus)"),
        ]

        brands_map = {}
        for slug, name in brands_data:
            brand, _ = Brand.objects.get_or_create(slug=slug, defaults={'name': name, 'is_active': True})
            brands_map[slug] = brand

        return cats_map, brands_map

    def setup_review_users(self):
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
        return customers

    def generate_products(self, cats, brands, customers):
        # Category image banks (relative media paths)
        IMAGE_BANKS = {
            "mobile": [
                "products/angles/phone_front.jpg",
                "products/angles/phone_back.jpg",
                "products/angles/phone_angle.jpg",
                "products/angles/phone_lifestyle.jpg"
            ],
            "laptop": [
                "products/angles/laptop_front.jpg",
                "products/angles/laptop_angle.jpg",
                "products/angles/laptop_keyboard.jpg"
            ],
            "tablet": [
                "products/angles/phone_front.jpg",
                "products/angles/phone_angle.jpg",
                "products/angles/phone_back.jpg"
            ],
            "audio": [
                "products/angles/audio_front.jpg",
                "products/angles/audio_earbuds.jpg",
                "products/angles/audio_angle.jpg"
            ],
            "watches": [
                "products/angles/watch_front.jpg",
                "products/angles/watch_strap.jpg",
                "products/angles/watch_angle.jpg"
            ],
            "smart-bands": [
                "products/angles/watch_front.jpg",
                "products/angles/watch_angle.jpg"
            ],
            "accessories": [
                "products/angles/acc_powerbank.jpg",
                "products/angles/acc_cable.jpg"
            ],
            "consoles": [
                "products/angles/game_controller.jpg",
                "products/angles/game_keyboard.jpg"
            ],
            "gaming-gear": [
                "products/angles/game_keyboard.jpg",
                "products/angles/game_mouse.jpg",
                "products/angles/game_controller.jpg"
            ],
            "coffee-makers": [
                "products/angles/coffee_front.jpg",
                "products/angles/coffee_detail.jpg",
                "products/angles/coffee_drip.jpg"
            ],
            "kitchen-appliances": [
                "products/angles/coffee_front.jpg",
                "products/angles/coffee_drip.jpg"
            ],
            "tvs": [
                "products/angles/tv_screen.jpg",
                "products/angles/tv_screen.jpg"
            ],
        }

        # Archetypes generator definitions
        ARCHETYPES = [
            # 1. Phones
            {
                "cat": "mobile",
                "brand": "apple",
                "name_templates": [
                    "گوشی موبایل اپل مدل iPhone {gen} {model} ظرفیت {storage}",
                ],
                "models": ["Pro", "Pro Max", "Plus", "Standard"],
                "storages": ["128 گیگابایت", "256 گیگابایت", "512 گیگابایت", "1 ترابایت"],
                "gens": ["16", "15", "14", "13"],
                "price_min": 48000000, "price_max": 115000000,
                "specs": [
                    ("تراشه پردازنده", "Apple A-Series Bionic / Pro"),
                    ("فناوری صفحه نمایش", "Super Retina XDR OLED ۱۲۰ هرتز"),
                    ("سیستم دوربین", "سه‌گانه حرفه‌ای ۴۸ مگاپیکسل با سنسور شیفت"),
                    ("جنس فریم", "تیتانیوم گرید ۵ فضایی ضدخش"),
                    ("سیستم عامل", "iOS 18 با پشتیبانی از Apple Intelligence"),
                ]
            },
            {
                "cat": "mobile",
                "brand": "samsung",
                "name_templates": [
                    "گوشی موبایل سامسونگ مدل Galaxy {series} {model} 5G ظرفیت {storage}",
                ],
                "series": ["S24", "S23", "A55", "A35", "Z Fold 6", "Z Flip 6"],
                "models": ["Ultra", "Plus", "FE", "Enterprise Edition"],
                "storages": ["128 گیگابایت", "256 گیگابایت", "512 گیگابایت"],
                "price_min": 14000000, "price_max": 82000000,
                "specs": [
                    ("پردازنده", "Snapdragon 8 Gen 3 / Exynos Octa-Core"),
                    ("رزولوشن صفحه نمایش", "Dynamic AMOLED 2X رزولوشن QHD+"),
                    ("دوربین اصلی", "۲۰۰ مگاپیکسل واید با فوکوس لیزری"),
                    ("ظرفیت باتری", "۵۰۰۰ میلی‌آمپر ساعت با شارژ ۴۵ وات"),
                    ("پشتیبانی قلم", "همراه با قلم S-Pen اختصاصی و Galaxy AI"),
                ]
            },
            {
                "cat": "mobile",
                "brand": "xiaomi",
                "name_templates": [
                    "گوشی موبایل شیائومی مدل {series} {model} 5G با حافظه {storage}",
                ],
                "series": ["14T", "Redmi Note 13", "POCO F6", "POCO X6", "Xiaomi 14"],
                "models": ["Pro", "Ultra", "Pro Plus", "Speed Edition"],
                "storages": ["256 گیگابایت", "512 گیگابایت"],
                "price_min": 9500000, "price_max": 59000000,
                "specs": [
                    ("پردازنده", "MediaTek Dimensity 9300+ / Snapdragon 8s"),
                    ("نمایشگر", "CrystalRes AMOLED ۱۴۴ هرتز"),
                    ("شارژ فوق‌سریع", "شارژر ۱۲۰ واتی هایپرشارژ در جعبه"),
                    ("لنز دوربین", "لنزهای حرفه‌ای Leica Summilux"),
                ]
            },

            # 2. Laptops
            {
                "cat": "laptop",
                "brand": "asus",
                "name_templates": [
                    "لپ‌تاپ {size} اینچی ایسوس مدل {family} {code} با پردازنده {cpu}",
                ],
                "family": ["ROG Strix", "TUF Gaming", "Zenbook Pro", "VivoBook Pro", "Zephyrus"],
                "codes": ["G16", "A15", "Duo 16", "S14 OLED", "M16"],
                "sizes": ["14", "15.6", "16"],
                "cpu": ["Core i9 نسل 14", "Core i7", "Ryzen 9 8945HS", "Ryzen 7"],
                "price_min": 42000000, "price_max": 165000000,
                "specs": [
                    ("پردازنده مرکزی", "Intel Core i9 / AMD Ryzen 9"),
                    ("کارت گرافیک", "NVIDIA GeForce RTX 4070 / 4080 GDDR6"),
                    ("حافظه رم", "32 گیگابایت DDR5 5600MHz"),
                    ("حافظه داخلی", "1 ترابایت SSD PCIe 4.0 NVMe M.2"),
                    ("نمایشگر", "ROG Nebula Display 240Hz رزولوشن 2.5K"),
                ]
            },
            {
                "cat": "laptop",
                "brand": "apple",
                "name_templates": [
                    "مک‌بوک {model} اپل {size} اینچ با تراشه {chip} و رم {ram}",
                ],
                "model": ["Pro", "Air"],
                "sizes": ["13.6", "14.2", "15.3", "16.2"],
                "chip": ["M3", "M3 Pro", "M3 Max", "M2"],
                "ram": ["16GB", "18GB", "24GB", "36GB"],
                "price_min": 58000000, "price_max": 185000000,
                "specs": [
                    ("تراشه مجتمع", "Apple Silicon M3 / M3 Pro 3nm"),
                    ("صفحه نمایش", "Liquid Retina XDR با روشنایی ۱۶۰۰ نیت"),
                    ("شارژدهی باتری", "تا ۲۲ ساعت وب‌گردی و تماشای ویدیو"),
                    ("درگاه‌ها", "Thunderbolt 4 / USB 4، MagSafe 3، HDMI"),
                ]
            },
            {
                "cat": "laptop",
                "brand": "lenovo",
                "name_templates": [
                    "لپ‌تاپ {size} اینچی لنوو مدل {family} {gen} با گرافیک {gpu}",
                ],
                "family": ["Legion Pro 5", "Legion Slim 7", "ThinkPad X1 Carbon", "IdeaPad Gaming 3", "Yoga 9i"],
                "sizes": ["14", "15.6", "16"],
                "gen": ["نسل 9", "Gen 8", "Aura Edition"],
                "gpu": ["RTX 4060", "RTX 4070", "Intel Arc Graphics"],
                "price_min": 35000000, "price_max": 128000000,
                "specs": [
                    ("سیستم خنک‌کننده", "Legion Coldfront 5.0 با محفظه بخار"),
                    ("کیبورد", "کیبورد ارگونومیک با نورپردازی RGB ۴ منطقه‌ای"),
                    ("وزن", "۲.۱ کیلوگرم با بدنه آلومینیومی"),
                ]
            },

            # 3. Audio & Headphones
            {
                "cat": "audio",
                "brand": "sony",
                "name_templates": [
                    "هدفون بلوتوثی نویزکنسلینگ سونی مدل {model} با صدای {feature}",
                ],
                "model": ["WH-1000XM5", "WH-1000XM4", "WF-1000XM5", "LinkBuds S", "ULT WEAR"],
                "feature": ["Hi-Res Audio Wireless", "حذف نویز هوشمند V1", "بیس کوبنده و شفاف"],
                "price_min": 6500000, "price_max": 22000000,
                "specs": [
                    ("سیستم حذف نویز", "پردازنده یکپارچه V1 با ۸ میکروفون محیطی"),
                    ("عمر باتری", "تا ۳۰ ساعت پخش مداوم با نویزکنسلینگ فعال"),
                    ("پشتیبانی کدک", "LDAC، AAC، SBC و DSEE Extreme"),
                    ("اتصال همزمان", "اتصال هوشمند به دو دستگاه به صورت همزمان"),
                ]
            },
            {
                "cat": "audio",
                "brand": "anker",
                "name_templates": [
                    "ایربادز بی‌سیم انکر مدل Soundcore {model} با گواهی {cert}",
                ],
                "model": ["Liberty 4 NC", "Space A40", "Life P3", "R50i", "Sport X10"],
                "cert": ["ضدآب IPX5", "Hi-Res Audio Wireless", "شارژ سریع بی سیم"],
                "price_min": 1400000, "price_max": 7500000,
                "specs": [
                    ("قابلیت نویز کنسلینگ", "کاهش ۹۸.۵ درصدی صداهای زائد با Adaptive ANC 2.0"),
                    ("شارژدهی کل", "۵۰ ساعت همراه با کیس شارژ"),
                    ("درایور صوتی", "درایورهای ۱۱ میلی‌متری سفارشی با بیس عمیق"),
                ]
            },
            {
                "cat": "audio",
                "brand": "jbl",
                "name_templates": [
                    "اسپیکر بلوتوثی قابل حمل جی‌بی‌ال مدل {model} ضدآب {spec}",
                ],
                "model": ["Charge 5", "Flip 6", "Boombox 3", "Go 4", "PartyBox 110", "Xtreme 4"],
                "spec": ["IP67", "با توان خروجی قدرتمند", "با پاوربانک داخلی"],
                "price_min": 2100000, "price_max": 34000000,
                "specs": [
                    ("توان خروجی واقعی", "۴۰ تا ۱۶۰ وات RMS با تفکیک صدای عالی"),
                    ("ضدآب و ضدغبار", "استاندارد معتبر IP67 غوطه‌ور در آب"),
                    ("فناوری اتصال", "JBL PartyBoost برای اتصال همزمان چند اسپیکر"),
                ]
            },

            # 4. Smartwatches & Wearables
            {
                "cat": "watches",
                "brand": "apple",
                "name_templates": [
                    "ساعت هوشمند اپل مدل Apple Watch {series} {size} میلی‌متری {case}",
                ],
                "series": ["Series 9", "Series 8", "Ultra 2", "SE 2023"],
                "sizes": ["40", "41", "44", "45", "49"],
                "case": ["آلومینیومی", "تیتانیومی", "با بند اسپرت لوپ", "با بند اوشن"],
                "price_min": 14000000, "price_max": 52000000,
                "specs": [
                    ("پردازنده", "Apple S9 SiP با موتور عصبی ۴ هسته‌ای"),
                    ("روشنایی نمایشگر", "صفحه نمایش Retina تا ۳۰۰۰ نیت"),
                    ("سنسورهای پایش سلامت", "نوار قلب ECG، اکسیژن خون، دماسنج بدن و تصادف"),
                    ("مقاومت آب", "مقاومت تا عمق ۱۰۰ متری برای غواصی"),
                ]
            },
            {
                "cat": "watches",
                "brand": "samsung",
                "name_templates": [
                    "ساعت هوشمند سامسونگ مدل Galaxy Watch {model} سایز {size}mm با فریم {material}",
                ],
                "model": ["7", "Ultra", "6 Classic", "6", "FE"],
                "sizes": ["40", "44", "47"],
                "material": ["تیتانیوم ضدضربه", "آلومینیوم تقویت‌شده Armor", "استیل ضدزنگ"],
                "price_min": 7800000, "price_max": 38000000,
                "specs": [
                    ("تراشه", "Exynos W1000 ۳ نانومتری پنج هسته‌ای"),
                    ("سیستم‌عامل", "Wear OS Powered by Samsung با پشتیبانی از فارسی"),
                    ("سنسور هوشمند", "BioActive Sensor برای سنجش ترکیب بدنی BIA"),
                ]
            },
            {
                "cat": "watches",
                "brand": "garmin",
                "name_templates": [
                    "ساعت ورزشی حرفه‌ای گارمین مدل {model} با شیشه {glass}",
                ],
                "model": ["Fenix 7 Pro Solar", "Epix Pro Gen 2", "Forerunner 965", "Instinct 2X Solar"],
                "glass": ["یاقوت کبود سافایر", "سولار با شارژ خورشیدی", "Gorilla Glass DX"],
                "price_min": 28000000, "price_max": 85000000,
                "specs": [
                    ("باتری", "تا ۳۷ روز در حالت ساعت هوشمند با شارژ نوری"),
                    ("موقعیت‌یابی", "GPS چندفرکانسه Multi-Band با نقشه‌های توپوگرافی"),
                    ("چراغ‌قوه LED", "دارای چراغ‌قوه پرنور داخلی چندحالته"),
                ]
            },

            # 5. Espresso & Coffee Makers
            {
                "cat": "coffee-makers",
                "brand": "delonghi",
                "name_templates": [
                    "اسپرسوساز خانگی دلونگی مدل {model} با پمپ {bar} بار ایتالیایی",
                ],
                "model": ["Dedica EC685", "EC850.M", "Magnifica S", "Specialista Prestigio", "Eletta Explore"],
                "bar": ["۱۵", "۱۹"],
                "price_min": 8500000, "price_max": 75000000,
                "specs": [
                    ("فشار پمپ بخار", "۱۵ تا ۱۹ بار پمپ اولکا ایتالیا"),
                    ("توان مصرفی", "۱۳۵۰ تا ۱۴۵۰ وات سیستم ترموبلاک سریع"),
                    ("سیستم شیر", "نازل بخار کاپوچینوساز قابل تنظیم برای فوم شیر غلیظ"),
                    ("جنس بدنه", "استیل ضدزنگ خش‌دار پولیش‌شده"),
                ]
            },
            {
                "cat": "coffee-makers",
                "brand": "philips",
                "name_templates": [
                    "اسپرسوساز تمام اتوماتیک فیلیپس مدل {model} سری {series}",
                ],
                "model": ["EP2220", "EP3246 LatteGo", "EP5447", "HD7762 با آسیاب"],
                "series": ["2200", "3200", "5400"],
                "price_min": 18000000, "price_max": 58000000,
                "specs": [
                    ("آسیاب سرامیکی", "آسیاب ۱۰۰٪ سرامیکی با ۱۲ درجه قابل تنظیم"),
                    ("سیستم فوم شیر LatteGo", "شستشوی آسان ظرف شیر در ۱۵ ثانیه بدون شلنگ"),
                    ("منوی لمسی", "صفحه نمایش لمسی رنگی با ۶ نوشیدنی متنوع"),
                ]
            },

            # 6. Gaming Gear
            {
                "cat": "gaming-gear",
                "brand": "razer",
                "name_templates": [
                    "کیبورد مکانیکال گیمینگ ریزر مدل {model} با سوییچ {switch}",
                ],
                "model": ["BlackWidow V4 Pro", "Huntsman V3 Pro", "DeathStalker V2 Pro", "Cynosa V2"],
                "switch": ["اپتیکال آنالوگ Gen-2", "مکانیکی زرد سایلنت", "مکانیکی سبز کلیکی"],
                "price_min": 4200000, "price_max": 21000000,
                "specs": [
                    ("نرخ نمونه‌برداری", "فوق‌سریع ۸۰۰۰ هرتز Razer HyperPolling"),
                    ("نورپردازی", "Razer Chroma RGB با ۱۶.۸ میلیون رنگ مجزا برای هر کلید"),
                    ("استراحتگاه مچ دست", "چرم مصنوعی مغناطیسی با بالشتک نرم"),
                ]
            },
            {
                "cat": "gaming-gear",
                "brand": "logitech",
                "name_templates": [
                    "ماوس گیمینگ بی‌سیم لاجیتک مدل {model} سنسور {sensor}",
                ],
                "model": ["G Pro X Superlight 2", "G502 X Plus", "G305 Lightspeed", "G703 Hero"],
                "sensor": ["HERO 2 با دقت 32000 DPI", "Hero 25K اپتیکال"],
                "price_min": 2400000, "price_max": 12500000,
                "specs": [
                    ("وزن ماوس", "فوق سبک ۶۰ گرم بدون سوراخ روی بدنه"),
                    ("نوع سوییچ", "هیبریدی اپتیکال-مکانیکی LIGHTFORCE"),
                    ("شارژدهی", "تا ۹۵ ساعت بازی مداوم با یک بار شارژ"),
                ]
            },

            # 7. Accessories & Power Banks
            {
                "cat": "accessories",
                "brand": "baseus",
                "name_templates": [
                    "پاوربانک فست‌شارژ باسئوس {cap} مدل {model} توان {watt} وات",
                ],
                "cap": ["10000mAh", "20000mAh", "30000mAh"],
                "model": ["Blade HD فوق‌باریک", "Adaman فلزی", "Bipow دیجیتال", "Amblight پرو"],
                "watt": ["20W", "30W", "65W", "100W"],
                "price_min": 1100000, "price_max": 5800000,
                "specs": [
                    ("فناوری شارژ", "Power Delivery 3.0 و Quick Charge 4.0"),
                    ("پورت‌ها", "دو خروجی Type-C و دو خروجی USB-A با شارژ همزمان"),
                    ("نمایشگر دیجیتال", "نمایش دقیق ولتاژ، آمپر و درصد شارژ باقی‌مانده"),
                ]
            },
            {
                "cat": "accessories",
                "brand": "anker",
                "name_templates": [
                    "شارژر دیواری فست‌شارژ انکر مدل {model} فناوری GaN توان {watt}W",
                ],
                "model": ["735 Charger GaNPrime", "Nano II", "Prime 67W", "PowerPort Atom III"],
                "watt": ["30", "45", "65", "100"],
                "price_min": 950000, "price_max": 4800000,
                "specs": [
                    ("فناوری نیمه‌هادی GaN", "تولید حرارت بسیار کم با ۵۳٪ ابعاد کوچک‌تر"),
                    ("محافظت ایمنی ActiveShield", "پایش دما بیش از ۳ میلیون بار در طول روز"),
                ]
            },

            # 8. TVs
            {
                "cat": "tvs",
                "brand": "sony",
                "name_templates": [
                    "تلویزیون هوشمند {size} اینچ سونی مدل {model} 4K با پردازنده XR",
                ],
                "size": ["55", "65", "75", "85"],
                "model": ["BRAVIA XR A80L OLED", "X90L Full Array LED", "BRAVIA 7 Mini LED", "X85L"],
                "price_min": 45000000, "price_max": 185000000,
                "specs": [
                    ("پنل تصویر", "OLED / Full Array LED با رزولوشن 4K HDR ۱۲۰ هرتز"),
                    ("پردازنده هوش شناختی", "Cognitive Processor XR شبیه‌ساز بینایی انسان"),
                    ("صدای آکوستیک", "Acoustic Surface Audio+ خروج صدا مستقیماً از شیشه صفحه"),
                    ("ویژگی‌های گیمینگ", "دارای ۲ درگاه HDMI 2.1 با پشتیبانی VRR و ALLM برای PS5"),
                ]
            },
            {
                "cat": "tvs",
                "brand": "lg",
                "name_templates": [
                    "تلویزیون اولد {size} اینچ ال‌جی مدل {model} با رفرش‌ریت ۱۴۴Hz",
                ],
                "size": ["55", "65", "77"],
                "model": ["OLED evo G4", "OLED C3", "OLED B3", "QNED80"],
                "price_min": 52000000, "price_max": 195000000,
                "specs": [
                    ("فناوری پیکسل‌ها", "پیکسل‌های خودتابش Self-lit OLED بدون نور پس‌زمینه"),
                    ("پردازنده تصویر", "alpha 11 AI Processor 4K با هوش مصنوعی"),
                    ("سیستم عامل", "webOS 24 با پشتیبانی از Apple AirPlay 2"),
                ]
            },
        ]

        REVIEWS_POOL = [
            ("کیفیت ساخت فراتر از انتظار", "از کیفیت مونتاژ و متریال واقعاً لذت بردم. بسته‌بندی عالی بود و در کمتر از ۲۴ ساعت رسید دستم.", 5),
            ("بهترین خرید امسالم بود", "عملکردش بی‌نظیره و اصالت فیزیکی کالا کاملاً مشخصه. پیشنهاد می‌کنم حتماً بخرید.", 5),
            ("ارزش خرید بسیار بالا", "توی این رنج قیمتی رقیبی نداره. کارایی باتری و سرعت پردازش عالیه.", 4),
            ("راضیم از سفارشم", "کیفیت ساخت خوبه و کاملاً طبق مشخصاتی که نوشته بود ارسال شد. گارانتی هم معتبره.", 4),
            ("خوب و باکیفیت اما قیمت کمی بالا", "در کل راضیم، تنها نکته منفیش قیمت دلاری روز بود اما عملکردش فوق‌العاده‌ست.", 4),
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

        created_products = []
        specs_to_create = []
        images_to_create = []
        variants_to_create = []
        reviews_to_create = []

        existing_count = Product.objects.count()
        target_total = 1050
        needed = max(0, target_total - existing_count)

        self.stdout.write(f"Existing products in DB: {existing_count}. Generating {needed} new unique products...")

        counter = 1
        while len(created_products) < needed:
            # Pick an archetype
            arch = random.choice(ARCHETYPES)
            cat_obj = cats.get(arch["cat"])
            brand_obj = brands.get(arch["brand"])

            if not cat_obj or not brand_obj:
                continue

            # Generate realistic name
            tmpl = random.choice(arch["name_templates"])
            subs = {}
            if "{gen}" in tmpl: subs["gen"] = random.choice(arch.get("gens", ["1", "2"]))
            if "{model}" in tmpl: subs["model"] = random.choice(arch.get("models", ["Pro"]))
            if "{series}" in tmpl: subs["series"] = random.choice(arch.get("series", ["X"]))
            if "{storage}" in tmpl: subs["storage"] = random.choice(arch.get("storages", ["256"]))
            if "{size}" in tmpl: subs["size"] = random.choice(arch.get("sizes", ["15"]))
            if "{family}" in tmpl: subs["family"] = random.choice(arch.get("family", ["Pro"]))
            if "{code}" in tmpl: subs["code"] = random.choice(arch.get("codes", ["1"]))
            if "{cpu}" in tmpl: subs["cpu"] = random.choice(arch.get("cpu", ["Core i7"]))
            if "{chip}" in tmpl: subs["chip"] = random.choice(arch.get("chip", ["M3"]))
            if "{ram}" in tmpl: subs["ram"] = random.choice(arch.get("ram", ["16GB"]))
            if "{feature}" in tmpl: subs["feature"] = random.choice(arch.get("feature", ["شفاف"]))
            if "{cert}" in tmpl: subs["cert"] = random.choice(arch.get("cert", ["IPX5"]))
            if "{spec}" in tmpl: subs["spec"] = random.choice(arch.get("spec", ["ضدآب"]))
            if "{case}" in tmpl: subs["case"] = random.choice(arch.get("case", ["تیتانیوم"]))
            if "{material}" in tmpl: subs["material"] = random.choice(arch.get("material", ["استیل"]))
            if "{glass}" in tmpl: subs["glass"] = random.choice(arch.get("glass", ["یاقوت"]))
            if "{bar}" in tmpl: subs["bar"] = random.choice(arch.get("bar", ["15"]))
            if "{switch}" in tmpl: subs["switch"] = random.choice(arch.get("switch", ["سایلنت"]))
            if "{sensor}" in tmpl: subs["sensor"] = random.choice(arch.get("sensor", ["Hero"]))
            if "{cap}" in tmpl: subs["cap"] = random.choice(arch.get("cap", ["20000mAh"]))
            if "{watt}" in tmpl: subs["watt"] = random.choice(arch.get("watt", ["65"]))
            if "{gpu}" in tmpl: subs["gpu"] = random.choice(arch.get("gpu", ["RTX 4060"]))

            raw_name = tmpl.format(**subs)
            # Add a subtle distinguishing revision tag to guarantee uniqueness
            name = f"{raw_name} - نسخه {random.choice(['گلوبال', 'پک اصلی', 'سفارش اروپا', 'رسمی با کد رجیستری', '۲۰۲۶'])} (مدل {counter})"
            
            slug = slugify(f"{arch['brand']}-{arch['cat']}-{counter}-{random.randint(100, 999)}", allow_unicode=False)
            sku = f"{arch['brand'][:3].upper()}-{arch['cat'][:3].upper()}-{counter:04d}"

            # Pricing
            base_price = Decimal(random.randint(arch["price_min"], arch["price_max"])).quantize(Decimal('10000'))
            
            # ~35% discounted
            has_discount = (random.random() < 0.35)
            sale_price = None
            discount_percent = 0
            if has_discount:
                discount_percent = random.choice([5, 8, 10, 12, 15, 18, 20, 25, 30])
                discount_amount = (base_price * Decimal(discount_percent)) / Decimal(100)
                sale_price = (base_price - discount_amount).quantize(Decimal('10000'))

            stock = random.choice([0, 2, 3, 5, 8, 12, 18, 25, 35, 45, 60])
            is_available = stock > 0

            short_desc = f"محصول اورجینال {name} با بالاترین استانداردهای تضمین اصالت فیزیکی، عملکرد فوق‌العاده و خدمات پس از فروش رسمی."
            desc = (
                f"{name} یکی از پیشرفته‌ترین و پرطرفدارترین گزینه‌ها در دسته {cat_obj.name} محسوب می‌شود. "
                f"این کالا با بهره‌گیری از برترین متریال صنعتی، طراحی مدرن ارگونومیک و بازدهی انرژی بهینه، "
                f"تجربه‌ای متمایز و حرفه‌ای را برای کاربران فراهم می‌سازد. پلمپ معتبر شرکتی، ارسال فوق‌سریع و ضمانت بازگشت وجه ۷ روزه "
                f"از ویژگی‌های تضمین‌شده این کالا است."
            )

            p = Product(
                name=name,
                slug=slug,
                sku=sku,
                category=cat_obj,
                brand=brand_obj,
                base_price=base_price,
                sale_price=sale_price,
                discount_percent=discount_percent,
                stock=stock,
                is_available=is_available,
                is_active=True,
                is_featured=(random.random() < 0.15),
                is_bestseller=(random.random() < 0.2),
                is_new_arrival=(random.random() < 0.25),
                short_description=short_desc,
                description=desc,
            )
            created_products.append(p)
            counter += 1

        # Bulk create products
        with transaction.atomic():
            Product.objects.bulk_create(created_products, batch_size=400)

        # Retrieve saved products from DB to have IDs
        saved_products = Product.objects.filter(id__gt=existing_count).select_related('category')
        self.stdout.write(f"Saved {saved_products.count()} new products. Attaching multi-angle images, specifications, and reviews...")

        for p in saved_products:
            cat_slug = p.category.slug
            # Find category image bank or fallback
            img_pool = IMAGE_BANKS.get(cat_slug, IMAGE_BANKS["mobile"])

            # Add multi-angle images
            # Angle 1: Primary
            images_to_create.append(ProductImage(
                product=p,
                image=img_pool[0],
                alt_text=f"{p.name} - نمای روبرو و کاور",
                is_feature=True,
                order=1
            ))
            # Additional angles
            for idx, img_path in enumerate(img_pool[1:], start=2):
                images_to_create.append(ProductImage(
                    product=p,
                    image=img_path,
                    alt_text=f"{p.name} - نمای جانبی و زاویه {idx}",
                    is_feature=False,
                    order=idx
                ))

            # Add Specs from Archetype
            # Pick a matching archetype
            matching_archs = [a for a in ARCHETYPES if a["cat"] == cat_slug]
            chosen_arch = matching_archs[0] if matching_archs else ARCHETYPES[0]
            for key, val in chosen_arch.get("specs", []):
                specs_to_create.append(ProductSpecification(
                    product=p,
                    key=key,
                    value=val
                ))
            # Add universal warranty spec
            specs_to_create.append(ProductSpecification(
                product=p,
                key="گارانتی و اصالت",
                value="۱۸ ماه گارانتی رسمی معتبر شرکتی + ۷ روز مهلت تست اصالت"
            ))

            # Add Customer Reviews (1 to 3 reviews per product for 60% of products)
            if random.random() < 0.6:
                review_count = min(random.randint(1, 3), len(customers))
                chosen_revs = random.sample(REVIEWS_POOL, review_count)
                chosen_customers = random.sample(customers, review_count)
                for i in range(review_count):
                    title, comment, rating = chosen_revs[i]
                    user = chosen_customers[i]
                    reviews_to_create.append(Review(
                        product=p,
                        user=user,
                        title=title,
                        comment=comment,
                        rating=rating,
                        is_verified_buyer=(random.random() < 0.8),
                        is_approved=True
                    ))

            # Add Variants for 40% of products (Color variants with price delta)
            if random.random() < 0.4:
                chosen_colors = random.sample(COLOR_VARIANTS, 2)
                for idx, (col_name, col_hex) in enumerate(chosen_colors):
                    price_delta = base_price + Decimal(idx * 500000)
                    variants_to_create.append(ProductVariant(
                        product=p,
                        sku=f"{p.sku}-V{idx+1}",
                        name=f"رنگ {col_name}",
                        price_override=price_delta if idx > 0 else None,
                        stock=random.randint(3, 20),
                        is_active=True
                    ))

        # Bulk create related records in batches
        self.stdout.write(f"Bulk creating {len(images_to_create):,} images...")
        ProductImage.objects.bulk_create(images_to_create, batch_size=600)

        self.stdout.write(f"Bulk creating {len(specs_to_create):,} specifications...")
        ProductSpecification.objects.bulk_create(specs_to_create, batch_size=600)

        self.stdout.write(f"Bulk creating {len(reviews_to_create):,} customer reviews...")
        Review.objects.bulk_create(reviews_to_create, batch_size=600)

        if variants_to_create:
            self.stdout.write(f"Bulk creating {len(variants_to_create):,} variants...")
            ProductVariant.objects.bulk_create(variants_to_create, batch_size=600)
