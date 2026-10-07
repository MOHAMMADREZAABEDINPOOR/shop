from decimal import Decimal
import csv
import json
import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from django.db.models import Sum, Count, Avg, Q
from django.db.models.functions import TruncDate
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.core.paginator import Paginator
from django.utils import timezone
from django.utils.text import slugify

from orders.models import Order, OrderItem
from catalog.models import Product, ProductVariant, Category, Brand, ProductImage, ProductSpecification
from accounts.models import User
from core.models import ContactMessage, SiteSetting
from core.validators import validate_image_upload
from django.core.exceptions import ValidationError

def staff_required(view_func):
    return user_passes_test(lambda u: u.is_authenticated and (u.is_staff or u.is_superuser), login_url='accounts:login')(view_func)


@staff_required
def dashboard_overview_view(request):
    """
    Staff / Admin executive operations dashboard showcasing business KPIs and stock alerts.
    """
    paid_statuses = [
        Order.OrderStatus.PAID,
        Order.OrderStatus.PROCESSING,
        Order.OrderStatus.SHIPPED,
        Order.OrderStatus.DELIVERED
    ]
    paid_orders = Order.objects.filter(status__in=paid_statuses)
    total_revenue = paid_orders.aggregate(Sum('grand_total'))['grand_total__sum'] or Decimal('0')
    total_orders_count = Order.objects.count()
    pending_orders_count = Order.objects.filter(status__in=[Order.OrderStatus.PENDING, Order.OrderStatus.AWAITING_PAYMENT]).count()
    aov = paid_orders.aggregate(Avg('grand_total'))['grand_total__avg'] or Decimal('0')

    total_customers_count = User.objects.filter(role=User.Role.CUSTOMER).count()
    total_products_count = Product.objects.count()

    low_stock_products = Product.objects.filter(stock__lte=5, stock__gt=0, is_active=True)
    out_of_stock_products = Product.objects.filter(stock=0, is_active=True)

    recent_orders = Order.objects.select_related('user').prefetch_related('items').order_by('-created_at')[:10]
    unread_messages = ContactMessage.objects.filter(is_read=False).count()

    context = {
        'total_revenue': total_revenue,
        'total_orders_count': total_orders_count,
        'pending_orders_count': pending_orders_count,
        'aov': round(aov),
        'total_customers_count': total_customers_count,
        'total_products_count': total_products_count,
        'low_stock_products': low_stock_products,
        'out_of_stock_products': out_of_stock_products,
        'recent_orders': recent_orders,
        'unread_messages': unread_messages,
    }
    return render(request, 'dashboard/overview.html', context)


@staff_required
def dashboard_orders_view(request):
    """
    Order management table with status filtering and tracking code assignment.
    """
    status_filter = request.GET.get('status')
    orders = Order.objects.select_related('user').prefetch_related('items').order_by('-created_at')

    if status_filter:
        orders = orders.filter(status=status_filter)

    q = request.GET.get('q', '').strip()
    if q:
        orders = orders.filter(
            Q(order_number__icontains=q) |
            Q(shipping_name__icontains=q) |
            Q(shipping_phone__icontains=q) |
            Q(user__email__icontains=q)
        )

    context = {
        'orders': orders[:50],
        'status_choices': Order.OrderStatus.choices,
        'current_status': status_filter,
        'q': q,
    }
    return render(request, 'dashboard/orders_list.html', context)


@staff_required
@require_POST
def dashboard_update_order_status_view(request, order_number):
    """
    Updates order progress and tracking code.
    """
    order = get_object_or_404(Order, order_number=order_number)
    new_status = request.POST.get('status')
    tracking_code = request.POST.get('tracking_code', '').strip()

    if new_status in dict(Order.OrderStatus.choices):
        order.status = new_status
        if tracking_code:
            order.tracking_code = tracking_code
        order.save(update_fields=['status', 'tracking_code', 'updated_at'])
        messages.success(request, f"وضعیت سفارش {order.order_number} به «{order.get_status_display()}» تغییر یافت.")

    return redirect(request.META.get('HTTP_REFERER', 'dashboard:orders'))


