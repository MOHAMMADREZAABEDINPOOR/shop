import time
from django.http import HttpResponse
from django.utils.deprecation import MiddlewareMixin

# In-memory IP tracking for sensitive endpoints
_RATE_LIMIT_STORE = {}

class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Applies defense-in-depth HTTP security headers to all responses.
    """
    def process_response(self, request, response):
        response.headers.setdefault('X-Content-Type-Options', 'nosniff')
        response.headers.setdefault('X-Frame-Options', 'DENY')
        response.headers.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
        response.headers.setdefault('Permissions-Policy', 'camera=(), microphone=(), geolocation=()')
        response.headers.setdefault('Cross-Origin-Opener-Policy', 'same-origin')
        # CSP: blocks third-party exfiltration while allowing the site's own
        # inline scripts/styles (used across templates) + Google Fonts.
        csp = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' https://www.googletagmanager.com https://www.google-analytics.com; "
            "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net; "
            "font-src 'self' https://fonts.gstatic.com https://cdn.jsdelivr.net data:; "
            "img-src 'self' data: https:; "
            "connect-src 'self' https://www.google-analytics.com; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
        response.headers.setdefault('Content-Security-Policy', csp)
        return response


class SimpleRateLimitMiddleware(MiddlewareMixin):
    """
    Protects sensitive endpoints (login, register, password reset, checkout,
    contact, newsletter) from brute-force and spam bots.
    """
    RATE_LIMIT_ROUTES = {
        '/accounts/login/': (15, 60),               # 15 requests per 60s
        '/accounts/register/': (10, 60),            # 10 requests per 60s
        '/accounts/forgot-password/': (5, 300),     # 5 requests per 5min
        '/orders/checkout/': (30, 60),              # 30 requests per 60s
        '/contact/': (10, 300),                     # 10 messages per 5min
        '/newsletter/subscribe/': (10, 300),        # 10 subscribes per 5min
    }

    def process_request(self, request):
        path = request.path
        if path in self.RATE_LIMIT_ROUTES and request.method == 'POST':
            limit, window = self.RATE_LIMIT_ROUTES[path]
            client_ip = self._get_client_ip(request)
            key = f"{client_ip}:{path}"
            now = time.time()

            # Clean old entries
            requests = [t for t in _RATE_LIMIT_STORE.get(key, []) if now - t < window]
            if len(requests) >= limit:
                return HttpResponse(
                    '{"status": "error", "message": "تعداد درخواست‌های شما بیش از حد مجاز است. لطفاً کمی صبر کرده و دوباره تلاش کنید."}',
                    status=429,
                    content_type="application/json; charset=utf-8"
                )

            requests.append(now)
            _RATE_LIMIT_STORE[key] = requests
        return None

    def _get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '127.0.0.1')
