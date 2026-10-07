from .models import Cart

def get_or_create_cart(request):
    """
    Retrieves or initializes the active cart for an authenticated user or guest session.
    """
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user, is_active=True)
        # Check if there is an orphaned guest cart to merge
        session_key = request.session.session_key
        if session_key:
            guest_cart = Cart.objects.filter(session_key=session_key, is_active=True, user__isnull=True).first()
            if guest_cart and guest_cart != cart:
                guest_cart.merge_with_user(request.user)
        return cart
    else:
        if not request.session.session_key:
            request.session.save()
        session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key, is_active=True, user__isnull=True)
        return cart
