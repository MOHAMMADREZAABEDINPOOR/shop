import uuid
from django.db import models
from django.utils import timezone
from core.models import TimeStampedModel

class Payment(TimeStampedModel):
    """
    Financial transaction log for order payments supporting sandbox and production gateways.
    """
    class PaymentStatus(models.TextChoices):
        PENDING = 'PENDING', 'در انتظار پرداخت'
        SUCCESSFUL = 'SUCCESSFUL', 'موفق و تایید شده'
        FAILED = 'FAILED', 'ناموفق با خطا'
        CANCELLED = 'CANCELLED', 'انصراف توسط خریدار'

    order = models.ForeignKey('orders.Order', on_delete=models.PROTECT, related_name='payments', verbose_name="سفارش")
    transaction_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, db_index=True, verbose_name="شناسه یکتای تراکنش")
    gateway = models.CharField(max_length=50, default='sandbox', verbose_name="درگاه پرداخت")
    amount = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="مبلغ تراکنش (تومان)")
    status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING, db_index=True, verbose_name="وضعیت پرداخت")

    # Gateway Response details
    tracking_number = models.CharField(max_length=100, blank=True, verbose_name="شماره پیگیری / مرجع بانکی (RRN)")
    card_pan_masked = models.CharField(max_length=30, blank=True, verbose_name="شماره کارت ماسک‌شده")
    error_message = models.TextField(blank=True, verbose_name="علت خطا یا پیام درگاه")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="آدرس IP کاربر")
    idempotency_key = models.CharField(max_length=100, unique=True, db_index=True, verbose_name="کلید عدم تکرار (Idempotency Key)")

    verified_at = models.DateTimeField(null=True, blank=True, verbose_name="زمان اعتبارسنجی نهایی")

    class Meta:
        verbose_name = "تراکنش مالی"
        verbose_name_plural = "تراکنش‌های مالی"
        ordering = ['-created_at']

    def __str__(self):
        return f"پرداخت {self.transaction_id} برای سفارش {self.order.order_number} ({self.get_status_display()})"

    def mark_successful(self, tracking_number, card_pan_masked=""):
        self.status = self.PaymentStatus.SUCCESSFUL
        self.tracking_number = tracking_number
        self.card_pan_masked = card_pan_masked
        self.verified_at = timezone.now()
        self.save(update_fields=['status', 'tracking_number', 'card_pan_masked', 'verified_at', 'updated_at'])

    def mark_failed(self, error_message):
        self.status = self.PaymentStatus.FAILED
        self.error_message = error_message
        self.save(update_fields=['status', 'error_message', 'updated_at'])

    def mark_cancelled(self):
        self.status = self.PaymentStatus.CANCELLED
        self.save(update_fields=['status', 'updated_at'])
