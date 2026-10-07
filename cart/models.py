from django.db import models
from django.conf import settings
from decimal import Decimal
from core.models import TimeStampedModel, SiteSetting

class Cart(TimeStampedModel):
    """
    Shopping cart instance supporting both authenticated users and guest sessions.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        null=True, blank=True, related_name='carts', verbose_name="کاربر"
    )
    session_key = models.CharField(
        max_length=40, null=True, blank=True, db_index=True, verbose_name="کلید سشن مهمان"
    )
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        verbose_name = "سبد خرید"
        verbose_name_plural = "سبدهای خرید"
        ordering = ['-updated_at']

    def __str__(self):
        owner = self.user.email if self.user else f"Guest ({self.session_key})"
        return f"Cart #{self.id} for {owner}"

    def get_items(self):
        return self.items.select_related('product', 'variant', 'product__category', 'product__brand').prefetch_related('product__images')

    def get_subtotal(self):
        """Authoritative subtotal from database prices."""
        total = Decimal('0')
        for item in self.get_items():
            total += item.get_total_price()
        return total

    def get_item_count(self):
        return sum(item.quantity for item in self.items.all())

    def get_shipping_cost(self):
        subtotal = self.get_subtotal()
        site_settings = SiteSetting.get_settings()
        if subtotal == 0:
            return Decimal('0')
        if subtotal >= site_settings.free_shipping_threshold:
            return Decimal('0')
        return site_settings.standard_shipping_cost

    def get_grand_total(self):
        return self.get_subtotal() + self.get_shipping_cost()

    def merge_with_user(self, user):
        """
        Merges guest cart items into the authenticated user's active cart upon login.
        """
        user_cart, _ = Cart.objects.get_or_create(user=user, is_active=True)
        for item in self.items.all():
            existing_item = user_cart.items.filter(
                product=item.product,
                variant=item.variant
            ).first()
            if existing_item:
                existing_item.quantity += item.quantity
                # Cap at stock limit
                max_stock = item.variant.stock if item.variant else item.product.stock
                if existing_item.quantity > max_stock:
                    existing_item.quantity = max_stock
                existing_item.save()
            else:
                item.cart = user_cart
                item.save()
        # Deactivate guest cart
        self.is_active = False
        self.save()
        return user_cart


class CartItem(TimeStampedModel):
    """
    Individual item line in a shopping cart.
    """
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name="سبد خرید")
    product = models.ForeignKey('catalog.Product', on_delete=models.CASCADE, related_name='cart_items', verbose_name="محصول")
    variant = models.ForeignKey('catalog.ProductVariant', on_delete=models.CASCADE, null=True, blank=True, related_name='cart_items', verbose_name="تنوع محصول")
    quantity = models.PositiveIntegerField(default=1, verbose_name="تعداد")

    class Meta:
        verbose_name = "آیتم سبد خرید"
        verbose_name_plural = "آیتم‌های سبد خرید"
        constraints = [
            models.UniqueConstraint(fields=['cart', 'product', 'variant'], name='unique_cart_product_variant')
        ]
        ordering = ['created_at']

    def __str__(self):
        variant_info = f" - {self.variant.name}" if self.variant else ""
        return f"{self.product.name}{variant_info} x {self.quantity}"

    def get_unit_price(self):
        """Server-side unit price resolution."""
        if self.variant:
            return self.variant.get_price()
        return self.product.get_effective_price()

    def get_total_price(self):
        return self.get_unit_price() * self.quantity

    def get_available_stock(self):
        if self.variant:
            return self.variant.stock
        return self.product.stock

    def is_stock_sufficient(self):
        return self.get_available_stock() >= self.quantity
