import uuid
from decimal import Decimal
from django.db import models
from django.conf import settings
from django.utils import timezone
from core.models import TimeStampedModel

class Coupon(TimeStampedModel):
    """
    Promotional discount coupon engine with validation rules and user usage limits.
    """
    class DiscountType(models.TextChoices):
        PERCENTAGE = 'PERCENTAGE', 'درصدی'
        FIXED = 'FIXED', 'مبلغ ثابت (تومان)'

    code = models.CharField(max_length=50, unique=True, db_index=True, verbose_name="کد تخفیف")
    discount_type = models.CharField(max_length=20, choices=DiscountType.choices, default=DiscountType.PERCENTAGE, verbose_name="نوع تخفیف")
    discount_value = models.DecimalField(max_digits=10, decimal_places=0, verbose_name="مقدار تخفیف (درصد یا تومان)")
    min_order_amount = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="حداقل مبلغ سفارش")
    max_discount_amount = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True, verbose_name="حداکثر سقف تخفیف (برای درصدی)")
    start_date = models.DateTimeField(default=timezone.now, verbose_name="تاریخ شروع اعتبار")
    end_date = models.DateTimeField(verbose_name="تاریخ پایان اعتبار")
    usage_limit = models.PositiveIntegerField(null=True, blank=True, verbose_name="حداکثر تعداد کل استفاده")
    usage_per_user = models.PositiveIntegerField(default=1, verbose_name="حداکثر دفعات استفاده برای هر کاربر")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        verbose_name = "کوپن تخفیف"
        verbose_name_plural = "کوپن‌های تخفیف"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code} ({self.get_discount_type_display()})"

    def clean(self):
        self.code = self.code.strip().upper()

    def is_valid(self, user, subtotal):
        """
        Server-side validation checking time, status, subtotal, and user usage history.
        """
        now = timezone.now()
        if not self.is_active:
            return False, "این کد تخفیف غیرفعال است."
        if now < self.start_date:
            return False, "زمان استفاده از این کد تخفیف هنوز شروع نشده است."
        if now > self.end_date:
            return False, "مهلت استفاده از این کد تخفیف به پایان رسیده است."
        if subtotal < self.min_order_amount:
            return False, f"حداقل مبلغ سفارش برای استفاده از این کد {self.min_order_amount:,} تومان است."
        if self.usage_limit:
            total_used = self.usages.count()
            if total_used >= self.usage_limit:
                return False, "ظرفیت استفاده از این کد تخفیف تکمیل شده است."
        if user and user.is_authenticated:
            user_used = self.usages.filter(user=user).count()
            if user_used >= self.usage_per_user:
                return False, "شما قبلاً از این کد تخفیف استفاده کرده‌اید."
        return True, "کد تخفیف معتبر است."

    def calculate_discount(self, subtotal):
        if self.discount_type == self.DiscountType.PERCENTAGE:
            discount = (subtotal * self.discount_value) / Decimal('100')
            if self.max_discount_amount and discount > self.max_discount_amount:
                discount = self.max_discount_amount
            return round(discount)
        else:
            return min(self.discount_value, subtotal)


class CouponUsage(models.Model):
    """
    Logs each coupon application to prevent abuse and enforce per-user limits.
    """
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name='usages', verbose_name="کوپن")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='coupon_usages', verbose_name="کاربر")
    order = models.ForeignKey('Order', on_delete=models.CASCADE, null=True, blank=True, related_name='coupon_usages', verbose_name="سفارش")
    used_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان استفاده")

    class Meta:
        verbose_name = "لاگ استفاده از کوپن"
        verbose_name_plural = "لاگ‌های استفاده از کوپن"
        ordering = ['-used_at']


