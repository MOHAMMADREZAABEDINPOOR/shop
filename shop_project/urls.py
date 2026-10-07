from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls', namespace='core')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('', include('catalog.urls', namespace='catalog')),
    path('cart/', include('cart.urls', namespace='cart')),
    path('orders/', include('orders.urls', namespace='orders')),
    path('payments/', include('payments.urls', namespace='payments')),
    path('reviews/', include('reviews.urls', namespace='reviews')),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
]

handler400 = 'core.views.custom_400_view'
handler403 = 'core.views.custom_403_view'
handler404 = 'core.views.custom_404_view'
handler500 = 'core.views.custom_500_view'

# Persian branding for the Admin panel
admin.site.site_header = '🛍️ مدیریت فروشگاه آوانگارد'
admin.site.site_title = 'پنل مدیریت آوانگارد'
admin.site.index_title = 'خوش آمدید — مدیریت کامل فروشگاه'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
