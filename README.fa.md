<div align="center">

<img src="assets/readme/hero.gif" width="1200" alt="COMMERCE · DJANGO: a shopping cart with products and a checkout receipt" />

**[English](README.md) · [فارسی](README.fa.md)**

</div>

<div dir="rtl">

# 🛒 COMMERCE · DJANGO

فروشگاه Django با تنوع محصول، سبد مهمان و مشتری، ثبت سفارش با کنترل موجودی، شبیه‌ساز پرداخت محلی و داشبورد عملیات.

[GitHub](https://github.com/MOHAMMADREZAABEDINPOOR/shop) · [PIMX / Profile](https://github.com/MOHAMMADREZAABEDINPOOR) · [بنر ثابت](assets/readme/hero.png)

| نمای کلی | جزئیات |
|:---|:---|
| 🛒 تجربه | برنامه وب / تجربه مرورگری |
| 🧰 فناوری | `Django>=5.1,<6.2` · `Pillow>=10.0.0` · `cryptography>=42.0.0` |
| 🌐 زبان راهنما | [English](README.md) · [فارسی](README.fa.md) |

[✨ امکانات](#امکانات) · [🚀 شروع کار](#شروع-کار) · [⚙️ تنظیمات](#تنظیمات) · [🌍 استقرار](#استقرار)

---

<a id="امکانات"></a>

## ✨ امکانات

| بخش | قابلیت موجود |
|:---|:---|
| 🛍️ فروشگاه | فیلتر کاتالوگ، جست‌وجوی زنده و گونه محصول |
| 🛍️ فروشگاه | ادغام سبد مهمان، آدرس و تسویه چندمرحله‌ای |
| 🛍️ فروشگاه | پردازش تراکنشی سفارش و پرداخت و قفل موجودی |
| 🌐 تجربه کاربری | نظر، داشبورد و ظاهر فروشگاه فارسی |

<a id="پشته-فنی"></a>

## 🧰 پشته فنی

| ابزار | نسخه یا منبع |
|---|---|
| Django>=5.1,<6.2 | `requirements.txt` |
| Pillow>=10.0.0 | `requirements.txt` |
| cryptography>=42.0.0 | `requirements.txt` |

<a id="شروع-کار"></a>

## 🚀 شروع کار

Python 3 و محیط دسکتاپ برای پروژه‌های Tkinter/Turtle؛ Tkinter از اجزای نصب Python است و با pip نصب نمی‌شود. برای وابستگی‌های قدیمی از نسخه Python سازگار استفاده کنید.

<div dir="ltr">

```bash
git clone https://github.com/MOHAMMADREZAABEDINPOOR/shop.git
cd shop

python -m venv .venv
# Windows: .venv\Scripts\Activate.ps1; macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
# Copy .env.example to .env
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

</div>

<a id="تنظیمات"></a>

## ⚙️ تنظیمات

کلیدهای زیر از فایل نمونه یا کد استخراج شده‌اند؛ همه الزاماً اجباری نیستند. مقدار و پیش‌فرض را در همان فایل بررسی و اسرار را فقط در محیط محلی یا هاست تنظیم کنید.

| نام | کاربرد |
|---|---|
| `ALLOWED_HOSTS` | تنظیم برنامه؛ تعریف را در منبع بررسی کنید |
| `ANALYTICS_ID` | تنظیم برنامه؛ تعریف را در منبع بررسی کنید |
| `DATABASE_URL` | اعتبارنامه یا اتصال؛ خصوصی نگه دارید |
| `DATA_ENCRYPTION_KEY` | اعتبارنامه یا اتصال؛ خصوصی نگه دارید |
| `DEBUG` | تنظیم برنامه؛ تعریف را در منبع بررسی کنید |
| `DEFAULT_FROM_EMAIL` | تنظیم برنامه؛ تعریف را در منبع بررسی کنید |
| `EMAIL_BACKEND` | تنظیم برنامه؛ تعریف را در منبع بررسی کنید |
| `EMAIL_HOST` | تنظیم برنامه؛ تعریف را در منبع بررسی کنید |
| `EMAIL_HOST_PASSWORD` | اعتبارنامه یا اتصال؛ خصوصی نگه دارید |
| `EMAIL_HOST_USER` | تنظیم برنامه؛ تعریف را در منبع بررسی کنید |
| `EMAIL_PORT` | تنظیم برنامه؛ تعریف را در منبع بررسی کنید |
| `EMAIL_USE_TLS` | تنظیم برنامه؛ تعریف را در منبع بررسی کنید |
| `PAYMENT_GATEWAY_DEFAULT` | تنظیم برنامه؛ تعریف را در منبع بررسی کنید |
| `PAYMENT_PUBLIC_KEY` | اعتبارنامه یا اتصال؛ خصوصی نگه دارید |
| `PAYMENT_SECRET` | اعتبارنامه یا اتصال؛ خصوصی نگه دارید |
| `REDIS_URL` | تنظیم برنامه؛ تعریف را در منبع بررسی کنید |
| `SECRET_KEY` | اعتبارنامه یا اتصال؛ خصوصی نگه دارید |
| `ZARINPAL_MERCHANT_ID` | تنظیم برنامه؛ تعریف را در منبع بررسی کنید |
| `ZARINPAL_SANDBOX` | تنظیم برنامه؛ تعریف را در منبع بررسی کنید |

<a id="استفاده"></a>

## 🎯 استفاده

نمونه محیط را به .env کپی و روی دیتابیس توسعه تازه migrate و seed_data را اجرا کنید. /shop/ را باز، محصول اضافه و /orders/checkout/ را تکمیل کنید. /dashboard/ برای عملیات و /admin/ برای مدیریت Django است.

<a id="ساختار-پروژه"></a>

## 🗂️ ساختار پروژه

| مسیر | نقش |
|---|---|
| [`accounts/`](accounts/) | اپ حساب |
| [`assets/`](assets/) | فایل برند، رسانه و README |
| [`cart/`](cart/) | فرآیند سبد |
| [`catalog/`](catalog/) | کاتالوگ محصول |
| [`dashboard/`](dashboard/) | داشبورد عملیات |
| [`docs/`](docs/) | راهنمای تکمیلی |
| [`orders/`](orders/) | فرآیند سفارش |
| [`payments/`](payments/) | فرآیند پرداخت |
| [`static/`](static/) | فایل استاتیک وب |
| [`templates/`](templates/) | قالب سمت سرور |
| [`manage.py`](manage.py) | فایل ورودی یا تنظیم پروژه |
| [`populate_reviews_variants.py`](populate_reviews_variants.py) | فایل ورودی یا تنظیم پروژه |
| [`setup_visuals.py`](setup_visuals.py) | فایل ورودی یا تنظیم پروژه |
| [`test_dashboard_e2e.py`](test_dashboard_e2e.py) | فایل ورودی یا تنظیم پروژه |
| [`upgrade_visuals.py`](upgrade_visuals.py) | فایل ورودی یا تنظیم پروژه |

<a id="فرمان‌ها-و-بررسی"></a>

## 🧪 فرمان‌ها و بررسی

<div dir="ltr">

```bash
python manage.py check
python manage.py test
```

</div>

<a id="استقرار"></a>

## 🌍 استقرار

فایل محیط واقعی، HTTPS، دیتابیس مستقل و میزبان مجاز تنظیم کنید. در PHP ریشه وب را public/ و در Django فایل استاتیک و WSGI/ASGI را تنظیم کنید. سرور توسعه برای میزبانی عمومی نیست.

<a id="محدودیت‌ها"></a>

## 📌 محدودیت‌ها

درگاه پرداخت شبیه‌ساز محلی است و اتصال بانکی واقعی نیست. SQLite رفتار قفل ردیف PostgreSQL را بازسازی نمی‌کند. حساب نمونه فقط برای توسعه است؛ دیتابیس و رسانه محلی منتشر نمی‌شوند.

<a id="رفع-مشکل"></a>

## 🛠️ رفع مشکل

- پکیج غایب: وابستگی را با مدیر پکیج پروژه نصب کنید.
- خطای API یا شبکه: آدرس، سرویس و اتصال میزبانی را بررسی کنید.
- فایل قدیمی: در صورت وجود اسکریپت ساخت، build و کش مرورگر را تازه کنید.

<a id="مشارکت"></a>

## 🤝 مشارکت

برای تغییر، شاخه مستقل بسازید، رفتار فعلی را بررسی کنید و توضیح روشن همراه تغییر بفرستید. اطلاعات خصوصی، خروجی build و دیتابیس محلی را commit نکنید.

راهنماهای همراه:

- [DEPLOYMENT.md](DEPLOYMENT.md)
- [SECURITY.md](SECURITY.md)

<a id="مجوز"></a>

## 📄 مجوز

فایل مجوز در این نسخه موجود نیست. نمایش عمومی کد به‌تنهایی مجوز استفاده مجدد نیست؛ برای شرایط استفاده با مالک مخزن هماهنگ کنید.

---

ساخته‌شده در مجموعه **PIMX** · مستندات فارسی و انگلیسی.

---

<div align="center">

🛒 **COMMERCE · DJANGO** · [English](README.md) · [فارسی](README.fa.md)

</div>

</div>
