from django.contrib import admin
from django.utils.html import mark_safe

from core.admin_helpers import badge, stars, yes_no, product_thumb, toman
from .models import Review


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        'product_thumb', 'product_summary', 'rating_stars', 'title',
        'user_badge', 'buyer_badge', 'approval_badge', 'created_at'
    )
    list_filter = ('rating', 'is_verified_buyer', 'is_approved', 'created_at')
    search_fields = ('product__name', 'user__email', 'title', 'comment')
    actions = ['approve_reviews', 'disapprove_reviews']
    list_select_related = ('product', 'user')
    list_per_page = 25
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('🛍️ محصول و کاربر', {
            'fields': ('product', 'user', 'is_verified_buyer'),
        }),
        ('⭐ محتوای دیدگاه', {
            'fields': ('rating', 'title', 'comment'),
        }),
        ('🛡️ انتشار', {
            'fields': ('is_approved',),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product', 'user')

    @admin.display(description='محصول')
    def product_thumb(self, obj):
        return product_thumb(obj.product)

    @admin.display(description='دیدگاه')
    def product_summary(self, obj):
        return mark_safe(
            f'<strong>{obj.title or "بدون عنوان"}</strong>'
            f'<br><span style="color:#64748b;font-size:0.78rem;">{obj.product.name} — {obj.user}</span>'
        )

    @admin.display(description='امتیاز')
    def rating_stars(self, obj):
        return stars(obj.rating)

    @admin.display(description='کاربر')
    def user_badge(self, obj):
        return badge(obj.user.get_full_name() or obj.user.username, 'info')

    @admin.display(description='خریدار')
    def buyer_badge(self, obj):
        return yes_no(obj.is_verified_buyer, yes='✓ خریدار واقعی', no='❓ نامشخص',
                      yes_color='success', no_color='muted')

    @admin.display(description='انتشار')
    def approval_badge(self, obj):
        return yes_no(obj.is_approved, yes='✅ منتشرشده', no='⏳ در انتظار')

    @admin.action(description='✅ تأیید و انتشار دیدگاه‌های انتخاب‌شده')
    def approve_reviews(self, request, queryset):
        updated = queryset.update(is_approved=True)
        self.message_user(request, f'{updated} دیدگاه منتشر شد.', 'success')
    approve_reviews.short_description = "تأیید دیدگاه‌های انتخاب‌شده برای انتشار"

    @admin.action(description='⏳ در انتظار تأیید دیدگاه‌های انتخاب‌شده')
    def disapprove_reviews(self, request, queryset):
        updated = queryset.update(is_approved=False)
        self.message_user(request, f'{updated} دیدگاه از انتشار خارج شد.', 'warning')
    disapprove_reviews.short_description = "عدم تأیید دیدگاه‌های انتخاب‌شده"
