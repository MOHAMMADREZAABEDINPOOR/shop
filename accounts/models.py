from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone
from core.models import TimeStampedModel

class UserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("ایمیل کاربر الزامی است.")
        email = self.normalize_email(email).lower()
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)
        extra_fields.setdefault('role', User.Role.SUPERADMIN)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom enterprise User model with role-based access control.
    """
    class Role(models.TextChoices):
        CUSTOMER = 'CUSTOMER', 'مشتری'
        STAFF = 'STAFF', 'کارمند'
        ADMIN = 'ADMIN', 'مدیر'
        SUPERADMIN = 'SUPERADMIN', 'مدیر ارشد'

    email = models.EmailField(unique=True, db_index=True, verbose_name="ایمیل")
    phone_number = models.CharField(max_length=20, unique=True, null=True, blank=True, verbose_name="شماره تماس")
    first_name = models.CharField(max_length=150, blank=True, verbose_name="نام")
    last_name = models.CharField(max_length=150, blank=True, verbose_name="نام خانوادگی")
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER, verbose_name="نقش کاربری")

    is_active = models.BooleanField(default=True, verbose_name="فعال")
    is_staff = models.BooleanField(default=False, verbose_name="دسترسی پرسنل")
    is_verified = models.BooleanField(default=False, verbose_name="ایمیل تأیید شده")
    verification_token = models.CharField(max_length=100, blank=True, verbose_name="توکن تأیید ایمیل")

    date_joined = models.DateTimeField(default=timezone.now, verbose_name="تاریخ عضویت")

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = "کاربر"
        verbose_name_plural = "کاربران"
        ordering = ['-date_joined']

    def __str__(self):
        full_name = self.get_full_name()
        return full_name if full_name else self.email

    def get_full_name(self):
        full = f"{self.first_name} {self.last_name}".strip()
        return full if full else self.email

    def get_short_name(self):
        return self.first_name if self.first_name else self.email

    def save(self, *args, **kwargs):
        # Synchronize Django is_staff flag with role
        if self.role in [self.Role.STAFF, self.Role.ADMIN, self.Role.SUPERADMIN]:
            self.is_staff = True
        if self.role == self.Role.SUPERADMIN:
            self.is_superuser = True
        super().save(*args, **kwargs)


class UserProfile(TimeStampedModel):
    """
    Extended user profile information.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile', verbose_name="کاربر")
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True, verbose_name="تصویر پروفایل")
    national_code = models.CharField(max_length=10, blank=True, verbose_name="کد ملی")
    birth_date = models.DateField(null=True, blank=True, verbose_name="تاریخ تولد")
    notify_email = models.BooleanField(default=True, verbose_name="اطلاع‌رسانی از طریق ایمیل")
    notify_sms = models.BooleanField(default=False, verbose_name="اطلاع‌رسانی از طریق پیامک")

    class Meta:
        verbose_name = "پروفایل کاربر"
        verbose_name_plural = "پروفایل‌های کاربران"

    def __str__(self):
        return f"پروفایل {self.user}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        from core.images import compress_image_field
        compress_image_field(self.avatar, max_size=(512, 512))


class Address(TimeStampedModel):
    """
    User delivery addresses with default selection.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses', verbose_name="کاربر")
    title = models.CharField(max_length=100, default="منزل", verbose_name="عنوان آدرس (مثلاً منزل، محل کار)")
    receiver_name = models.CharField(max_length=150, verbose_name="نام تحویل‌گیرنده")
    receiver_phone = models.CharField(max_length=20, verbose_name="شماره تماس تحویل‌گیرنده")
    province = models.CharField(max_length=100, verbose_name="استان")
    city = models.CharField(max_length=100, verbose_name="شهر")
    postal_code = models.CharField(max_length=20, verbose_name="کد پستی ۱۰ رقمی")
    address_line = models.TextField(verbose_name="نشانی پستی کامل")
    is_default = models.BooleanField(default=False, verbose_name="آدرس پیش‌فرض")

    class Meta:
        verbose_name = "آدرس پستی"
        verbose_name_plural = "آدرس‌های پستی"
        ordering = ['-is_default', '-created_at']

    def __str__(self):
        return f"{self.title}: {self.province}، {self.city} - {self.receiver_name}"

    def save(self, *args, **kwargs):
        # Ensure only one address is default per user
        if self.is_default:
            Address.objects.filter(user=self.user, is_default=True).exclude(id=self.id).update(is_default=False)
        elif not Address.objects.filter(user=self.user, is_default=True).exists():
            self.is_default = True
        super().save(*args, **kwargs)


class Wishlist(TimeStampedModel):
    """
    User wishlist items.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_items', verbose_name="کاربر")
    product = models.ForeignKey('catalog.Product', on_delete=models.CASCADE, related_name='wishlisted_by', verbose_name="محصول")

    class Meta:
        verbose_name = "علاقه‌مندی"
        verbose_name_plural = "لیست علاقه‌مندی‌ها"
        constraints = [
            models.UniqueConstraint(fields=['user', 'product'], name='unique_user_product_wishlist')
        ]
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user} -> {self.product}"


class RecentlyViewed(models.Model):
    """
    Tracks recently viewed products per user or guest session.
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='recently_viewed', verbose_name="کاربر")
    session_key = models.CharField(max_length=40, null=True, blank=True, db_index=True, verbose_name="شناسه سشن مهمان")
    product = models.ForeignKey('catalog.Product', on_delete=models.CASCADE, related_name='view_history', verbose_name="محصول")
    viewed_at = models.DateTimeField(auto_now=True, verbose_name="تاریخ بازدید")

    class Meta:
        verbose_name = "بازدید اخیر"
        verbose_name_plural = "بازدیدهای اخیر"
        ordering = ['-viewed_at']

    def __str__(self):
        return f"View: {self.product} at {self.viewed_at}"
