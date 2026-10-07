from django.urls import path, re_path
from . import views

app_name = 'catalog'

urlpatterns = [
    path('shop/', views.shop_list_view, name='shop'),
    path('shop/compare/', views.product_compare_view, name='compare'),
    path('api/search/', views.live_search_api_view, name='live_search_api'),
    re_path(r'^category/(?P<slug>[-\w]+)/$', views.category_detail_view, name='category_detail'),
    re_path(r'^brand/(?P<slug>[-\w]+)/$', views.brand_detail_view, name='brand_detail'),
    re_path(r'^product/(?P<slug>[-\w]+)/$', views.product_detail_view, name='product_detail'),
]
