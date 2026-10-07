from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.urls import reverse
from .models import SiteSetting, Banner, ContactMessage, NewsletterSubscription
from catalog.models import Category, Brand, Product
from reviews.models import Review

def home_view(request):
    """
    Homepage showcasing hero banners, top categories, featured offers, best sellers, and new arrivals.
    """
    hero_banners = Banner.objects.filter(position='hero', is_active=True).order_by('order')
    dual_banner_1 = Banner.objects.filter(position='middle_dual_1', is_active=True).first()
    dual_banner_2 = Banner.objects.filter(position='middle_dual_2', is_active=True).first()
    special_banner = Banner.objects.filter(position='special_offer', is_active=True).first()

    categories = Category.objects.filter(parent__isnull=True, is_active=True).order_by('order')[:8]
    featured_products = Product.objects.filter(is_featured=True, is_active=True).prefetch_related('images')[:8]
    bestseller_products = Product.objects.filter(is_bestseller=True, is_active=True).prefetch_related('images')[:8]
    new_products = Product.objects.filter(is_new_arrival=True, is_active=True).prefetch_related('images')[:8]
    discounted_products = Product.objects.filter(sale_price__isnull=False, is_active=True).prefetch_related('images')[:8]
    brands = Brand.objects.filter(is_active=True)[:12]
    testimonials = Review.objects.filter(is_approved=True, rating__gte=4).select_related('user', 'product')[:6]

    context = {
        'hero_banners': hero_banners,
        'dual_banner_1': dual_banner_1,
        'dual_banner_2': dual_banner_2,
        'special_banner': special_banner,
        'categories': categories,
        'featured_products': featured_products,
        'bestseller_products': bestseller_products,
        'new_products': new_products,
        'discounted_products': discounted_products,
        'brands': brands,
        'testimonials': testimonials,
    }
    return render(request, 'core/home.html', context)


from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
from django.urls import reverse
from .models import SiteSetting, Banner, ContactMessage, NewsletterSubscription
from catalog.models import Category, Brand, Product

MAX_CONTACT_LEN = {"name": 150, "email": 254, "phone": 30, "subject": 200, "message": 5000}


def _honeypot_triggered(request):
    return bool(request.POST.get('website', '').strip())


def contact_view(request):
    """
    Contact us page with real database persistence.
    """
    site_settings = SiteSetting.get_settings()
    if request.method == 'POST':
        if _honeypot_triggered(request):
            messages.success(request, "پیام شما با موفقیت ثبت شد. کارشناسان ما به زودی با شما تماس خواهند گرفت.")
            return redirect('core:contact')

        name = request.POST.get('name', '').strip()[:MAX_CONTACT_LEN["name"]]
        email = request.POST.get('email', '').strip().lower()[:MAX_CONTACT_LEN["email"]]
        phone = request.POST.get('phone', '').strip()[:MAX_CONTACT_LEN["phone"]]
        subject = request.POST.get('subject', '').strip()[:MAX_CONTACT_LEN["subject"]]
        message = request.POST.get('message', '').strip()[:MAX_CONTACT_LEN["message"]]

        try:
            validate_email(email)
            email_valid = True
        except ValidationError:
            email_valid = False

        if not name or not email or not message:
            messages.error(request, "لطفاً تمامی فیلدهای الزامی (نام، ایمیل و پیام) را تکمیل نمایید.")
        elif not email_valid:
            messages.error(request, "آدرس ایمیل وارد شده معتبر نیست.")
        else:
            ContactMessage.objects.create(
                name=name,
                email=email,
                phone=phone,
                subject=subject or "پیام از سایت",
                message=message
            )
            messages.success(request, "پیام شما با موفقیت ثبت شد. کارشناسان ما به زودی با شما تماس خواهند گرفت.")
            return redirect('core:contact')

    return render(request, 'core/contact.html', {'settings': site_settings})


@require_POST
def newsletter_subscribe_view(request):
    """
    Newsletter email subscription endpoint.
    """
    if _honeypot_triggered(request):
        return JsonResponse({'status': 'success', 'message': 'عضویت شما در خبرنامه با موفقیت انجام شد.'})

    email = request.POST.get('email', '').strip().lower()[:254]
    try:
        validate_email(email)
    except ValidationError:
        return JsonResponse({'status': 'error', 'message': 'لطفاً یک آدرس ایمیل معتبر وارد نمایید.'}, status=400)

    sub, created = NewsletterSubscription.objects.get_or_create(email=email)
    if not created and not sub.is_active:
        sub.is_active = True
        sub.save()

    return JsonResponse({'status': 'success', 'message': 'عضویت شما در خبرنامه با موفقیت انجام شد.'})


