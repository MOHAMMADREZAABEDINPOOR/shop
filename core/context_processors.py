import os

from core.models import SiteSetting

def site_settings_context(request):
    """
    Exposes global store settings to all templates.
    """
    try:
        settings = SiteSetting.get_settings()
    except Exception:
        settings = None
    return {
        'site_settings': settings
    }


def analytics_context(request):
    """Exposes the analytics measurement ID (empty = analytics disabled)."""
    return {
        'analytics_id': os.environ.get('ANALYTICS_ID', '').strip(),
    }
