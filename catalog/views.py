import json
from decimal import Decimal
from django.db import models
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from django.core.paginator import Paginator
from django.db.models import Q, Min, Max, Avg
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from .models import Category, Brand, Product, ProductVariant
from accounts.models import RecentlyViewed, Wishlist
from reviews.models import Review

SEARCH_SYNONYMS = {
    's': ['سامسونگ', 'samsung', 'galaxy', 'سونی', 'sony'],
    'sa': ['سامسونگ', 'samsung', 'galaxy'],
    'sam': ['سامسونگ', 'samsung', 'galaxy'],
    'sams': ['سامسونگ', 'samsung', 'galaxy'],
    'samsu': ['سامسونگ', 'samsung', 'galaxy'],
    'samsun': ['سامسونگ', 'samsung', 'galaxy'],
    'samsung': ['سامسونگ', 'samsung', 'galaxy'],
    'galaxy': ['سامسونگ', 'samsung', 'گلکسی', 'galaxy'],
    'سامسونگ': ['samsung', 'galaxy', 'سامسونگ'],
    'گلکسی': ['galaxy', 'samsung', 'سامسونگ'],
    'app': ['اپل', 'apple', 'آیفون', 'iphone', 'ipad'],
    'appl': ['اپل', 'apple', 'آیفون', 'iphone', 'ipad'],
    'apple': ['اپل', 'آیفون', 'apple', 'iphone', 'ipad', 'macbook'],
    'اپل': ['apple', 'iphone', 'ipad', 'اپل'],
    'iph': ['آیفون', 'iphone'],
    'iphone': ['آیفون', 'اپل', 'iphone', 'apple'],
    'آیفون': ['iphone', 'apple'],
    'ipad': ['آیپد', 'ipad', 'اپل', 'apple'],
    'آیپد': ['ipad', 'apple'],
    'macbook': ['مک‌بوک', 'macbook', 'اپل'],
    'مک‌بوک': ['macbook', 'اپل'],
    'xi': ['شیائومی', 'xiaomi'],
    'xia': ['شیائومی', 'xiaomi'],
    'xiao': ['شیائومی', 'xiaomi'],
    'xiaomi': ['شیائومی', 'xiaomi', 'mi'],
    'شیائومی': ['xiaomi', 'شیائومی'],
    'so': ['سونی', 'sony'],
    'son': ['سونی', 'sony', 'playstation', 'ps5'],
    'sony': ['سونی', 'sony', 'playstation', 'ps5'],
    'سونی': ['sony', 'سونی'],
    'playstation': ['پلی‌استیشن', 'سونی', 'ps5', 'playstation'],
    'ps': ['پلی‌استیشن', 'ps5', 'playstation', 'سونی'],
    'ps5': ['پلی‌استیشن', 'ps5', 'playstation', 'سونی'],
    'پلی‌استیشن': ['playstation', 'ps5', 'sony'],
    'as': ['ایسوس', 'asus'],
    'asu': ['ایسوس', 'asus'],
    'asus': ['ایسوس', 'asus', 'zenbook'],
    'ایسوس': ['asus', 'ایسوس'],
    'dys': ['دایسون', 'dyson'],
    'dyso': ['دایسون', 'dyson'],
    'dyson': ['دایسون', 'dyson'],
    'دایسون': ['dyson', 'دایسون'],
    'phi': ['فیلیپس', 'philips'],
    'phil': ['فیلیپس', 'philips'],
    'philips': ['فیلیپس', 'philips'],
    'فیلیپس': ['philips', 'فیلیپس'],
    'ank': ['انکر', 'anker'],
    'anke': ['انکر', 'anker'],
    'anker': ['انکر', 'anker'],
    'انکر': ['anker', 'انکر'],
    'log': ['لاجیتک', 'logitech'],
    'logi': ['لاجیتک', 'logitech'],
    'logitech': ['لاجیتک', 'logitech'],
    'لاجیتک': ['logitech', 'لاجیتک'],
    'bos': ['بوش', 'bosch'],
    'bosc': ['بوش', 'bosch'],
    'bosch': ['بوش', 'bosch'],
    'بوش': ['bosch', 'بوش'],
    'can': ['کانن', 'canon'],
    'cano': ['کانن', 'canon'],
    'canon': ['کانن', 'canon'],
    'کانن': ['canon', 'کانن'],
    'bra': ['براون', 'braun'],
    'brau': ['براون', 'braun'],
    'braun': ['براون', 'braun'],
    'براون': ['braun', 'براون'],
    'del': ['دلونگی', 'delonghi', 'dell'],
    'delo': ['دلونگی', 'delonghi'],
    'delonghi': ['دلونگی', 'delonghi'],
    'دلونگی': ['delonghi', 'دلونگی'],
    'phone': ['گوشی', 'موبایل', 'phone'],
    'mobile': ['گوشی', 'موبایل', 'mobile'],
    'گوشی': ['phone', 'mobile', 'گوشی'],
    'موبایل': ['phone', 'mobile', 'موبایل'],
    'lap': ['لپ‌تاپ', 'laptop'],
    'laptop': ['لپ‌تاپ', 'laptop', 'macbook', 'zenbook'],
    'لپ‌تاپ': ['laptop', 'لپ‌تاپ'],
    'tab': ['تبلت', 'tablet'],
    'tablet': ['تبلت', 'tablet', 'ipad'],
    'تبلت': ['tablet', 'تبلت'],
    'wat': ['ساعت', 'watch'],
    'watch': ['ساعت', 'watch'],
    'ساعت': ['watch', 'ساعت'],
    'head': ['هدفون', 'headphone'],
    'headphone': ['هدفون', 'headphone', 'هندزفری'],
    'هدفون': ['headphone', 'هدفون'],
    'tv': ['تلویزیون', 'tv'],
    'تلویزیون': ['tv', 'تلویزیون'],
}

