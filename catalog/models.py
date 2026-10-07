from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from core.models import TimeStampedModel

class Category(TimeStampedModel):
    """
    Multi-level hierarchical product categories.
    """
    name = models.CharField(max_length=150, verbose_name="نام دسته‌بندی")
    slug = models.SlugField(max_length=170, unique=True, allow_unicode=True, verbose_name="اسلاگ (URL)")
    parent = models.ForeignKey(
        'self', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='children', verbose_name="دسته‌بندی والد"
    )
    icon = models.CharField(max_length=100, blank=True, verbose_name="کلاس آیکون یا کاراکتر SVG")
    image = models.ImageField(upload_to="categories/", null=True, blank=True, verbose_name="تصویر دسته‌بندی")
    description = models.TextField(blank=True, verbose_name="توضیحات")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    # SEO
    meta_title = models.CharField(max_length=200, blank=True, verbose_name="عنوان سئو (Title)")
    meta_description = models.TextField(blank=True, verbose_name="توضیحات سئو (Meta Description)")

    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"
        ordering = ['order', 'name']

    def __str__(self):
        if self.parent:
            return f"{self.parent} -> {self.name}"
        return self.name

    def get_absolute_url(self):
        return reverse('catalog:category_detail', kwargs={'slug': self.slug})

    def get_all_subcategories(self):
        """Recursively get all descendant categories."""
        descendants = []
        for child in self.children.filter(is_active=True):
            descendants.append(child)
            descendants.extend(child.get_all_subcategories())
        return descendants


class Brand(TimeStampedModel):
    """
    Product manufacturers / brands.
    """
    name = models.CharField(max_length=150, verbose_name="نام برند")
    slug = models.SlugField(max_length=170, unique=True, allow_unicode=True, verbose_name="اسلاگ")
    logo = models.ImageField(upload_to="brands/", null=True, blank=True, verbose_name="لوگوی برند")
    description = models.TextField(blank=True, verbose_name="درباره برند")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        verbose_name = "برند"
        verbose_name_plural = "برندها"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('catalog:brand_detail', kwargs={'slug': self.slug})


class Product(TimeStampedModel):
    """
    E-Commerce Product supporting simple items and variable variant parents.
    """
    name = models.CharField(max_length=250, verbose_name="نام محصول")
    slug = models.SlugField(max_length=270, unique=True, allow_unicode=True, verbose_name="اسلاگ محصول")
    sku = models.CharField(max_length=60, unique=True, db_index=True, verbose_name="شناسه کالا (SKU)")
    barcode = models.CharField(max_length=60, blank=True, verbose_name="بارکد کالا")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name="دسته‌بندی")
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, blank=True, related_name='products', verbose_name="برند")

    short_description = models.CharField(max_length=500, blank=True, verbose_name="توضیح کوتاه")
    description = models.TextField(verbose_name="توضیحات کامل و بررسی محصول")

    base_price = models.DecimalField(max_digits=12, decimal_places=0, verbose_name="قیمت پایه (تومان)")
    sale_price = models.DecimalField(max_digits=12, decimal_places=0, null=True, blank=True, verbose_name="قیمت با تخفیف (تومان)")
    discount_percent = models.PositiveIntegerField(default=0, verbose_name="درصد تخفیف")

    stock = models.PositiveIntegerField(default=0, verbose_name="موجودی انبار")
    is_available = models.BooleanField(default=True, verbose_name="در دسترس")
    is_active = models.BooleanField(default=True, verbose_name="فعال در سایت")

    # Marketing Badges
    is_featured = models.BooleanField(default=False, verbose_name="پیشنهاد ویژه")
    is_bestseller = models.BooleanField(default=False, verbose_name="پرفروش‌ترین")
    is_new_arrival = models.BooleanField(default=False, verbose_name="جدیدترین")

    # Physical Attributes
    weight = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True, verbose_name="وزن (گرم/کیلوگرم)")
    dimensions = models.CharField(max_length=100, blank=True, verbose_name="ابعاد (طول x عرض x ارتفاع)")

    # SEO
    meta_title = models.CharField(max_length=200, blank=True, verbose_name="عنوان سئو")
    meta_description = models.TextField(blank=True, verbose_name="توضیحات متا سئو")

    class Meta:
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['sku']),
            models.Index(fields=['is_active', 'is_available']),
        ]

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('catalog:product_detail', kwargs={'slug': self.slug})

    def get_effective_price(self):
        """Authoritative current unit price."""
        if self.sale_price and self.sale_price < self.base_price:
            return self.sale_price
        return self.base_price

    def has_discount(self):
        return bool(self.sale_price and self.sale_price < self.base_price)

    def calculate_discount_percent(self):
        if self.has_discount() and self.base_price > 0:
            diff = self.base_price - self.sale_price
            return int((diff / self.base_price) * 100)
        return 0

    def is_in_stock(self):
        if self.has_variants():
            return any(v.stock > 0 for v in self.variants.filter(is_active=True))
        return self.is_available and self.stock > 0

    def has_variants(self):
        return self.variants.filter(is_active=True).exists()

    def get_primary_image(self):
        featured = self.images.filter(is_feature=True).first()
        if featured:
            return featured.image.url
        first = self.images.first()
        return first.image.url if first else '/static/images/placeholder.svg'

    def get_average_rating(self):
        from reviews.models import Review
        reviews = Review.objects.filter(product=self, is_approved=True)
        if not reviews.exists():
            return 0
        total = sum(r.rating for r in reviews)
        return round(total / reviews.count(), 1)

    def get_review_count(self):
        from reviews.models import Review
        return Review.objects.filter(product=self, is_approved=True).count()


    @property
    def is_newly_added(self):
        from datetime import timedelta
        from django.utils import timezone
        if not self.created_at:
            return False
        return (timezone.now() - self.created_at) <= timedelta(days=7)

    def marketing_badges(self):
        badges = []
        if self.is_bestseller:
            badges.append(("bestseller", "پرفروش"))
        if self.is_featured:
            badges.append(("featured", "ویژه"))
        if self.is_new_arrival or self.is_newly_added:
            badges.append(("new", "جدید"))
        return badges