# Static Policy Pages
def about_view(request):
    settings = SiteSetting.get_settings()
    return render(request, 'core/about.html', {'settings': settings})

def faq_view(request):
    return render(request, 'core/faq.html')

def terms_view(request):
    settings = SiteSetting.get_settings()
    return render(request, 'core/policy_page.html', {
        'title': 'قوانین و مقررات',
        'content': settings.terms_and_conditions
    })

def privacy_view(request):
    settings = SiteSetting.get_settings()
    return render(request, 'core/policy_page.html', {
        'title': 'سیاست حریم خصوصی',
        'content': settings.privacy_policy
    })

def shipping_policy_view(request):
    settings = SiteSetting.get_settings()
    return render(request, 'core/policy_page.html', {
        'title': 'رویه ارسال سفارشات',
        'content': settings.shipping_policy
    })

def returns_policy_view(request):
    settings = SiteSetting.get_settings()
    return render(request, 'core/policy_page.html', {
        'title': 'رویه بازگردانی کالا',
        'content': settings.returns_policy
    })

def cookie_policy_view(request):
    settings = SiteSetting.get_settings()
    return render(request, 'core/policy_page.html', {
        'title': 'سیاست کوکی‌ها',
        'content': settings.cookie_policy
    })


# SEO: robots.txt
def robots_txt_view(request):
    lines = [
        "User-agent: *",
        "Disallow: /admin/",
        "Disallow: /accounts/",
        "Disallow: /cart/",
        "Disallow: /orders/checkout/",
        "Disallow: /payments/",
        "Disallow: /dashboard/",
        "",
        f"Sitemap: {request.build_absolute_uri(reverse('core:sitemap'))}"
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


# SEO: Dynamic Sitemap
def sitemap_xml_view(request):
    products = Product.objects.filter(is_active=True).values('slug', 'updated_at')
    categories = Category.objects.filter(is_active=True).values('slug', 'updated_at')

    xml_lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
        f'  <url><loc>{request.build_absolute_uri("/")}</loc><changefreq>daily</changefreq><priority>1.0</priority></url>',
        f'  <url><loc>{request.build_absolute_uri("/shop/")}</loc><changefreq>daily</changefreq><priority>0.9</priority></url>',
    ]

    for c in categories:
        url = request.build_absolute_uri(f"/category/{c['slug']}/")
        lastmod = c['updated_at'].strftime('%Y-%m-%d')
        xml_lines.append(f'  <url><loc>{url}</loc><lastmod>{lastmod}</lastmod><changefreq>weekly</changefreq><priority>0.8</priority></url>')

    for p in products:
        url = request.build_absolute_uri(f"/product/{p['slug']}/")
        lastmod = p['updated_at'].strftime('%Y-%m-%d')
        xml_lines.append(f'  <url><loc>{url}</loc><lastmod>{lastmod}</lastmod><changefreq>daily</changefreq><priority>0.8</priority></url>')

    xml_lines.append('</urlset>')
    return HttpResponse("\n".join(xml_lines), content_type="application/xml")


# Custom HTTP Error Handlers
def custom_400_view(request, exception=None):
    return render(request, 'errors/400.html', status=400)

def custom_403_view(request, exception=None):
    return render(request, 'errors/403.html', status=403)

def custom_404_view(request, exception=None):
    return render(request, 'errors/404.html', status=404)

def custom_500_view(request):
    return render(request, 'errors/500.html', status=500)

def set_language_direct(request, lang_code):
    if lang_code in ('en', 'fa'):
        from django.utils import translation
        translation.activate(lang_code)
        request.session['django_language'] = lang_code
        request.session['_language'] = lang_code
        referer = request.META.get('HTTP_REFERER') or '/'
        response = redirect(referer)
        response.set_cookie(
            'django_language',
            lang_code,
            max_age=365 * 24 * 60 * 60,
            path='/',
            samesite='Lax'
        )
        return response
    return redirect('/')