def build_search_query(q):
    if not q:
        return Q()
    q = q.strip()
    q_lower = q.lower()

    q_filter = (
        Q(name__icontains=q) |
        Q(slug__icontains=q) |
        Q(sku__icontains=q) |
        Q(description__icontains=q) |
        Q(category__name__icontains=q) |
        Q(category__slug__icontains=q) |
        Q(brand__name__icontains=q) |
        Q(brand__slug__icontains=q)
    )

    if q_lower in SEARCH_SYNONYMS:
        for term in SEARCH_SYNONYMS[q_lower]:
            q_filter |= (
                Q(name__icontains=term) |
                Q(slug__icontains=term) |
                Q(brand__name__icontains=term) |
                Q(brand__slug__icontains=term) |
                Q(category__name__icontains=term) |
                Q(category__slug__icontains=term)
            )

    try:
        from core.templatetags.shop_filters import TRANSLATIONS
        matched_fa_names = []
        for en_key, tr_dict in TRANSLATIONS.items():
            if q_lower in en_key.lower():
                fa_val = tr_dict.get('fa')
                if fa_val:
                    matched_fa_names.append(fa_val)
        if matched_fa_names:
            q_filter |= Q(name__in=matched_fa_names[:30])
    except Exception:
        pass

    return q_filter

