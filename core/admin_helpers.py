"""
Shared helpers for beautiful Django Admin list columns:
pill badges, star ratings, thumbnails and Persian-formatted numbers.
"""
from django.templatetags.static import static
from django.utils.html import format_html
from django.urls import reverse

PLACEHOLDER = static('images/placeholder.svg')

COLORS = {
    'success': 'adm-success',
    'danger': 'adm-danger',
    'warning': 'adm-warning',
    'info': 'adm-info',
    'purple': 'adm-purple',
    'muted': 'adm-muted',
}


def badge(text, color='muted'):
    """Render a pill badge: badge('موجود', 'success')"""
    css = COLORS.get(color, 'adm-muted')
    return format_html('<span class="adm-badge {}">{}</span>', css, text)


def yes_no(value, yes='✓ فعال', no='✕ غیرفعال', yes_color='success', no_color='danger'):
    return badge(yes if value else no, yes_color if value else no_color)


def stars(rating):
    """★★★★☆ visual rating."""
    rating = int(rating or 0)
    return format_html(
        '<span class="adm-stars" title="{} از ۵">{}</span> <span class="adm-mono">{}</span>',
        rating,
        '★' * rating + '☆' * (5 - rating),
        f'{rating}/5'
    )


def thumbnail(url, alt='', size=46):
    return format_html(
        '<img src="{}" alt="{}" class="adm-thumb" style="width:{}px;height:{}px;">',
        url or PLACEHOLDER, alt, size, size
    )


def toman(value):
    """1,250,000 → «۱٬۲۵۰٬۰۰۰» with bold mono style."""
    try:
        digits = f'{int(value):,}'
        fa = digits.translate(str.maketrans('0123456789,', '۰۱۲۳۴۵۶۷۸۹٬'))
    except (TypeError, ValueError):
        fa = str(value)
    return format_html('<span class="adm-mono">{}</span>', fa)


def product_thumb(product):
    """Safe thumbnail for a Product instance (may have no images)."""
    if product is None:
        return format_html('<span class="adm-badge adm-muted">حذف‌شده</span>')
    return thumbnail(product.get_primary_image(), product.name)


def order_link(order):
    """Clickable order number jumping straight to the change page."""
    if order is None:
        return '—'
    url = reverse('admin:orders_order_change', args=[order.pk])
    return format_html('<a href="{}" class="adm-mono">{}</a>', url, order.order_number)
