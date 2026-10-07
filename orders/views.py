import json
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from .models import Order, OrderItem, Coupon, CouponUsage
from accounts.models import Address
from cart.utils import get_or_create_cart
from catalog.models import Product, ProductVariant
from core.models import SiteSetting

@login_required
def checkout_view(request):
    """
    Multi-step checkout pipeline with atomic inventory locking and snapshot creation.
    """
    if request.user.is_staff:
        messages.info(request, "حساب‌های مدیریتی امکان ثبت سفارش ندارند؛ برای مدیریت از پنل مدیریت استفاده کنید.")
        return redirect('dashboard:overview')
    cart = get_or_create_cart(request)
    items = list(cart.get_items())

    if not items:
        lang = getattr(request, 'LANGUAGE_CODE', None) or 'fa'
        msg = "Your shopping cart is empty. Please add items to proceed." if lang == 'en' else "سبد خرید شما خالی است. ابتدا کالاهای مورد نظر خود را انتخاب کنید."
        messages.warning(request, msg)
        return redirect('catalog:shop')

    user = request.user
    addresses = user.addresses.all()
    default_address = addresses.filter(is_default=True).first() or addresses.first()
    site_settings = SiteSetting.get_settings()

    # Pre-calculate totals
    subtotal = cart.get_subtotal()
    shipping_cost = cart.get_shipping_cost()

    # Check coupon in session
    coupon_code = request.session.get('checkout_coupon_code')
    coupon = None
    discount_amount = Decimal('0')
    if coupon_code:
        coupon = Coupon.objects.filter(code=coupon_code, is_active=True).first()
        if coupon:
            is_valid, msg = coupon.is_valid(user, subtotal)
            if is_valid:
                discount_amount = coupon.calculate_discount(subtotal)
            else:
                del request.session['checkout_coupon_code']
                coupon = None

    grand_total = subtotal - discount_amount + shipping_cost
    if grand_total < 0:
        grand_total = Decimal('0')

    if request.method == 'POST':
        address_id = request.POST.get('address_id')
        shipping_method = request.POST.get('shipping_method', 'پست پیشتاز')
        customer_notes = request.POST.get('customer_notes', '').strip()

        # Validate Address
        if not address_id:
            messages.error(request, "لطفاً آدرس تحویل سفارش را انتخاب یا اضافه کنید.")
            return redirect('orders:checkout')

        address = get_object_or_404(Address, id=address_id, user=user)

        # ATOMIC CHECKOUT & INVENTORY LOCKING TO PREVENT RACE CONDITIONS & OVERSELLING
        try:
            with transaction.atomic():
                # Re-fetch and lock all products and variants in cart
                for item in items:
                    product = Product.objects.select_for_update().get(id=item.product.id)
                    if not product.is_active:
                        raise ValueError(f"کالای «{product.name}» دیگر فعال نیست.")

                    if item.variant:
                        variant = ProductVariant.objects.select_for_update().get(id=item.variant.id)
                        if not variant.is_active:
                            raise ValueError(f"تنوع انتخابی برای «{product.name}» فعال نیست.")
                        if variant.stock < item.quantity:
                            raise ValueError(
                                f"موجودی تنوع «{variant.name}» از محصول «{product.name}» کافی نیست (موجود: {variant.stock} عدد)."
                            )
                        # Decrement variant stock
                        variant.stock -= item.quantity
                        variant.save(update_fields=['stock'])
                    else:
                        if product.stock < item.quantity:
                            raise ValueError(
                                f"موجودی کالای «{product.name}» کافی نیست (موجودی فعلی: {product.stock} عدد)."
                            )
                        # Decrement product stock
                        product.stock -= item.quantity
                        product.save(update_fields=['stock'])

                # Create Order with snapshots
                order = Order.objects.create(
                    order_number=Order.generate_order_number(),
                    user=user,
                    # Address Snapshot
                    shipping_name=address.receiver_name,
                    shipping_phone=address.receiver_phone,
                    shipping_province=address.province,
                    shipping_city=address.city,
                    shipping_postal_code=address.postal_code,
                    shipping_address_line=address.address_line,
                    # Financial Snapshot
                    subtotal=subtotal,
                    discount_amount=discount_amount,
                    coupon=coupon,
                    shipping_cost=shipping_cost,
                    tax_amount=Decimal('0'),
                    grand_total=grand_total,
                    status=Order.OrderStatus.AWAITING_PAYMENT,
                    shipping_method=shipping_method,
                    customer_notes=customer_notes
                )

                # Record Coupon Usage
                if coupon:
                    CouponUsage.objects.create(
                        coupon=coupon,
                        user=user,
                        order=order
                    )
                    # Clear session coupon
                    if 'checkout_coupon_code' in request.session:
                        del request.session['checkout_coupon_code']

                # Create OrderItem Snapshots
                for item in items:
                    unit_price = item.get_unit_price()
                    total_price = unit_price * item.quantity
                    OrderItem.objects.create(
                        order=order,
                        product=item.product,
                        variant=item.variant,
                        product_name=item.product.name,
                        variant_name=item.variant.name if item.variant else "",
                        unit_price=unit_price,
                        quantity=item.quantity,
                        total_price=total_price
                    )

                # Clear Cart
                cart.items.all().delete()

            # Redirect to Payment Gateway initialization
            return redirect('payments:initiate', order_number=order.order_number)

        except ValueError as e:
            messages.error(request, str(e))
            return redirect('cart:detail')
        except Exception as e:
            messages.error(request, "خطایی در ثبت سفارش رخ داد. لطفاً مجدداً تلاش نمایید.")
            return redirect('orders:checkout')

    context = {
        'cart': cart,
        'items': items,
        'addresses': addresses,
        'default_address': default_address,
        'subtotal': subtotal,
        'discount_amount': discount_amount,
        'shipping_cost': shipping_cost,
        'grand_total': grand_total,
        'applied_coupon': coupon,
    }
    return render(request, 'orders/checkout.html', context)