@staff_required
def dashboard_inventory_view(request):
    """
    Dedicated stock monitoring and quick adjustment screen.
    """
    products = Product.objects.select_related('category').order_by('stock')

    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        new_stock = request.POST.get('stock')
        if product_id and new_stock is not None and new_stock.isdigit():
            p = get_object_or_404(Product, id=product_id)
            p.stock = int(new_stock)
            p.is_available = p.stock > 0
            p.save(update_fields=['stock', 'is_available', 'updated_at'])
            messages.success(request, f"موجودی انبار کالای «{p.name}» به {new_stock} تغییر یافت.")
            return redirect('dashboard:inventory')

    context = {
        'products': products[:100],
    }
    return render(request, 'dashboard/inventory.html', context)


@staff_required
def dashboard_reports_view(request):
    """
    Analytics & reporting center: revenue trend, order status funnel,
    top-selling products, and category share (Chart.js powered).
    """
    days = int(request.GET.get('days', 30) or 30)
    days = min(max(days, 7), 90)
    date_from = timezone.now() - timezone.timedelta(days=days)

    paid_statuses = [
        Order.OrderStatus.PAID,
        Order.OrderStatus.PROCESSING,
        Order.OrderStatus.SHIPPED,
        Order.OrderStatus.DELIVERED
    ]
    paid_orders = Order.objects.filter(status__in=paid_statuses)

    # 1. Revenue & orders per day trend
    trend = (
        paid_orders.filter(created_at__gte=date_from)
        .annotate(day=TruncDate('created_at'))
        .values('day')
        .annotate(revenue=Sum('grand_total'), orders=Count('id'))
        .order_by('day')
    )
    trend_labels = [d['day'].strftime('%m/%d') for d in trend]
    trend_revenue = [int(d['revenue'] or 0) for d in trend]
    trend_orders = [d['orders'] for d in trend]

    # Period-over-period growth comparison
    current_revenue = sum(trend_revenue)
    prev_window = paid_orders.filter(
        created_at__gte=date_from - timezone.timedelta(days=days),
        created_at__lt=date_from
    ).aggregate(v=Sum('grand_total'))['v'] or Decimal('0')
    growth_percent = (
        round((Decimal(current_revenue) - prev_window) / prev_window * 100, 1)
        if prev_window else None
    )

    # 2. Status distribution
    status_counts = Order.objects.values('status').annotate(n=Count('id'))
    status_map = dict(Order.OrderStatus.choices)
    status_labels = [status_map.get(s['status'], s['status']) for s in status_counts]
    status_values = [s['n'] for s in status_counts]

    # 3. Top selling products (by revenue)
    top_products = (
        OrderItem.objects.filter(order__status__in=paid_statuses, order__created_at__gte=date_from)
        .values('product__name')
        .annotate(qty=Sum('quantity'), revenue=Sum('total_price'))
        .order_by('-revenue')[:8]
    )

    # 4. Category revenue share
    category_share = (
        OrderItem.objects.filter(order__status__in=paid_statuses, order__created_at__gte=date_from)
        .values('product__category__name')
        .annotate(revenue=Sum('total_price'))
        .order_by('-revenue')[:6]
    )

    context = {
        'days': days,
        'current_revenue': current_revenue,
        'growth_percent': growth_percent,
        'trend_labels_json': json.dumps(trend_labels),
        'trend_revenue_json': json.dumps(trend_revenue),
        'trend_orders_json': json.dumps(trend_orders),
        'status_labels_json': json.dumps(status_labels, ensure_ascii=False),
        'status_values_json': json.dumps(status_values),
        'top_products': top_products,
        'category_share': category_share,
        'category_labels_json': json.dumps([c['product__category__name'] or 'نامشخص' for c in category_share], ensure_ascii=False),
        'category_values_json': json.dumps([int(c['revenue'] or 0) for c in category_share]),
    }
    return render(request, 'dashboard/reports.html', context)


