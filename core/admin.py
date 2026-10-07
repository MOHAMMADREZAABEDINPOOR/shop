from django.contrib import admin
from django.utils.html import format_html, mark_safe

from core.admin_helpers import badge, thumbnail, yes_no
from .models import SiteSetting, Banner, ContactMessage, NewsletterSubscription


@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    list_display = ('site_name', 'phone', 'email', 'currency', 'free_shipping_threshold')


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('preview', 'title', 'position', 'order', 'status_badge', 'link_badge', 'created_at')
    list_filter = ('position', 'is_active')
    search_fields = ('title', 'subtitle', 'link_url')
    list_editable = ('order',)
    readonly_fields = ('preview',)

    @admin.display(description='تصویر')
    def preview(self, obj):
        return thumbnail(obj.image.url if obj.image else None, obj.title, size=72)

    @admin.display(description='وضعیت')
    def status_badge(self, obj):
        return yes_no(obj.is_active, yes='✓ نمایش داده می‌شود', no='✕ مخفی')

    @admin.display(description='لینک')
    def link_badge(self, obj):
        return badge('🔗 دارد', 'info') if obj.link_url else badge('بدون لینک', 'muted')


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('status_dot', 'name', 'email', 'phone_display', 'subject', 'read_badge', 'replied_badge', 'created_at')
    list_filter = ('is_read', 'replied', 'created_at')
    # NOTE: phone/message are encrypted at rest, so they are excluded from search.
    search_fields = ('name', 'email', 'subject')
    readonly_fields = ('created_at', 'updated_at', 'message_display')
    list_per_page = 25
    date_hierarchy = 'created_at'
    actions = ('mark_as_read', 'mark_as_unread', 'mark_as_replied')

    fieldsets = (
        ('👤 فرستنده', {
            'fields': ('name', 'email', 'phone'),
        }),
        ('💬 پیام', {
            'fields': ('subject', 'message_display', 'message'),
        }),
        ('📌 وضعیت پیگیری', {
            'fields': ('is_read', 'replied'),
        }),
    )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        # Unread messages float to the top for faster triage.
        return qs.order_by('is_read', '-created_at')

    @admin.display(description='')
    def status_dot(self, obj):
        if not obj.is_read:
            return mark_safe('<span class="adm-badge adm-warning">پیام جدید</span>')
        if not obj.replied:
            return badge('بی‌پاسخ', 'info')
        return badge('پاسخ‌داده‌شده', 'success')

    @admin.display(description='تماس')
    def phone_display(self, obj):
        return obj.phone or badge('—', 'muted')

    @admin.display(description='متن پیام (رمزگشایی‌شده)')
    def message_display(self, obj):
        return format_html(
            '<div class="adm-message-box">{}</div>',
            obj.message or ''
        )

    @admin.display(description='خوانده‌شده')
    def read_badge(self, obj):
        return yes_no(obj.is_read, yes='✓ خوانده', no='🔵 تازه', no_color='info')

    @admin.display(description='پاسخ')
    def replied_badge(self, obj):
        return yes_no(obj.replied, yes='✓ پاسخش داده شد', no='در انتظار پاسخ',
                      yes_color='success', no_color='info')

    @admin.action(description='✅ خوانده‌شده علامت‌زدن پیام‌ها')
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} پیام خوانده‌شده علامت خورد.', 'success')

    @admin.action(description='🔵 نخوانده علامت‌زدن پیام‌ها')
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f'{updated} پیام نخوانده علامت خورد.', 'info')

    @admin.action(description='✉️ پاسخ‌داده‌شده علامت‌زدن پیام‌ها')
    def mark_as_replied(self, request, queryset):
        updated = queryset.update(replied=True, is_read=True)
        self.message_user(request, f'{updated} پیام پاسخ‌داده‌شده علامت خورد.', 'success')


@admin.register(NewsletterSubscription)
class NewsletterSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('email', 'status_badge', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('email',)

    @admin.display(description='وضعیت')
    def status_badge(self, obj):
        return yes_no(obj.is_active, yes='✓ عضو فعال', no='✕ لغو کرده')