class Order(TimeStampedModel):
    """
    Customer order with immutable snapshots of pricing, products, and shipping address.
    """
    class OrderStatus(models.TextChoices):
        PENDING = 'PENDING', 'در انتظار پرداخت'
        AWAITING_PAYMENT = 'AWAITING_PAYMENT', 'درگاه پرداخت'
        PAID = 'PAID', 'پرداخت شده و تایید شده'
        PROCESSING = 'PROCESSING', 'در حال آماده‌سازی و بسته‌بندی'
        SHIPPED = 'SHIPPED', 'تحویل به شرکت حمل و نقل'
        DELIVERED = 'DELIVERED', 'تحویل داده شده به مشتری'
        CANCELLED = 'CANCELLED', 'لغو شده'
        RETURNED = 'RETURNED', 'مرجوع شده'
        REFUNDED = 'REFUNDED', 'استرداد وجه انجام شد'

    order_number = models.CharField(max_length=60, unique=True, db_index=True, verbose_name="شماره سفارش")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name='orders', verbose_name="مشتری")

    # Shipping Address Snapshot
    shipping_name = models.CharField(max_length=150, verbose_name="نام گیرنده")
    shipping_phone = models.CharField(max_length=20, verbose_name="شماره تماس گیرنده")
    shipping_province = models.CharField(max_length=100, verbose_name="استان")
    shipping_city = models.CharField(max_length=100, verbose_name="شهر")
    shipping_postal_code = models.CharField(max_length=20, verbose_name="کد پستی")
    shipping_address_line = models.TextField(verbose_name="نشانی کامل پستی")

    # Financial Snapshot
    subtotal = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="جمع اقلام (تومان)")
    discount_amount = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="مبلغ تخفیف (تومان)")
    coupon = models.ForeignKey(Coupon, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders', verbose_name="کوپن استفاده شده")
    shipping_cost = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="هزینه ارسال (تومان)")
    tax_amount = models.DecimalField(max_digits=12, decimal_places=0, default=0, verbose_name="مالیات (تومان)")
    grand_total = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="مبلغ نهایی فاکتور (تومان)")

    # Status & Shipping
    status = models.CharField(max_length=30, choices=OrderStatus.choices, default=OrderStatus.PENDING, db_index=True, verbose_name="وضعیت سفارش")
    shipping_method = models.CharField(max_length=100, default="پست پیشتاز", verbose_name="روش ارسال")
    tracking_code = models.CharField(max_length=100, blank=True, verbose_name="کد رهگیری پستی")

    # Notes
    customer_notes = models.TextField(blank=True, verbose_name="یادداشت خریدار")
    admin_notes = models.TextField(blank=True, verbose_name="یادداشت‌های داخلی مدیر")

    class Meta:
        verbose_name = "سفارش"
        verbose_name_plural = "سفارش‌ها"
        ordering = ['-created_at']

    def __str__(self):
        return f"سفارش {self.order_number} - {self.user.get_full_name()} ({self.get_status_display()})"

    @classmethod
    def generate_order_number(cls):
        date_str = timezone.now().strftime('%Y%m%d')
        unique_id = uuid.uuid4().hex[:6].upper()
        return f"ORD-{date_str}-{unique_id}"

    def can_be_cancelled(self):
        return self.status in [self.OrderStatus.PENDING, self.OrderStatus.AWAITING_PAYMENT, self.OrderStatus.PAID]


class OrderItem(TimeStampedModel):
    """
    Snapshot of product line item at checkout time.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="سفارش")
    product = models.ForeignKey('catalog.Product', on_delete=models.SET_NULL, null=True, blank=True, related_name='order_items', verbose_name="محصول")
    variant = models.ForeignKey('catalog.ProductVariant', on_delete=models.SET_NULL, null=True, blank=True, related_name='order_items', verbose_name="تنوع محصول")

    # Product and Price Snapshot
    product_name = models.CharField(max_length=250, verbose_name="نام محصول در زمان خرید")
    variant_name = models.CharField(max_length=200, blank=True, verbose_name="عنوان تنوع در زمان خرید")
    unit_price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="قیمت واحد (تومان)")
    quantity = models.PositiveIntegerField(default=1, verbose_name="تعداد")
    total_price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="جمع سطر (تومان)")

    class Meta:
        verbose_name = "آیتم سفارش"
        verbose_name_plural = "آیتم‌های سفارش"
        ordering = ['id']

    def __str__(self):
        variant_info = f" ({self.variant_name})" if self.variant_name else ""
        return f"{self.product_name}{variant_info} x {self.quantity}"