@login_required
def apply_coupon_api(request):
    """
    AJAX endpoint to test and validate promotional coupons.
    """
    code = request.POST.get('code', '').strip().upper()
    if not code:
        return JsonResponse({'status': 'error', 'message': 'لطفاً کد تخفیف را وارد کنید.'}, status=400)

    cart = get_or_create_cart(request)
    subtotal = cart.get_subtotal()

    coupon = Coupon.objects.filter(code=code, is_active=True).first()
    if not coupon:
        return JsonResponse({'status': 'error', 'message': 'کد تخفیف وارد شده معتبر نیست.'}, status=400)

    is_valid, msg = coupon.is_valid(request.user, subtotal)
    if not is_valid:
        return JsonResponse({'status': 'error', 'message': msg}, status=400)

    discount = coupon.calculate_discount(subtotal)
    shipping = cart.get_shipping_cost()
    new_grand_total = max(Decimal('0'), subtotal - discount + shipping)

    request.session['checkout_coupon_code'] = coupon.code

    return JsonResponse({
        'status': 'success',
        'message': f"کد تخفیف «{coupon.code}» با موفقیت اعمال شد.",
        'discount_amount': f"{discount:,}",
        'new_grand_total': f"{new_grand_total:,}"
    })


@login_required
def remove_coupon_api(request):
    """
    Removes applied coupon from checkout session.
    """
    if 'checkout_coupon_code' in request.session:
        del request.session['checkout_coupon_code']
    return JsonResponse({'status': 'success', 'message': 'کد تخفیف حذف شد.'})


@login_required
def order_success_view(request, order_number):
    """
    Confirmed order summary page.
    """
    order = get_object_or_404(request.user.orders.prefetch_related('items', 'payments'), order_number=order_number)
    return render(request, 'orders/order_success.html', {'order': order})


@login_required
def order_cancel_view(request, order_number):
    """
    Cancels pending order and restores reserved inventory atomically.
    """
    order = get_object_or_404(request.user.orders, order_number=order_number)

    if not order.can_be_cancelled():
        messages.error(request, "این سفارش به دلیل تغییر وضعیت قابل لغو توسط خریدار نمی‌باشد.")
        return redirect('accounts:order_detail', order_number=order.order_number)

    with transaction.atomic():
        # Restore stock
        for item in order.items.all():
            if item.variant:
                variant = ProductVariant.objects.select_for_update().filter(id=item.variant.id).first()
                if variant:
                    variant.stock += item.quantity
                    variant.save(update_fields=['stock'])
            elif item.product:
                product = Product.objects.select_for_update().filter(id=item.product.id).first()
                if product:
                    product.stock += item.quantity
                    product.save(update_fields=['stock'])

        order.status = Order.OrderStatus.CANCELLED
        order.save(update_fields=['status', 'updated_at'])

    messages.info(request, f"سفارش {order.order_number} لغو گردید و موجودی کالاها به انبار بازگردانده شد.")
    return redirect('accounts:order_detail', order_number=order.order_number)
