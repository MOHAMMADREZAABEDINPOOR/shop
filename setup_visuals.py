import os
import shutil
import urllib.request
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop_project.settings')
django.setup()

from django.conf import settings
from catalog.models import Product, ProductImage
from core.models import Banner

MEDIA_ROOT = settings.MEDIA_ROOT
PRODUCTS_DIR = os.path.join(MEDIA_ROOT, 'products')
BANNERS_DIR = os.path.join(MEDIA_ROOT, 'banners')

os.makedirs(PRODUCTS_DIR, exist_ok=True)
os.makedirs(BANNERS_DIR, exist_ok=True)

ARTIFACT_DIR = r"C:\Users\PIMX\.gemini\antigravity-ide\brain\60f7299c-3fa9-48fc-84d0-6077075cb92e"

def copy_generated_files():
    print("Copying AI-generated assets...")
    # 1. Hero banner
    hero_src = os.path.join(ARTIFACT_DIR, "hero_banner_tech_1789911532223.jpg")
    hero_dst = os.path.join(BANNERS_DIR, "hero_main.jpg")
    if os.path.exists(hero_src):
        shutil.copyfile(hero_src, hero_dst)
        print(f"Copied hero banner to {hero_dst}")

    # 2. iPhone
    iphone_src = os.path.join(ARTIFACT_DIR, "iphone_16_pro_1789911547175.jpg")
    iphone_dst = os.path.join(PRODUCTS_DIR, "iphone-16-pro-max.jpg")
    if os.path.exists(iphone_src):
        shutil.copyfile(iphone_src, iphone_dst)
        print(f"Copied iPhone photo to {iphone_dst}")

    # 3. Samsung S24
    s24_src = os.path.join(ARTIFACT_DIR, "samsung_s24_ultra_1789911617449.jpg")
    s24_dst = os.path.join(PRODUCTS_DIR, "samsung-galaxy-s24-ultra.jpg")
    if os.path.exists(s24_src):
        shutil.copyfile(s24_src, s24_dst)
        print(f"Copied Samsung S24 photo to {s24_dst}")

def download_image(url, destination):
    print(f"Downloading {url} -> {destination}")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=15) as response, open(destination, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        print(f"Success: {os.path.basename(destination)}")
        return True
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return False

# High quality studio images
EXTERNAL_PRODUCTS = {
    "macbook-pro-14-m3": {
        "url": "https://images.unsplash.com/photo-1517336714731-489689fd1ca8?w=1000&q=85",
        "filename": "macbook-pro-14-m3.jpg"
    },
    "sony-wh-1000xm5": {
        "url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=1000&q=85",
        "filename": "sony-wh-1000xm5.jpg"
    },
    "delonghi-dedica-ec685": {
        "url": "https://images.unsplash.com/photo-1514432324607-a09d9b4aefdd?w=1000&q=85",
        "filename": "delonghi-dedica-ec685.jpg"
    },
    "apple-watch-series-9": {
        "url": "https://images.unsplash.com/photo-1508685096489-7aacd43bd3b1?w=1000&q=85",
        "filename": "apple-watch-series-9.jpg"
    },
    "philips-hd7459": {
        "url": "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=1000&q=85",
        "filename": "philips-hd7459.jpg"
    },
    "xiaomi-power-bank-20000": {
        "url": "https://images.unsplash.com/photo-1609592426868-b7e6518fb521?w=1000&q=85",
        "filename": "xiaomi-power-bank-20000.jpg"
    },
}

EXTERNAL_BANNERS = {
    "middle_dual_1": {
        "url": "https://images.unsplash.com/photo-1550009158-9ebf69173e03?w=1200&q=85",
        "filename": "banner_gadgets.jpg",
        "title": "جدیدترین گجت‌های هوشمند ۲۰۲۶",
        "subtitle": "تا ۳۰٪ تخفیف روی تمامی لوازم جانبی و ابزارهای تکنولوژی",
        "position": "middle_dual_1",
        "button_text": "مشاهده تخفیف‌ها",
        "link_url": "/shop/?category=accessories"
    },
    "middle_dual_2": {
        "url": "https://images.unsplash.com/photo-1526738549149-8e07eca6c147?w=1200&q=85",
        "filename": "banner_audio.jpg",
        "title": "کیفیت صدای بی‌نظیر های‌فای",
        "subtitle": "بهترین هدفون‌ها و اسپیکرهای حرفه‌ای با ضمانت تعویض",
        "position": "middle_dual_2",
        "button_text": "خرید سیستم صوتی",
        "link_url": "/shop/?category=accessories"
    },
    "special_offer": {
        "url": "https://images.unsplash.com/photo-1468495244123-6c6c332eeece?w=1400&q=85",
        "filename": "banner_special.jpg",
        "title": "جشنواره فصل فناوری و لوازم خانگی لوکس",
        "subtitle": "ارسال رایگان برای تمام سفارش‌های بالای ۵۰۰ هزار تومان با کد تخفیف WELCOME10",
        "position": "special_offer",
        "button_text": "خرید شگفت‌انگیز",
        "link_url": "/shop/?discount=1"
    }
}

def main():
    copy_generated_files()

    # Download external product photos
    for slug, data in EXTERNAL_PRODUCTS.items():
        dst = os.path.join(PRODUCTS_DIR, data['filename'])
        if not os.path.exists(dst):
            download_image(data['url'], dst)

    # Download external banner photos
    for key, data in EXTERNAL_BANNERS.items():
        dst = os.path.join(BANNERS_DIR, data['filename'])
        if not os.path.exists(dst):
            download_image(data['url'], dst)

    # Update Hero Banner
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

    # Update Dual and Special Banners
    for key, b_data in EXTERNAL_BANNERS.items():
        Banner.objects.update_or_create(
            position=b_data['position'],
            defaults={
                'title': b_data['title'],
                'subtitle': b_data['subtitle'],
                'image': f"banners/{b_data['filename']}",
                'link_url': b_data['link_url'],
                'button_text': b_data['button_text'],
                'order': 2,
                'is_active': True
            }
        )

    # Link Product Images
    ALL_PRODUCT_IMAGES = {
        "iphone-16-pro-max": "products/iphone-16-pro-max.jpg",
        "samsung-galaxy-s24-ultra": "products/samsung-galaxy-s24-ultra.jpg",
        "macbook-pro-14-m3": "products/macbook-pro-14-m3.jpg",
        "sony-wh-1000xm5": "products/sony-wh-1000xm5.jpg",
        "delonghi-dedica-ec685": "products/delonghi-dedica-ec685.jpg",
        "apple-watch-series-9": "products/apple-watch-series-9.jpg",
        "philips-hd7459": "products/philips-hd7459.jpg",
        "xiaomi-power-bank-20000": "products/xiaomi-power-bank-20000.jpg",
    }

    for slug, rel_path in ALL_PRODUCT_IMAGES.items():
        try:
            prod = Product.objects.get(slug=slug)
            ProductImage.objects.update_or_create(
                product=prod,
                is_feature=True,
                defaults={
                    'image': rel_path,
                    'alt_text': prod.name,
                    'order': 1
                }
            )
            print(f"Product image linked: {slug} -> {rel_path}")
        except Product.DoesNotExist:
            print(f"Product not found: {slug}")

    print("\nVisual setup completed successfully!")

if __name__ == '__main__':
    main()
