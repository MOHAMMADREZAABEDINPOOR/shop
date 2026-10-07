"""Template tags powering the Avangard Admin dashboard quick-stats strip."""
from django import template

register = template.Library()


@register.simple_tag
def admin_quick_stats():
    from catalog.models import Product
    from core.models import ContactMessage
    from orders.models import Order
    from reviews.models import Review

    O = Order.OrderStatus
    return {
        'products': Product.objects.filter(is_active=True).count(),
        'orders_pending': Order.objects.filter(status__in=[O.PENDING, O.AWAITING_PAYMENT]).count(),
        'orders_processing': Order.objects.filter(status=O.PROCESSING).count(),
        'unread_messages': ContactMessage.objects.filter(is_read=False).count(),
        'pending_reviews': Review.objects.filter(is_approved=False).count(),
    }
