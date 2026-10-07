from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('', views.cart_detail_view, name='detail'),
    path('api/add/', views.add_to_cart_api, name='api_add'),
    path('api/update/<int:item_id>/', views.update_cart_item_api, name='api_update'),
    path('api/remove/<int:item_id>/', views.remove_cart_item_api, name='api_remove'),
    path('api/mini-cart/', views.mini_cart_api, name='api_mini_cart'),
]
