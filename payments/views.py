import uuid
from decimal import Decimal
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from .models import Payment
from .gateways import get_payment_gateway
from orders.models import Order
from catalog.models import Product, ProductVariant

@login_required
def initiate_payment_view(request, order_number):
    """
    Initializes payment for an order and forwards customer to the configured payment gateway.
    """
    order = get_object_or_404(request.user.orders, order_number=order_number)

    if order.status not in [Order.OrderStatus.PENDING, Order.OrderStatus.AWAITING_PAYMENT]:
        messages.warning(request, f"این سفارش قبلاً تعیین وضعیت شده است ({order.get_status_display()}).")
        return redirect('accounts:order_detail', order_number=order.order_number)

    gateway = get_payment_gateway()
    redirect_url, payment = gateway.initiate_payment(order, request)
    return redirect(redirect_url)


def sandbox_gateway_view(request, transaction_id):
    """
    Simulates a secure banking portal (Shetab / Shaparak style) with interactive cards and buttons.
    """
    payment = get_object_or_404(Payment.objects.select_related('order', 'order__user'), transaction_id=transaction_id)

    if payment.status != Payment.PaymentStatus.PENDING:
        return redirect('payments:result', transaction_id=payment.transaction_id)

    context = {
        'payment': payment,
        'order': payment.order,
        'amount': payment.amount,
    }
    return render(request, 'payments/sandbox_gateway.html', context)


@csrf_exempt
def verify_payment_view(request, transaction_id):
    """
    Server-side idempotent verification callback.
    Guarantees that repeated callbacks do not trigger duplicate state updates or overselling.
    """
    simulated_action = request.POST.get('action', 'success')
    card_pan = request.POST.get('card_number', '6037-9918-****-4219')
    card_pan_masked = card_pan[-8:] if len(card_pan) >= 8 else "****-****"

    with transaction.atomic():
        # Lock payment record to enforce strict idempotency
        payment = Payment.objects.select_for_update().select_related('order', 'order__user').filter(transaction_id=transaction_id).first()
        if not payment:
            messages.error(request, "تراکنش مالی یافت نشد.")
            return redirect('core:home')

        # IDEMPOTENCY CHECK: If already finalized, do not re-execute!
        if payment.status == Payment.PaymentStatus.SUCCESSFUL:
            return redirect('payments:result', transaction_id=payment.transaction_id)

        order = payment.order

        if simulated_action == 'success':
            tracking_number = f"TRX-{uuid.uuid4().hex[:10].upper()}"
            payment.mark_successful(
                tracking_number=tracking_number,
                card_pan_masked=f"****-****-****-{card_pan_masked[-4:]}"
            )
            order.status = Order.OrderStatus.PAID
            order.save(update_fields=['status', 'updated_at'])

            # Send order confirmation email
            subject = f"تأیید پرداخت و ثبت سفارش {order.order_number}"
            body = (
                f"مشتری گرامی {order.shipping_name}،\n\n"
                f"پرداخت شما به مبلغ {order.grand_total:,} تومان با موفقیت انجام شد.\n"
                f"شماره سفارش: {order.order_number}\n"
                f"شماره پیگیری بانکی: {tracking_number}\n\n"
                f"سفارش شما در حال آماده‌سازی و پردازش در انبار است.\n"
                f"با تشکر از خرید شما."
            )
            try:
                send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [order.user.email], fail_silently=True)
            except Exception:
                pass

        elif simulated_action == 'cancel':
            payment.mark_cancelled()
            order.status = Order.OrderStatus.CANCELLED
            order.save(update_fields=['status', 'updated_at'])

            # Restore reserved inventory
            for item in order.items.all():
                if item.variant:
                    v = ProductVariant.objects.select_for_update().filter(id=item.variant.id).first()
                    if v:
                        v.stock += item.quantity
                        v.save(update_fields=['stock'])
                elif item.product:
                    p = Product.objects.select_for_update().filter(id=item.product.id).first()
                    if p:
                        p.stock += item.quantity
                        p.save(update_fields=['stock'])

        else:  # fail / error
            error_msg = "رمز اینترنتی نامعتبر است یا موجودی حساب کافی نمی‌باشد."
            payment.mark_failed(error_msg)
            order.status = Order.OrderStatus.AWAITING_PAYMENT
            order.save(update_fields=['status', 'updated_at'])

    return redirect('payments:result', transaction_id=payment.transaction_id)


def payment_result_view(request, transaction_id):
    """
    Customer-facing receipt showing transaction status and details.
    """
    payment = get_object_or_404(Payment.objects.select_related('order', 'order__user'), transaction_id=transaction_id)
    context = {
        'payment': payment,
        'order': payment.order,
    }
    return render(request, 'payments/payment_result.html', context)
