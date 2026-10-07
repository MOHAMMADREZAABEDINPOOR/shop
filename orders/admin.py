from django.contrib import admin
from django.utils.html import format_html

from core.admin_helpers import badge, order_link, product_thumb, toman, yes_no
from .models import Order, OrderItem, Coupon, CouponUsage

# Color map for the Persian order status labels
STATUS_COLORS = {
    'PENDING': 'warning',
    'AWAITING_PAYMENT': 'warning',
    'PAID': 'info',
    'PROCESSING': 'info',
    'SHIPPED': 'purple',
    'DELIVERED': 'success',
    'CANCELLED': 'danger',
    'RETURNED': 'danger',
    'REFUNDED': 'muted',
}


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    fields = ('thumb', 'product_name', 'variant_name', 'unit_price', 'quantity', 'total_price')
    readonly_fields = ('thumb', 'product_name', 'variant_name', 'unit_price', 'quantity', 'total_price')

    @admin.display(description='تصویر')
    def thumb(self, obj):
        return product_thumb(obj.product if obj.product_id else None)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        'order_link_col', 'customer_col', 'shipping_phone', 'items_count',
        'grand_total_col', 'status_badge', 'shipping_method', 'created_at'
    )
    list_filter = ('status', 'shipping_method', 'created_at')
    search_fields = ('order_number', 'user__email', 'shipping_name', 'shipping_phone', 'tracking_code')
    readonly_fields = ('order_number', 'created_at', 'updated_at', 'items_summary')
    inlines = [OrderItemInline]
    ordering = ('-created_at',)
    list_per_page = 25
    list_select_related = ('user',)
    date_hierarchy = 'created_at'
    actions = ('mark_processing', 'mark_shipped', 'mark_delivered', 'mark_cancelled')

    fieldsets = (
        ('🧾 اطلاعات سفارش', {
            'fields': ('order_number', 'user', 'status', 'created_at'),
        }),
        ('🚚 گیرنده و ارسال', {
            'fields': ('shipping_name', 'shipping_phone', 'shipping_province', 'shipping_city',
                       'shipping_postal_code', 'shipping_address_line', 'shipping_method', 'tracking_code'),
        }),
        ('💰 مالی', {
            'fields': ('subtotal', 'discount_amount', 'coupon', 'shipping_cost', 'tax_amount', 'grand_total'),
        }),
        ('📝 یادداشت‌ها', {
            'fields': ('customer_notes', 'admin_notes'),
        }),
        ('📦 اقلام سفارش', {
            'fields': ('items_summary',),
            'classes': ('collapse',),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

    @admin.display(description='شماره سفارش')
    def order_link_col(self, obj):
        return order_link(obj)

    @admin.display(description='مشتری')
    def customer_col(self, obj):
        return format_html(
            '<strong>{}</strong><br><span style="color:#64748b;font-size:0.78rem;">{}</span>',
            obj.shipping_name, obj.user.email if obj.user_id else 'خرید مهمان'
        )

    @admin.display(description='اقلام', ordering='items__count')
    def items_count(self, obj):
        return badge(f'{obj.items.count()} قلم', 'muted')

    @admin.display(description='مبلغ کل (تومان)', ordering='grand_total')
    def grand_total_col(self, obj):
        return toman(obj.grand_total)

    @admin.display(description='وضعیت')
    def status_badge(self, obj):
        color = STATUS_COLORS.get(obj.status, 'muted')
        label = dict(obj._meta.get_field('status').choices).get(obj.status, obj.status)
        return badge(label, color)

    @admin.display(description='خلاصه اقلام')
    def items_summary(self, obj):
        rows = [
            f'• {item.product_name} × {item.quantity} — {int(item.total_price):,} تومان'
            for item in obj.items.select_related('product').all()
        ]
        return format_html('<div class="adm-message-box">{}</div>', '\n'.join(rows) or 'بدون اقلام')

    def _set_status(self, request, queryset, status, message, level):
        updated = queryset.update(status=status)
        self.message_user(request, f'{updated} سفارش به «{message}» تغییر وضعیت یافت.', level)

    @admin.action(description='🔄 تغییر وضعیت به «در حال آماده‌سازی»')
    def mark_processing(self, request, queryset):
        self._set_status(request, queryset, Order.OrderStatus.PROCESSING, 'در حال آماده‌سازی', 'info')

    @admin.action(description='🚚 تغییر وضعیت به «تحویل به شرکت حمل»')
    def mark_shipped(self, request, queryset):
        self._set_status(request, queryset, Order.OrderStatus.SHIPPED, 'تحویل به شرکت حمل و نقل', 'success')

    @admin.action(description='✅ تغییر وضعیت به «تحویل‌شده به مشتری»')
    def mark_delivered(self, request, queryset):
        self._set_status(request, queryset, Order.OrderStatus.DELIVERED, 'تحویل داده شده', 'success')

    @admin.action(description='❌ لغو سفارش')
    def mark_cancelled(self, request, queryset):
        self._set_status(request, queryset, Order.OrderStatus.CANCELLED, 'لغو شده', 'warning')


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_badge', 'min_order_amount', 'validity', 'usage_progress', 'status_badge')
    list_filter = ('is_active', 'discount_type')
    search_fields = ('code',)

    @admin.display(description='تخفیف')
    def discount_badge(self, obj):
        if obj.discount_type == Coupon.DiscountType.PERCENTAGE:
            return badge(f'{obj.discount_value}٪', 'purple')
        return badge(f'{int(obj.discount_value):,} تومان', 'purple')

    @admin.display(description='اعتبار')
    def validity(self, obj):
        return format_html(
            '<span class="adm-mono" style="font-size:0.78rem;">{} ← {}</span>',
            obj.start_date, obj.end_date
        )

    @admin.display(description='مصرف')
    def usage_progress(self, obj):
        used = obj.usages.count()
        limit = obj.usage_limit or '∞'
        color = 'danger' if obj.usage_limit and used >= obj.usage_limit else 'info'
        return badge(f'{used} / {limit}', color)

    @admin.display(description='وضعیت')
    def status_badge(self, obj):
        return yes_no(obj.is_active, yes='✓ فعال', no='✕ غیرفعال')


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = ('coupon_code', 'user', 'order_link_col', 'used_at')
    list_filter = ('used_at', 'coupon')
    list_select_related = ('coupon', 'order')

    @admin.display(description='کد تخفیف')
    def coupon_code(self, obj):
        return badge(obj.coupon.code, 'purple')

    @admin.display(description='سفارش')
    def order_link_col(self, obj):
        return order_link(obj.order)