@staff_required
def dashboard_export_orders_csv_view(request):
    """
    CSV export of orders for accounting/reporting (Excel-friendly UTF-8 BOM).
    """
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="orders-export.csv"'
    response.write('\ufeff')  # BOM for Excel

    writer = csv.writer(response)
    writer.writerow([
        'شماره سفارش', 'مشتری', 'ایمیل', 'مبلغ نهایی (تومان)', 'وضعیت',
        'تعداد اقلام', 'روش ارسال', 'کد رهگیری', 'تاریخ ثبت'
    ])
    orders = (
        Order.objects.select_related('user')
        .annotate(items_count=Count('items'))
        .order_by('-created_at')[:2000]
    )
    for o in orders:
        writer.writerow([
            o.order_number,
            o.shipping_name,
            getattr(o.user, 'email', '') or '',
            int(o.grand_total),
            o.get_status_display(),
            o.items_count,
            o.shipping_method,
            o.tracking_code,
            o.created_at.strftime('%Y-%m-%d %H:%M'),
        ])
    return response


# =========================================================================
# Employer / Staff Product Management Views (Full CRUD & Discounts)
# =========================================================================

@staff_required
def dashboard_products_list_view(request):
    """
    Comprehensive product management catalog for the store employer/admin:
    Search, category filter, brand filter, stock status, discount toggle, and pagination.
    """
    products = Product.objects.select_related('category', 'brand').prefetch_related('images').order_by('-created_at')

    # Search query
    q = request.GET.get('q', '').strip()
    if q:
        products = products.filter(
            Q(name__icontains=q) |
            Q(sku__icontains=q) |
            Q(category__name__icontains=q) |
            Q(brand__name__icontains=q)
        )

    # Category filter
    category_slug = request.GET.get('category', '').strip()
    if category_slug:
        products = products.filter(category__slug=category_slug)

    # Brand filter
    brand_slug = request.GET.get('brand', '').strip()
    if brand_slug:
        products = products.filter(brand__slug=brand_slug)

    # Stock filter
    stock_status = request.GET.get('stock_status', '').strip()
    if stock_status == 'in_stock':
        products = products.filter(stock__gt=5)
    elif stock_status == 'low_stock':
        products = products.filter(stock__lte=5, stock__gt=0)
    elif stock_status == 'out_of_stock':
        products = products.filter(stock=0)

    # Discount filter
    discount_filter = request.GET.get('discount', '').strip()
    if discount_filter == 'yes':
        products = products.filter(sale_price__isnull=False)
    elif discount_filter == 'no':
        products = products.filter(sale_price__isnull=True)

    # Statistics
    total_count = Product.objects.count()
    in_stock_count = Product.objects.filter(stock__gt=0).count()
    discounted_count = Product.objects.filter(sale_price__isnull=False).count()
    out_of_stock_count = Product.objects.filter(stock=0).count()

    # Pagination: 25 items per page
    paginator = Paginator(products, 25)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    categories = Category.objects.all().order_by('name')
    brands = Brand.objects.all().order_by('name')

    context = {
        'page_obj': page_obj,
        'q': q,
        'category_slug': category_slug,
        'brand_slug': brand_slug,
        'stock_status': stock_status,
        'discount_filter': discount_filter,
        'total_count': total_count,
        'in_stock_count': in_stock_count,
        'discounted_count': discounted_count,
        'out_of_stock_count': out_of_stock_count,
        'categories': categories,
        'brands': brands,
    }
    return render(request, 'dashboard/products_list.html', context)


