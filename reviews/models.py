from django.db import models
from django.conf import settings
from core.models import TimeStampedModel

class Review(TimeStampedModel):
    """
    Customer product ratings and reviews with Verified Buyer validation.
    """
    RATING_CHOICES = (
        (1, '۱ ستاره - بسیار ضعیف'),
        (2, '۲ ستاره - ضعیف'),
        (3, '۳ ستاره - معمولی'),
        (4, '۴ ستاره - خوب'),
        (5, '۵ ستاره - عالی'),
    )

    product = models.ForeignKey('catalog.Product', on_delete=models.CASCADE, related_name='reviews', verbose_name="محصول")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews', verbose_name="کاربر")
    rating = models.PositiveSmallIntegerField(choices=RATING_CHOICES, default=5, verbose_name="امتیاز (۱ تا ۵)")
    title = models.CharField(max_length=150, verbose_name="عنوان دیدگاه")
    comment = models.TextField(verbose_name="متن دیدگاه")
    is_verified_buyer = models.BooleanField(default=False, verbose_name="خریدار تأیید شده")
    is_approved = models.BooleanField(default=True, verbose_name="تأیید شده برای انتشار")

    class Meta:
        verbose_name = "دیدگاه و امتیاز"
        verbose_name_plural = "دیدگاه‌ها و امتیازها"
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(fields=['product', 'user'], name='unique_user_product_review')
        ]

    def __str__(self):
        return f"{self.user} on {self.product.name} ({self.rating}★)"
