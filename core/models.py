from django.db import models

from .crypto import EncryptedCharField, EncryptedTextField

class TimeStampedModel(models.Model):
    """
    Abstract base model providing self-updating 'created_at' and 'updated_at' fields.
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بروزرسانی")

    class Meta:
        abstract = True


class SiteSetting(TimeStampedModel):
    """
    Global store settings, configurable by staff/superusers from the dashboard.
    """
    site_name = models.CharField(max_length=150, default="فروشگاه اینترنتی مدرن", verbose_name="نام فروشگاه")
    site_tagline = models.CharField(max_length=250, default="تجربه خریدی مطمئن، سریع و لذت‌بخش", verbose_name="شعار فروشگاه")
    logo = models.ImageField(upload_to="site/", null=True, blank=True, verbose_name="لوگوی فروشگاه")
    favicon = models.ImageField(upload_to="site/", null=True, blank=True, verbose_name="فاوآیکون")
    phone = models.CharField(max_length=30, default="021-88889999", verbose_name="شماره تماس پشتیبانی")
    email = models.EmailField(default="support@shop.local", verbose_name="ایمیل پشتیبانی")
    address = models.CharField(max_length=300, default="تهران، خیابان ولیعصر، برج فناوری، طبقه ۴", verbose_name="آدرس دفتر مرکزی")
    working_hours = models.CharField(max_length=100, default="شنبه تا چهارشنبه ۹ الی ۱۸ - پنجشنبه ۹ الی ۱۴", verbose_name="ساعات پاسخگویی")
    currency = models.CharField(max_length=20, default="تومان", verbose_name="واحد پول")
    free_shipping_threshold = models.DecimalField(max_digits=12, decimal_places=0, default=500000, verbose_name="حداقل خرید برای ارسال رایگان (تومان)")
    standard_shipping_cost = models.DecimalField(max_digits=12, decimal_places=0, default=45000, verbose_name="هزینه ارسال پیش‌فرض (تومان)")
    instagram_url = models.URLField(blank=True, default="https://instagram.com", verbose_name="لینک اینستاگرام")
    telegram_url = models.URLField(blank=True, default="https://t.me", verbose_name="لینک تلگرام")

    # Legal policies
    about_us = models.TextField(default="فروشگاه اینترنتی ما با هدف ارائه برترین محصولات با اصالت تضمین‌شده و بهترین قیمت آغاز به کار نموده است.", verbose_name="درباره ما")
    privacy_policy = models.TextField(default="ما به حریم خصوصی تمامی کاربران احترام می‌گذاریم و اطلاعات شما را با بالاترین استانداردهای امنیتی محافظت می‌کنیم.", verbose_name="سیاست حریم خصوصی")
    terms_and_conditions = models.TextField(default="استفاده از خدمات این فروشگاه به معنای پذیرش کامل قوانین و مقررات تجارت الکترونیک است.", verbose_name="قوانین و شرایط")
    shipping_policy = models.TextField(default="ارسال سفارشات تهران با پیک اکسپرس و شهرستان‌ها با پست پیشتاز و تیپاکس ظرف ۲۴ تا ۴۸ ساعت کاری انجام می‌پذیرد.", verbose_name="رویه ارسال")
    returns_policy = models.TextField(default="امکان مرجوعی کالا تا ۷ روز پس از تحویل در صورت عدم باز شدن پلمپ یا اشکال فنی کالا وجود دارد.", verbose_name="رویه مرجوعی کالا")
    cookie_policy = models.TextField(default="این وب‌سایت برای بهبود تجربه کاربری و حفظ وضعیت سبد خرید از کوکی‌های استاندارد استفاده می‌کند.", verbose_name="سیاست کوکی‌ها")

    class Meta:
        verbose_name = "تنظیمات سایت"
        verbose_name_plural = "تنظیمات سایت"

    def __str__(self):
        return self.site_name

    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(id=1)
        return obj


class Banner(TimeStampedModel):
    """
    Homepage and promotional banners managed dynamically via CMS.
    """
    POSITION_CHOICES = (
        ('hero', 'اسلایدر هیرو (بالای صفحه اصلی)'),
        ('middle_dual_1', 'بنر میانی دوتایی - سمت راست'),
        ('middle_dual_2', 'بنر میانی دوتایی - سمت چپ'),
        ('special_offer', 'بنر پیشنهاد ویژه عریض'),
        ('sidebar', 'بنر ستون کناری'),
    )

    title = models.CharField(max_length=200, verbose_name="عنوان بنر")
    subtitle = models.CharField(max_length=250, blank=True, verbose_name="زیرعنوان / توضیحات کوتاه")
    image = models.ImageField(upload_to="banners/", verbose_name="تصویر بنر")
    link_url = models.CharField(max_length=300, default="/shop/", verbose_name="آدرس لینک")
    position = models.CharField(max_length=30, choices=POSITION_CHOICES, default='hero', verbose_name="موقعیت نمایش")
    button_text = models.CharField(max_length=50, default="مشاهده و خرید", verbose_name="متن دکمه")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        verbose_name = "بنر و اسلایدر"
        verbose_name_plural = "بنرها و اسلایدرها"
        ordering = ['order', '-created_at']

    def __str__(self):
        return f"{self.get_position_display()} - {self.title}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        from core.images import compress_image_field
        compress_image_field(self.image)


class ContactMessage(TimeStampedModel):
    """
    Stores contact form submissions securely in database.
    """
    name = models.CharField(max_length=150, verbose_name="نام و نام خانوادگی")
    email = models.EmailField(verbose_name="ایمیل")
    phone = EncryptedCharField(max_length=500, blank=True, verbose_name="شماره تماس (رمزنگاری‌شده)")
    subject = models.CharField(max_length=200, verbose_name="موضوع پیام")
    message = EncryptedTextField(verbose_name="متن پیام (رمزنگاری‌شده)")
    is_read = models.BooleanField(default=False, verbose_name="خوانده شده")
    replied = models.BooleanField(default=False, verbose_name="پاسخ داده شده")

    class Meta:
        verbose_name = "پیام تماس با ما"
        verbose_name_plural = "پیام‌های تماس با ما"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.subject}"


class NewsletterSubscription(TimeStampedModel):
    """
    Tracks email newsletter subscribers.
    """
    email = models.EmailField(unique=True, verbose_name="ایمیل مشترک")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        verbose_name = "عضو خبرنامه"
        verbose_name_plural = "اعضای خبرنامه"
        ordering = ['-created_at']

    def __str__(self):
        return self.email