@staff_required
def dashboard_product_create_view(request):
    """
    Allows employer/staff to add a new product with full details, specs, and primary image.
    """
    categories = Category.objects.all().order_by('name')
    brands = Brand.objects.all().order_by('name')

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        sku = request.POST.get('sku', '').strip()
        category_id = request.POST.get('category')
        brand_id = request.POST.get('brand')
        base_price_raw = request.POST.get('base_price', '0').strip()
        sale_price_raw = request.POST.get('sale_price', '').strip()
        stock_raw = request.POST.get('stock', '10').strip()
        short_description = request.POST.get('short_description', '').strip()
        description = request.POST.get('description', '').strip()
        is_featured = bool(request.POST.get('is_featured'))
        is_bestseller = bool(request.POST.get('is_bestseller'))
        is_new_arrival = bool(request.POST.get('is_new_arrival'))

        if not name or not base_price_raw or not category_id:
            messages.error(request, "لطفاً نام کالا، دسته‌بندی و قیمت اصلی را مشخص نمایید.")
            return render(request, 'dashboard/product_form.html', {
                'categories': categories,
                'brands': brands,
                'is_create': True,
            })

        # Generate unique slug
        base_slug = slugify(name, allow_unicode=True) or f"product-{uuid.uuid4().hex[:6]}"
        slug = base_slug
        counter = 1
        while Product.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1

        if not sku:
            sku = f"SKU-{uuid.uuid4().hex[:8].upper()}"

        base_price = Decimal(base_price_raw.replace(',', ''))
        sale_price = Decimal(sale_price_raw.replace(',', '')) if sale_price_raw else None
        stock = int(stock_raw) if stock_raw.isdigit() else 0

        discount_percent = 0
        if sale_price and sale_price < base_price:
            discount_percent = int(((base_price - sale_price) / base_price) * 100)

        product = Product.objects.create(
            name=name,
            slug=slug,
            sku=sku,
            category_id=category_id,
            brand_id=brand_id or None,
            base_price=base_price,
            sale_price=sale_price,
            discount_percent=discount_percent,
            stock=stock,
            is_available=stock > 0,
            short_description=short_description,
            description=description,
            is_featured=is_featured,
            is_bestseller=is_bestseller,
            is_new_arrival=is_new_arrival,
        )

        # Handle Image Upload if provided
        if 'image' in request.FILES:
            try:
                validate_image_upload(request.FILES['image'])
            except ValidationError as e:
                messages.error(request, f"تصویر محصول پذیرفته نشد: {e.messages[0]}")
                return render(request, 'dashboard/product_form.html', {
                    'categories': categories,
                    'brands': brands,
                    'is_create': True,
                })
            ProductImage.objects.create(
                product=product,
                image=request.FILES['image'],
                alt_text=product.name,
                is_feature=True,
                order=1
            )
        elif request.POST.get('image_url'):
            # Allow linking an existing media path or URL
            ProductImage.objects.create(
                product=product,
                image=request.POST.get('image_url').strip(),
                alt_text=product.name,
                is_feature=True,
                order=1
            )

        # Handle specifications if provided
        spec_keys = request.POST.getlist('spec_key[]')
        spec_values = request.POST.getlist('spec_value[]')
        for k, v in zip(spec_keys, spec_values):
            if k.strip() and v.strip():
                ProductSpecification.objects.create(
                    product=product,
                    key=k.strip(),
                    value=v.strip()
                )

        messages.success(request, f"محصول جدید «{product.name}» با موفقیت در فروشگاه ثبت شد.")
        return redirect('dashboard:products')

    context = {
        'categories': categories,
        'brands': brands,
        'is_create': True,
    }
    return render(request, 'dashboard/product_form.html', context)


