from catalog.models import Category

def categories_menu_context(request):
    """
    Exposes active hierarchical categories for the main navigation menu.
    """
    try:
        categories = Category.objects.filter(
            parent__isnull=True,
            is_active=True
        ).prefetch_related('children__children').order_by('order', 'name')
    except Exception:
        categories = []
    return {
        'nav_categories': categories
    }