def shop_list_view(request):
    """
    Main product catalog listing with multi-faceted filtering, live search, and sorting.
    """
    queryset = Product.objects.filter(is_active=True).select_related('category', 'brand').prefetch_related('images')

    # Search keyword
    q = request.GET.get('q', '').strip()
    if q:
        queryset = queryset.filter(build_search_query(q))

    # Category filter (includes all descendant subcategories)
    category_slug = request.GET.get('category')
    selected_category = None
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug, is_active=True)
        subcategories = selected_category.get_all_subcategories()
        category_ids = [selected_category.id] + [c.id for c in subcategories]
        queryset = queryset.filter(category_id__in=category_ids)

    # Brand filter (single or multi-select: ?brands=slug1,slug2)
    brand_slug = request.GET.get('brand')
    selected_brand = None
    if brand_slug:
        selected_brand = get_object_or_404(Brand, slug=brand_slug, is_active=True)
        queryset = queryset.filter(brand=selected_brand)

    brand_slugs = [s for s in request.GET.get('brands', '').split(',') if s.strip()]
    if brand_slugs:
        queryset = queryset.filter(brand__slug__in=brand_slugs)

    # Price range filter
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price and min_price.isdigit():
        queryset = queryset.filter(base_price__gte=Decimal(min_price))
    if max_price and max_price.isdigit():
        queryset = queryset.filter(base_price__lte=Decimal(max_price))

    # In-stock filter
    in_stock = request.GET.get('in_stock') == '1'
    if in_stock:
        queryset = queryset.filter(stock__gt=0, is_available=True)

    # Discount filter
    discount_only = request.GET.get('discount') == '1'
    if discount_only:
        queryset = queryset.filter(sale_price__isnull=False).filter(sale_price__lt=models.F('base_price'))

    # Minimum rating filter (approved reviews average)
    min_rating = request.GET.get('min_rating', '').strip()
    rating_annotated = False
    if min_rating and min_rating.replace('.', '', 1).isdigit():
        queryset = queryset.annotate(
            avg_rating=Coalesce(Avg('reviews__rating', filter=Q(reviews__is_approved=True)), models.Value(0.0))
        ).filter(avg_rating__gte=Decimal(min_rating))
        rating_annotated = True
    else:
        min_rating = ''

    # Sorting
    sort = request.GET.get('sort', 'newest')
    if sort == 'oldest':
        queryset = queryset.order_by('created_at')
    elif sort == 'rating':
        if not rating_annotated:
            queryset = queryset.annotate(
                avg_rating=Coalesce(Avg('reviews__rating', filter=Q(reviews__is_approved=True)), models.Value(0.0))
            )
        queryset = queryset.order_by('-avg_rating')
    elif sort == 'price_low':
        queryset = queryset.order_by('base_price')
    elif sort == 'price_high':
        queryset = queryset.order_by('-base_price')
    elif sort == 'discount':
        queryset = queryset.order_by('-discount_percent')
    elif sort == 'popular' or sort == 'bestseller':
        queryset = queryset.order_by('-is_bestseller', '-created_at')
    else:  # newest default
        queryset = queryset.order_by('-created_at')

    # Pagination: 24 products per page for high-volume catalog
    paginator = Paginator(queryset, 24)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Context data for filters
    all_categories = Category.objects.filter(parent__isnull=True, is_active=True).prefetch_related('children')
    all_brands = Brand.objects.filter(is_active=True)
    price_bounds = Product.objects.filter(is_active=True).aggregate(lo=Min('base_price'), hi=Max('base_price'))

    context = {
        'page_obj': page_obj,
        'products': page_obj.object_list,
        'q': q,
        'selected_category': selected_category,
        'selected_brand': selected_brand,
        'min_price': min_price or '',
        'max_price': max_price or '',
        'in_stock': in_stock,
        'discount_only': discount_only,
        'min_rating': min_rating,
        'selected_brands': brand_slugs,
        'sort': sort,
        'categories': all_categories,
        'brands': all_brands,
        'price_lower_bound': price_bounds['lo'] or 0,
        'price_upper_bound': price_bounds['hi'] or 10000000,
        'total_count': paginator.count,
    }
    return render(request, 'catalog/shop.html', context)


def category_detail_view(request, slug):
    """Direct SEO category listing."""
    category = get_object_or_404(Category, slug=slug, is_active=True)
    # Redirect to shop with category filter
    return redirect(f"{reverse('catalog:shop')}?category={category.slug}")


def brand_detail_view(request, slug):
    """Direct SEO brand listing."""
    brand = get_object_or_404(Brand, slug=slug, is_active=True)
    return redirect(f"{reverse('catalog:shop')}?brand={brand.slug}")