class ProductImage(TimeStampedModel):
    """
    Multiple high-resolution images for each product.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images', verbose_name="محصول")
    image = models.ImageField(upload_to="products/", verbose_name="فایل تصویر")
    alt_text = models.CharField(max_length=200, blank=True, verbose_name="متن جایگزین (Alt Text)")
    is_feature = models.BooleanField(default=False, verbose_name="تصویر اصلی / کاور")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        verbose_name = "تصویر محصول"
        verbose_name_plural = "تصاویر محصول"
        ordering = ['order', '-is_feature', 'id']

    def __str__(self):
        return f"Image for {self.product.name}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        from core.images import compress_image_field
        compress_image_field(self.image)


class ProductAttribute(TimeStampedModel):
    """
    Technical attribute definition (e.g. Color, RAM, Storage).
    """
    name = models.CharField(max_length=100, unique=True, verbose_name="نام ویژگی (مثلاً رنگ، ظرفیت)")

    class Meta:
        verbose_name = "ویژگی کالا"
        verbose_name_plural = "ویژگی‌های کالا"

    def __str__(self):
        return self.name


class ProductAttributeValue(TimeStampedModel):
    """
    Value for an attribute (e.g. 128GB, Deep Purple, XL).
    """
    attribute = models.ForeignKey(ProductAttribute, on_delete=models.CASCADE, related_name='values', verbose_name="ویژگی")
    value = models.CharField(max_length=150, verbose_name="مقدار ویژگی")
    color_code = models.CharField(max_length=20, blank=True, verbose_name="کد رنگ هگز (مثلاً #FF0000 برای رنگ‌ها)")

    class Meta:
        verbose_name = "مقدار ویژگی"
        verbose_name_plural = "مقادیر ویژگی‌ها"
        unique_together = ('attribute', 'value')

    def __str__(self):
        return f"{self.attribute.name}: {self.value}"


class ProductVariant(TimeStampedModel):
    """
    Distinct SKU variant of a product (e.g. 128GB Black vs 256GB Silver) with independent price & stock.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants', verbose_name="محصول مرجع")
    name = models.CharField(max_length=200, verbose_name="عنوان تنوع (مثلاً رنگ مشکی - حافظه ۲۵۶ گیگابایت)")
    sku = models.CharField(max_length=80, unique=True, db_index=True, verbose_name="شناسه اختصاصی (SKU)")
    price_override = models.DecimalField(
        max_digits=12, decimal_places=0, null=True, blank=True,
        verbose_name="قیمت اختصاصی تنوع (در صورت خالی بودن، قیمت پایه محصول اعمال می‌شود)"
    )
    stock = models.PositiveIntegerField(default=0, verbose_name="موجودی این تنوع")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    attribute_values = models.ManyToManyField(ProductAttributeValue, blank=True, related_name='variants', verbose_name="مقادیر ویژگی‌ها")

    class Meta:
        verbose_name = "تنوع محصول (Variant)"
        verbose_name_plural = "تنوع‌های محصولات"
        ordering = ['id']

    def __str__(self):
        return f"{self.product.name} ({self.name})"

    def get_price(self):
        if self.price_override is not None:
            return self.price_override
        return self.product.get_effective_price()

    def is_in_stock(self):
        return self.is_active and self.stock > 0


class ProductSpecification(TimeStampedModel):
    """
    Detailed key-value technical specs displayed in product tables.
    """
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='specifications', verbose_name="محصول")
    key = models.CharField(max_length=150, verbose_name="عنوان مشخصه (مثلاً نوع پردازنده)")
    value = models.CharField(max_length=300, verbose_name="مقدار مشخصه")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        verbose_name = "مشخصه فنی محصول"
        verbose_name_plural = "مشخصات فنی محصول"
        ordering = ['order', 'id']

    def __str__(self):
        return f"{self.key}: {self.value}"
