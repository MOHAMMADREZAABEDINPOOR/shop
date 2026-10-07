from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from core.admin_helpers import badge, yes_no, thumbnail, toman
from .models import (
    Category, Brand, Product, ProductImage, ProductVariant,
    ProductAttribute, ProductAttributeValue, ProductSpecification
)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('preview', 'image', 'alt_text', 'is_feature', 'order')
    readonly_fields = ('preview',)

    @admin.display(description='پیش‌نمایش')
    def preview(self, obj):
        return thumbnail(obj.image.url if obj.image else None, obj.alt_text)


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ('name', 'sku', 'price_override', 'stock', 'is_active', 'admin_preview')
    readonly_fields = ('admin_preview',)

    @admin.display(description='وضعیت')
    def admin_preview(self, obj):
        if not obj.pk:
            return '—'
        color = 'success' if obj.stock > 0 else 'danger'
        return badge(f"موجودی: {obj.stock}", color)


class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'slug', 'order', 'status_badge')
    list_filter = ('is_active', 'parent')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'slug')

    @admin.display(description='وضعیت')
    def status_badge(self, obj):
        return yes_no(obj.is_active)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('logo_preview', 'name', 'slug', 'status_badge')
    list_filter = ('is_active',)
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

    @admin.display(description='لوگو')
    def logo_preview(self, obj):
        return thumbnail(obj.logo.url if obj.logo else None, obj.name, size=38)

    @admin.display(description='وضعیت')
    def status_badge(self, obj):
        return yes_no(obj.is_active)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'thumb', 'name', 'sku', 'category', 'price_display',
        'stock_badge', 'status_badge', 'marketing_badges'
    )
    list_filter = ('is_active', 'is_available', 'is_featured', 'is_bestseller', 'category', 'brand')
    search_fields = ('name', 'sku', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductVariantInline, ProductSpecificationInline]
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    list_per_page = 25
    list_select_related = ('category', 'brand')
    actions = ('activate_products', 'deactivate_products', 'mark_featured', 'mark_bestseller')

    fieldsets = (
        ('📦 اطلاعات اصلی محصول', {
            'fields': ('name', 'slug', 'sku', 'barcode', 'category', 'brand'),
        }),
        ('💰 قیمت‌گذاری', {
            'fields': ('base_price', 'sale_price', 'discount_percent'),
            'description': 'در صورت کمتر بودن قیمت فروش از قیمت پایه، تخفیف خودکار محاسبه می‌شود.',
        }),
        ('🏬 موجودی و وضعیت', {
            'fields': ('stock', 'is_available', 'is_active'),
        }),
        ('🎯 بازاریابی و نشان‌ها', {
            'fields': ('is_featured', 'is_bestseller', 'is_new_arrival'),
            'classes': ('collapse',),
        }),
        ('📝 توضیحات', {
            'fields': ('short_description', 'description'),
        }),
        ('🔎 سئو (SEO)', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',),
        }),
        ('⚖️ فیزیکی', {
            'fields': ('weight', 'dimensions'),
            'classes': ('collapse',),
        }),
    )

    # ---- Beautiful list columns ----
    @admin.display(description='تصویر')
    def thumb(self, obj):
        return thumbnail(obj.get_primary_image(), obj.name)

    @admin.display(description='قیمت (تومان)')
    def price_display(self, obj):
        if obj.has_discount():
            return format_html(
                '<span style="text-decoration:line-through;color:#94a3b8;font-size:0.78rem;">{}</span><br>{} {}',
                toman(obj.base_price),
                toman(obj.sale_price),
                badge(f'{obj.calculate_discount_percent()}٪ تخفیف', 'danger')
            )
        return toman(obj.base_price)

    @admin.display(description='موجودی')
    def stock_badge(self, obj):
        if not obj.is_in_stock():
            return badge('ناموجود', 'danger')
        if obj.stock <= 5:
            return badge(f'⚠ فقط {obj.stock}', 'warning')
        return badge(f'✓ {obj.stock} عدد', 'success')

    @admin.display(description='وضعیت سایت')
    def status_badge(self, obj):
        return yes_no(obj.is_active, yes='✓ منتشر', no='✕ مخفی')

    @admin.display(description='بازاریابی')
    def marketing_badges(self, obj):
        out = []
        if obj.is_featured:
            out.append(badge('⭐ ویژه', 'info'))
        if obj.is_bestseller:
            out.append(badge('🔥 پرفروش', 'warning'))
        if obj.is_new_arrival:
            out.append(badge('✨ جدید', 'purple'))
        return mark_safe(' '.join(out)) if out else badge('—', 'muted')

    # ---- Bulk actions ----
    @admin.action(description='✅ فعال کردن محصولات انتخاب‌شده')
    def activate_products(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} محصول فعال شد.', 'success')

    @admin.action(description='🚫 غیرفعال کردن محصولات انتخاب‌شده')
    def deactivate_products(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} محصول غیرفعال شد.', 'warning')

    @admin.action(description='⭐ نشانیدن به‌عنوان پیشنهاد ویژه')
    def mark_featured(self, request, queryset):
        updated = queryset.update(is_featured=True)
        self.message_user(request, f'{updated} محصول به پیشنهاد ویژه تبدیل شد.', 'success')

    @admin.action(description='🔥 نشانیدن به‌عنوان پرفروش‌ترین')
    def mark_bestseller(self, request, queryset):
        updated = queryset.update(is_bestseller=True)
        self.message_user(request, f'{updated} محصول به پرفروش‌ترین تبدیل شد.', 'success')


@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('product', 'name', 'sku', 'price_override', 'stock', 'is_active')
    list_filter = ('is_active', 'product')
    search_fields = ('name', 'sku', 'product__name')


@admin.register(ProductAttribute)
class ProductAttributeAdmin(admin.ModelAdmin):
    list_display = ('name', 'values_count')
    search_fields = ('name',)

    @admin.display(description='تعداد مقادیر')
    def values_count(self, obj):
        return badge(f'{obj.values.count()} مقدار', 'info')


@admin.register(ProductAttributeValue)
class ProductAttributeValueAdmin(admin.ModelAdmin):
    list_display = ('attribute', 'value', 'color_swatch')
    list_filter = ('attribute',)
    search_fields = ('value',)

    @admin.display(description='نمونه رنگ')
    def color_swatch(self, obj):
        if obj.color_code:
            return format_html(
                '<span style="display:inline-block;width:26px;height:26px;border-radius:8px;background:{};border:1px solid #cbd5e1;vertical-align:middle;"></span> <span class="adm-mono">{}</span>',
                obj.color_code, obj.color_code
            )
        return badge('—', 'muted')


@admin.register(ProductSpecification)
class ProductSpecificationAdmin(admin.ModelAdmin):
    list_display = ('product', 'key', 'value')
    list_filter = ('product__category',)
    search_fields = ('key', 'value', 'product__name')
