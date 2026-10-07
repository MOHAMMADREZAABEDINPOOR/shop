"""
Upgrade site visuals: fetch cinematic, high-contrast Unsplash photography
for hero and promotional banners, then relink Banner DB rows.
Run:  python upgrade_visuals.py
"""
import os
import shutil
import urllib.request
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'shop_project.settings')
django.setup()

from django.conf import settings
from core.models import Banner

MEDIA_ROOT = settings.MEDIA_ROOT
BANNERS_DIR = os.path.join(MEDIA_ROOT, 'banners')
os.makedirs(BANNERS_DIR, exist_ok=True)

# Cinematic dark/neon Unsplash picks (w=1600 for hero crispness)
NEW_BANNERS = {
    'hero': {
        'url': 'https://images.unsplash.com/photo-1531297484001-80022131f5a1?w=1600&q=90&fit=max&auto=format&sat=-15&blend=050a14&blend-alpha=25',
        'filename': 'hero_main_v2.jpg',
        'title': 'پرچم‌داران دنیای دیجیتال، بدون واسطه و با گارانتی معتبر',
        'subtitle': 'آیفون ۱۶ پرو مکس، گلکسی اس ۲۴ اولترا و جدیدترین لپ‌تاپ‌های دنیا با ارسال فوری و تحویل اکسپرس',
        'link_url': '/shop/',
        'button_text': 'مشاهده محصولات منتخب',
    },
    'middle_dual_1': {
        'url': 'https://images.unsplash.com/photo-1529156069898-49953e39b3ac?w=1200&q=88&fit=max&auto=format',
        'filename': 'banner_gadgets_v2.jpg',
        'title': 'جدیدترین گجت‌های هوشمند ۲۰۲۶',
        'subtitle': 'تا ۳۰٪ تخفیف روی تمامی لوازم جانبی و ابزارهای تکنولوژی',
        'link_url': '/shop/?category=accessories',
        'button_text': 'مشاهده تخفیف‌ها',
    },
    'middle_dual_2': {
        'url': 'https://images.unsplash.com/photo-1583394838336-acd977736f90?w=1200&q=88&fit=max&auto=format',
        'filename': 'banner_audio_v2.jpg',
        'title': 'کیفیت صدای بی‌نظیر های‌فای',
        'subtitle': 'بهترین هدفون‌ها و اسپیکرهای حرفه‌ای با ضمانت تعویض',
        'link_url': '/shop/?category=accessories',
        'button_text': 'خرید سیستم صوتی',
    },
    'special_offer': {
        'url': 'https://images.unsplash.com/photo-1472851294608-062f824d29cc?w=1400&q=88&fit=max&auto=format',
        'filename': 'banner_special_v2.jpg',
        'title': 'جشنواره فصل فناوری و لوازم خانگی لوکس',
        'subtitle': 'ارسال رایگان برای تمام سفارش‌های بالای ۵۰۰ هزار تومان با کد تخفیف WELCOME10',
        'link_url': '/shop/?discount=1',
        'button_text': 'خرید شگفت‌انگیز',
    },
}


def download_image(url, destination):
    print(f"Downloading {url} -> {destination}")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=20) as response, open(destination, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        print(f"Success: {os.path.basename(destination)}")
        return True
    except Exception as e:
        print(f"Failed to download {url}: {e}")
        return False


def main():
    for position, data in NEW_BANNERS.items():
        dst = os.path.join(BANNERS_DIR, data['filename'])
        ok = os.path.exists(dst) or download_image(data['url'], dst)
        if not ok:
            print(f"Skipping banner update for {position} (image unavailable)")
            continue

        defaults = {
            'title': data['title'],
            'subtitle': data['subtitle'],
            'image': f"banners/{data['filename']}",
            'link_url': data['link_url'],
            'button_text': data['button_text'],
            'order': 1,
            'is_active': True,
        }
        Banner.objects.update_or_create(position=position, defaults=defaults)
        print(f"Banner relinked: {position} -> banners/{data['filename']}")

    print("\nVisual upgrade completed successfully!")


if __name__ == '__main__':
    main()