def product_detail_view(request, slug):
    """
    Detailed product showcase: galleries, variants data for interactive JS, specs, reviews, recommendations.
    """
    product = get_object_or_404(
        Product.objects.select_related('category', 'brand').prefetch_related('images', 'variants', 'specifications'),
        slug=slug,
        is_active=True
    )

    # Track Recently Viewed
    if request.user.is_authenticated:
        RecentlyViewed.objects.update_or_create(
            user=request.user,
            product=product
        )
    else:
        if not request.session.session_key:
            request.session.save()
        RecentlyViewed.objects.update_or_create(
            session_key=request.session.session_key,
            product=product
        )

    # Serialize variants for dynamic client-side selection
    variants_data = []
    for v in product.variants.filter(is_active=True):
        variants_data.append({
            'id': v.id,
            'name': v.name,
            'sku': v.sku,
            'price': int(v.get_price()),
            'stock': v.stock,
            'is_in_stock': v.is_in_stock()
        })

    # Related Products in same category
    related_products = Product.objects.filter(
        category=product.category,
        is_active=True
    ).exclude(id=product.id).prefetch_related('images')[:4]

    # Customer Reviews
    reviews = Review.objects.filter(product=product, is_approved=True).select_related('user')

    # Wishlist status for active user
    is_in_wishlist = False
    if request.user.is_authenticated:
        is_in_wishlist = Wishlist.objects.filter(user=request.user, product=product).exists()

    context = {
        'product': product,
        'images': product.images.all(),
        'variants': product.variants.filter(is_active=True),
        'variants_json': json.dumps(variants_data),
        'specifications': product.specifications.all(),
        'related_products': related_products,
        'reviews': reviews,
        'is_in_wishlist': is_in_wishlist,
        'avg_rating': product.get_average_rating(),
        'review_count': product.get_review_count(),
    }
    return render(request, 'catalog/product_detail.html', context)


def product_compare_view(request):
    """
    Side-by-side product comparison matrix: ?ids=1,2,3 (max 3 products).
    """
    raw_ids = request.GET.get('ids', '')
    ids = []
    for part in raw_ids.replace(' ', ',').split(','):
        if part.isdigit():
            ids.append(int(part))
    ids = list(dict.fromkeys(ids))[:3]  # dedupe, keep order, cap at 3

    products = Product.objects.filter(
        id__in=ids, is_active=True
    ).select_related('category', 'brand').prefetch_related('images', 'specifications')

    # Preserve user selection order
    products = sorted(products, key=lambda p: ids.index(p.id))

    # Build unified spec rows across compared products
    all_keys = []
    for product in products:
        for spec in product.specifications.all():
            if spec.key not in all_keys:
                all_keys.append(spec.key)

    spec_rows = []
    for key in all_keys:
        row = {'key': key, 'values': [], 'identical': True}
        previous = None
        for product in products:
            value = next((s.value for s in product.specifications.all() if s.key == key), '—')
            row['values'].append(value)
            if previous is not None and value != previous:
                row['identical'] = False
            previous = value
        spec_rows.append(row)

    # Best-price highlight
    prices = [p.get_effective_price() for p in products]
    best_price = min(prices) if prices else None

    context = {
        'products': products,
        'spec_rows': spec_rows,
        'best_price': best_price,
        'price_map': {p.id: p.get_effective_price() for p in products},
    }
    return render(request, 'catalog/compare.html', context)


def live_search_api_view(request):
    """
    JSON endpoint for debounced live search suggestions.
    """
    from core.templatetags.shop_filters import lookup_translation, toman

    q = request.GET.get('q', '').strip()
    if len(q) < 1:
        return JsonResponse({'results': []})

    lang = getattr(request, 'LANGUAGE_CODE', None)
    if not lang:
        from django.utils import translation
        lang = translation.get_language() or 'fa'

    products = Product.objects.filter(
        build_search_query(q),
        is_active=True
    ).select_related('category', 'brand').prefetch_related('images').distinct()[:8]

    currency_str = lookup_translation('Currency Toman', lang)

    results = []
    for p in products:
        results.append({
            'id': p.id,
            'name': lookup_translation(p.name, lang),
            'url': p.get_absolute_url(),
            'price': toman(p.get_effective_price(), lang),
            'currency': currency_str,
            'category': lookup_translation(p.category.name, lang),
            'image': p.get_primary_image(),
            'in_stock': p.is_in_stock()
        })

    return JsonResponse({'results': results})
