from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from core.admin_helpers import badge, yes_no
from .models import User, UserProfile, Address, Wishlist, RecentlyViewed

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'اطلاعات تکمیلی پروفایل'

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    list_display = ('email', 'full_name', 'phone_number', 'role_badge', 'staff_badge', 'verified_badge', 'active_badge', 'date_joined')
    list_filter = ('role', 'is_staff', 'is_superuser', 'is_verified', 'is_active')
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('اطلاعات فردی', {'fields': ('first_name', 'last_name', 'phone_number')}),
        ('نقش و دسترسی‌ها', {'fields': ('role', 'is_active', 'is_staff', 'is_superuser', 'is_verified', 'groups', 'user_permissions')}),
        ('تاریخ‌ها', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'password', 'role'),
        }),
    )
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')
    ordering = ('-date_joined',)
    list_per_page = 25

    @admin.display(description='نام')
    def full_name(self, obj):
        return f'{obj.first_name} {obj.last_name}'.strip() or badge('بی‌نام', 'muted')

    @admin.display(description='نقش')
    def role_badge(self, obj):
        color = 'purple' if obj.is_superuser else ('info' if obj.is_staff else 'muted')
        label = obj.get_role_display() if hasattr(obj, 'get_role_display') else obj.role
        return badge(label, color)

    @admin.display(description='کادر')
    def staff_badge(self, obj):
        return yes_no(obj.is_staff, yes='✓ کادر', no='کاربر عادی', no_color='muted')

    @admin.display(description='احراز هویت')
    def verified_badge(self, obj):
        return yes_no(obj.is_verified, yes='✓ احرازشده', no='⏳ تأییدنشده')

    @admin.display(description='وضعیت')
    def active_badge(self, obj):
        return yes_no(obj.is_active, yes='✓ فعال', no='🚫 مسدود')

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'receiver_name', 'receiver_phone', 'province', 'city', 'default_badge')
    list_filter = ('province', 'is_default')
    search_fields = ('user__email', 'receiver_name', 'receiver_phone', 'postal_code')

    @admin.display(description='پیش‌فرض')
    def default_badge(self, obj):
        return yes_no(obj.is_default, yes='📌 پیش‌فرض', no='—', yes_color='info', no_color='muted')

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')
    search_fields = ('user__email', 'product__name')

@admin.register(RecentlyViewed)
class RecentlyViewedAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'session_key', 'viewed_at')
    ordering = ('-viewed_at',)