@staff_required
def dashboard_product_edit_view(request, pk):
    """
    Allows employer/staff to edit product specifications, prices, stock, discounts, and images.
    """
    product = get_object_or_404(Product, pk=pk)
    categories = Category.objects.all().order_by('name')
    brands = Brand.objects.all().order_by('name')

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        sku = request.POST.get('sku', '').strip()
        category_id = request.POST.get('category')
        brand_id = request.POST.get('brand')
        base_price_raw = request.POST.get('base_price', '').strip()
        sale_price_raw = request.POST.get('sale_price', '').strip()
        stock_raw = request.POST.get('stock', '').strip()
        short_description = request.POST.get('short_description', '').strip()
        description = request.POST.get('description', '').strip()
        is_featured = bool(request.POST.get('is_featured'))
        is_bestseller = bool(request.POST.get('is_bestseller'))
        is_new_arrival = bool(request.POST.get('is_new_arrival'))
        is_active = bool(request.POST.get('is_active'))

        if name:
            product.name = name
        if sku:
            product.sku = sku
        if category_id:
            product.category_id = category_id
        product.brand_id = brand_id or None

        if base_price_raw:
            product.base_price = Decimal(base_price_raw.replace(',', ''))

        if sale_price_raw:
            sp = Decimal(sale_price_raw.replace(',', ''))
            if sp < product.base_price:
                product.sale_price = sp
                product.discount_percent = int(((product.base_price - sp) / product.base_price) * 100)
            else:
                product.sale_price = None
                product.discount_percent = 0
        else:
            product.sale_price = None
            product.discount_percent = 0

        if stock_raw.isdigit():
            product.stock = int(stock_raw)
            product.is_available = product.stock > 0

        product.short_description = short_description
        product.description = description
        product.is_featured = is_featured
        product.is_bestseller = is_bestseller
        product.is_new_arrival = is_new_arrival
        product.is_active = is_active
        product.save()

        # Handle uploaded new image
        if 'new_image' in request.FILES:
            try:
                validate_image_upload(request.FILES['new_image'])
            except ValidationError as e:
                messages.error(request, f"تصویر جدید پذیرفته نشد: {e.messages[0]}")
                return render(request, 'dashboard/product_form.html', {
                    'product': product,
                    'categories': categories,
                    'brands': brands,
                    'is_create': False,
                })
            ProductImage.objects.create(
                product=product,
                image=request.FILES['new_image'],
                alt_text=product.name,
                is_feature=not product.images.exists(),
                order=product.images.count() + 1
            )

        messages.success(request, f"تغییرات کالا «{product.name}» با موفقیت ذخیره شد.")
        return redirect('dashboard:products')

    context = {
        'product': product,
        'categories': categories,
        'brands': brands,
        'is_create': False,
    }
    return render(request, 'dashboard/product_form.html', context)


@staff_required
@require_POST
def dashboard_product_quick_discount_view(request, pk):
    """
    Employer Quick Discount Tool:
    Allows instant setting of discount percentage or direct sale price.
    """
    product = get_object_or_404(Product, pk=pk)
    discount_percent_raw = request.POST.get('discount_percent', '').strip()
    sale_price_raw = request.POST.get('sale_price', '').strip()

    if discount_percent_raw and discount_percent_raw.isdigit():
        pct = int(discount_percent_raw)
        if 0 < pct < 100:
            discount_amount = (product.base_price * Decimal(pct)) / Decimal(100)
            product.sale_price = (product.base_price - discount_amount).quantize(Decimal('1000'))
            product.discount_percent = pct
            product.save(update_fields=['sale_price', 'discount_percent', 'updated_at'])
            messages.success(request, f"تخفیف {pct}٪ روی کالای «{product.name}» اعمال شد. قیمت فروش جدید: {product.sale_price:,} تومان")
        elif pct == 0:
            product.sale_price = None
            product.discount_percent = 0
            product.save(update_fields=['sale_price', 'discount_percent', 'updated_at'])
            messages.info(request, f"تخفیف کالای «{product.name}» حذف گردید.")
    elif sale_price_raw:
        sp = Decimal(sale_price_raw.replace(',', ''))
        if sp < product.base_price:
            product.sale_price = sp
            product.discount_percent = int(((product.base_price - sp) / product.base_price) * 100)
            product.save(update_fields=['sale_price', 'discount_percent', 'updated_at'])
            messages.success(request, f"قیمت با تخفیف «{product.name}» به {product.sale_price:,} تومان به‌روزرسانی شد.")

    return redirect(request.META.get('HTTP_REFERER', 'dashboard:products'))


@staff_required
@require_POST
def dashboard_product_toggle_view(request, pk):
    """
    Quickly toggles product active status.
    """
    product = get_object_or_404(Product, pk=pk)
    product.is_active = not product.is_active
    product.save(update_fields=['is_active', 'updated_at'])
    status_text = "فعال" if product.is_active else "غیرفعال"
    messages.success(request, f"وضعیت کالای «{product.name}» به «{status_text}» تغییر یافت.")
    return redirect(request.META.get('HTTP_REFERER', 'dashboard:products'))


@staff_required
@require_POST
def dashboard_product_delete_view(request, pk):
    """
    Allows employer/staff to delete a product.
    """
    product = get_object_or_404(Product, pk=pk)
    name = product.name
    product.delete()
    messages.warning(request, f"کالای «{name}» از سیستم حذف شد.")
    return redirect('dashboard:products')
