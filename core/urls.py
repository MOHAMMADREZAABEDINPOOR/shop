from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('faq/', views.faq_view, name='faq'),
    path('terms/', views.terms_view, name='terms'),
    path('privacy/', views.privacy_view, name='privacy'),
    path('shipping-policy/', views.shipping_policy_view, name='shipping_policy'),
    path('returns-policy/', views.returns_policy_view, name='returns_policy'),
    path('cookie-policy/', views.cookie_policy_view, name='cookie_policy'),
    path('newsletter/subscribe/', views.newsletter_subscribe_view, name='newsletter_subscribe'),
    path('lang/<str:lang_code>/', views.set_language_direct, name='set_language_direct'),
    path('robots.txt', views.robots_txt_view, name='robots_txt'),
    path('sitemap.xml', views.sitemap_xml_view, name='sitemap'),
]
