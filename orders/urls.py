from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('checkout/', views.checkout_view, name='checkout'),
    path('api/apply-coupon/', views.apply_coupon_api, name='apply_coupon'),
    path('api/remove-coupon/', views.remove_coupon_api, name='remove_coupon'),
    path('success/<str:order_number>/', views.order_success_view, name='order_success'),
    path('cancel/<str:order_number>/', views.order_cancel_view, name='order_cancel'),
]
