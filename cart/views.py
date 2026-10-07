import json
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import Cart, CartItem
from .utils import get_or_create_cart
from catalog.models import Product, ProductVariant

def cart_detail_view(request):
    """
    Full shopping cart review page with real-time stock checks and order totals.
    """
    cart = get_or_create_cart(request)
    items = cart.get_items()

    context = {
        'cart': cart,
        'items': items,
        'subtotal': cart.get_subtotal(),
        'shipping_cost': cart.get_shipping_cost(),
        'grand_total': cart.get_grand_total(),
        'item_count': cart.get_item_count(),
    }
    return render(request, 'cart/cart_detail.html', context)


@require_POST
def add_to_cart_api(request):
    """
    AJAX endpoint to add product or specific variant to cart with server-side stock enforcement.
    """
    try:
        data = json.loads(request.body)
    except Exception:
        data = request.POST

    product_id = data.get('product_id')
    variant_id = data.get('variant_id')
    try:
        quantity = int(data.get('quantity', 1))
    except (ValueError, TypeError):
        quantity = 1

    if quantity < 1:
        quantity = 1

    product = get_object_or_404(Product, id=product_id, is_active=True)
    variant = None
    if variant_id:
        variant = get_object_or_404(ProductVariant, id=variant_id, product=product, is_active=True)

    # Determine maximum stock available
    available_stock = variant.stock if variant else product.stock
    if available_stock <= 0:
        return JsonResponse({
            'status': 'error',
            'message': 'متأسفانه موجودی این کالا به اتمام رسیده است.'
        }, status=400)

    cart = get_or_create_cart(request)
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        variant=variant,
        defaults={'quantity': 0}
    )

    new_quantity = cart_item.quantity + quantity
    if new_quantity > available_stock:
        new_quantity = available_stock
        msg = f"حداکثر موجودی قابل سفارش ({available_stock} عدد) به سبد خرید افزوده شد."
    else:
        msg = "کالا با موفقیت به سبد خرید افزوده شد."

    cart_item.quantity = new_quantity
    cart_item.save()

    return JsonResponse({
        'status': 'success',
        'message': msg,
        'cart_item_count': cart.get_item_count(),
        'cart_subtotal': f"{cart.get_subtotal():,}",
        'cart_grand_total': f"{cart.get_grand_total():,}"
    })


@require_POST
def update_cart_item_api(request, item_id):
    """
    AJAX endpoint to increment, decrement, or adjust cart item quantity.
    """
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)

    try:
        data = json.loads(request.body)
    except Exception:
        data = request.POST

    action = data.get('action')
    available_stock = cart_item.get_available_stock()

    if action == 'increase':
        if cart_item.quantity < available_stock:
            cart_item.quantity += 1
            cart_item.save()
            msg = "تعداد افزایش یافت."
        else:
            return JsonResponse({
                'status': 'error',
                'message': f"امکان افزایش بیشتر وجود ندارد (موجودی انبار: {available_stock} عدد)"
            }, status=400)

    elif action == 'decrease':
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
            msg = "تعداد کاهش یافت."
        else:
            cart_item.delete()
            msg = "کالا از سبد خرید حذف شد."

    elif action == 'set':
        qty = int(data.get('quantity', 1))
        if qty <= 0:
            cart_item.delete()
            msg = "کالا از سبد خرید حذف شد."
        elif qty > available_stock:
            cart_item.quantity = available_stock
            cart_item.save()
            msg = f"تعداد به حداکثر موجودی ({available_stock}) تغییر یافت."
        else:
            cart_item.quantity = qty
            cart_item.save()
            msg = "تعداد به‌روزرسانی شد."

    # Return refreshed totals
    item_deleted = not CartItem.objects.filter(id=item_id).exists()
    return JsonResponse({
        'status': 'success',
        'message': msg,
        'item_deleted': item_deleted,
        'item_quantity': 0 if item_deleted else cart_item.quantity,
        'item_total': 0 if item_deleted else f"{cart_item.get_total_price():,}",
        'cart_item_count': cart.get_item_count(),
        'subtotal': f"{cart.get_subtotal():,}",
        'shipping_cost': f"{cart.get_shipping_cost():,}",
        'grand_total': f"{cart.get_grand_total():,}"
    })


@require_POST
def remove_cart_item_api(request, item_id):
    """
    AJAX endpoint to remove an item completely from the cart.
    """
    cart = get_or_create_cart(request)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    cart_item.delete()

    lang = getattr(request, 'LANGUAGE_CODE', None) or 'fa'
    from core.templatetags.shop_filters import toman
    msg = "Item removed from cart." if lang == 'en' else "کالا از سبد خرید حذف شد."

    return JsonResponse({
        'status': 'success',
        'message': msg,
        'cart_item_count': cart.get_item_count(),
        'subtotal': toman(cart.get_subtotal(), lang),
        'currency': "Toman" if lang == 'en' else "تومان",
        'shipping_cost': toman(cart.get_shipping_cost(), lang),
        'grand_total': toman(cart.get_grand_total(), lang)
    })


def mini_cart_api(request):
    """
    Returns active cart items JSON for the top navigation mini-cart drawer.
    """
    cart = get_or_create_cart(request)
    lang = getattr(request, 'LANGUAGE_CODE', None) or 'fa'
    from core.templatetags.shop_filters import tr_filter, toman

    currency = "Toman" if lang == 'en' else "تومان"
    items_data = []
    for item in cart.get_items():
        name = tr_filter(item.product.name, 'en') if lang == 'en' else item.product.name
        items_data.append({
            'id': item.id,
            'name': name,
            'variant': item.variant.name if item.variant else None,
            'image': item.product.get_primary_image(),
            'quantity': item.quantity,
            'unit_price': toman(item.get_unit_price(), lang),
            'total_price': toman(item.get_total_price(), lang),
            'url': item.product.get_absolute_url()
        })

    subtotal_val = cart.get_subtotal()
    return JsonResponse({
        'items': items_data,
        'item_count': cart.get_item_count(),
        'subtotal': toman(subtotal_val, lang),
        'currency': currency,
        'grand_total': toman(cart.get_grand_total(), lang)
    })

