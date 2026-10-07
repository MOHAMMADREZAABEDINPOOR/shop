from django.contrib import admin
from django.utils.html import format_html

from core.admin_helpers import badge, order_link, toman
from .models import Payment

STATUS_COLORS = {
    'PENDING': 'warning',
    'SUCCESSFUL': 'success',
    'FAILED': 'danger',
    'CANCELLED': 'muted',
}


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'short_tx', 'order_link_col', 'amount_col', 'gateway_badge',
        'status_badge', 'tracking_number', 'verified_at', 'created_at'
    )
    list_filter = ('status', 'gateway', 'created_at')
    search_fields = ('transaction_id', 'tracking_number', 'order__order_number', 'card_pan_masked')
    readonly_fields = (
        'transaction_id', 'order', 'amount', 'gateway', 'idempotency_key',
        'status', 'tracking_number', 'card_pan_masked', 'error_message',
        'ip_address', 'created_at', 'verified_at',
    )
    ordering = ('-created_at',)
    list_per_page = 25
    list_select_related = ('order',)
    date_hierarchy = 'created_at'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order')

    @admin.display(description='شناسه تراکنش')
    def short_tx(self, obj):
        return format_html('<span class="adm-mono" style="font-size:0.78rem;">{}…</span>', str(obj.transaction_id)[:8])

    @admin.display(description='سفارش')
    def order_link_col(self, obj):
        return order_link(obj.order)

    @admin.display(description='مبلغ (تومان)', ordering='amount')
    def amount_col(self, obj):
        return toman(obj.amount)

    @admin.display(description='درگاه')
    def gateway_badge(self, obj):
        return badge(obj.get_gateway_display() if hasattr(obj, 'get_gateway_display') else obj.gateway,
                     'purple' if obj.gateway == 'zarinpal' else 'muted')

    @admin.display(description='وضعیت')
    def status_badge(self, obj):
        color = STATUS_COLORS.get(obj.status, 'muted')
        label = obj.get_status_display()
        return badge(label, color)
