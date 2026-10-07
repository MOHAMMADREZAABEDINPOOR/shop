from .utils import get_or_create_cart

def cart_summary_context(request):
    """
    Exposes active cart summary and item count to header and mini-cart drawers.
    """
    try:
        cart = get_or_create_cart(request)
        item_count = cart.get_item_count()
        subtotal = cart.get_subtotal()
    except Exception:
        cart = None
        item_count = 0
        subtotal = 0

    return {
        'active_cart': cart,
        'cart_item_count': item_count,
        'cart_subtotal': subtotal,
    }
