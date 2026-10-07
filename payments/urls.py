from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('initiate/<str:order_number>/', views.initiate_payment_view, name='initiate'),
    path('sandbox/<uuid:transaction_id>/', views.sandbox_gateway_view, name='sandbox_gateway'),
    path('verify/<uuid:transaction_id>/', views.verify_payment_view, name='verify'),
    path('result/<uuid:transaction_id>/', views.payment_result_view, name='result'),
]
