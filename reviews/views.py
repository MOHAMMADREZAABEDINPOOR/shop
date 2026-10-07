from django.shortcuts import redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from .models import Review
from catalog.models import Product
from orders.models import Order, OrderItem

@login_required
@require_POST
def submit_review_view(request, product_id):
    product = get_object_or_404(Product, id=product_id, is_active=True)

    rating_val = request.POST.get('rating', '5')
    try:
        rating = int(rating_val)
        if rating < 1 or rating > 5:
            rating = 5
    except ValueError:
        rating = 5

    title = request.POST.get('title', '').strip()
    comment = request.POST.get('comment', '').strip()

    if not comment:
        messages.error(request, "لطفاً متن نظر خود را وارد کنید.")
        return redirect('catalog:product_detail', slug=product.slug)

    # Check if user is a verified buyer (ordered this product in a PAID/DELIVERED order)
    is_verified = OrderItem.objects.filter(
        order__user=request.user,
        order__status__in=[Order.OrderStatus.PAID, Order.OrderStatus.PROCESSING, Order.OrderStatus.SHIPPED, Order.OrderStatus.DELIVERED],
        product=product
    ).exists()

    review, created = Review.objects.update_or_create(
        product=product,
        user=request.user,
        defaults={
            'rating': rating,
            'title': title or "نظر کاربر",
            'comment': comment,
            'is_verified_buyer': is_verified,
            'is_approved': True  # Auto approved for seamless store operation
        }
    )

    if created:
        messages.success(request, "دیدگاه ارزشمند شما با موفقیت ثبت گردید.")
    else:
        messages.success(request, "دیدگاه شما با موفقیت به‌روزرسانی شد.")

    return redirect('catalog:product_detail', slug=product.slug)
