from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.dashboard_overview_view, name='overview'),
    path('orders/', views.dashboard_orders_view, name='orders'),
    path('orders/<str:order_number>/status/', views.dashboard_update_order_status_view, name='update_order_status'),
    path('inventory/', views.dashboard_inventory_view, name='inventory'),
    path('reports/', views.dashboard_reports_view, name='reports'),
    path('reports/export-orders/', views.dashboard_export_orders_csv_view, name='export_orders_csv'),
    # Employer / Staff Product Management Routes
    path('products/', views.dashboard_products_list_view, name='products'),
    path('products/create/', views.dashboard_product_create_view, name='product_create'),
    path('products/<int:pk>/edit/', views.dashboard_product_edit_view, name='product_edit'),
    path('products/<int:pk>/discount/', views.dashboard_product_quick_discount_view, name='product_quick_discount'),
    path('products/<int:pk>/toggle/', views.dashboard_product_toggle_view, name='product_toggle'),
    path('products/<int:pk>/delete/', views.dashboard_product_delete_view, name='product_delete'),
]
