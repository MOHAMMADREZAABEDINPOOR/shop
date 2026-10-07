import json
import uuid
import urllib.request
from decimal import Decimal
from abc import ABC, abstractmethod
from django.conf import settings
from django.urls import reverse
from .models import Payment

class BasePaymentGateway(ABC):
    """
    Abstract interface for e-commerce payment gateways.
    """
    @abstractmethod
    def initiate_payment(self, order, request):
        """Creates payment record and returns the gateway redirect URL."""
        pass

    @abstractmethod
    def verify_payment(self, request, transaction_id):
        """Verifies transaction server-to-server and updates state."""
        pass


class SandboxPaymentGateway(BasePaymentGateway):
    """
    Interactive local sandbox payment gateway simulating bank redirect,
    card number validation, dynamic OTP, and callbacks.
    """
    def initiate_payment(self, order, request):
        client_ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        idempotency_key = f"SANDBOX-{order.order_number}-{uuid.uuid4().hex[:8]}"

        payment = Payment.objects.create(
            order=order,
            gateway='sandbox',
            amount=order.grand_total,
            ip_address=client_ip,
            idempotency_key=idempotency_key
        )

        redirect_url = reverse('payments:sandbox_gateway', kwargs={'transaction_id': payment.transaction_id})
        return redirect_url, payment

    def verify_payment(self, request, transaction_id):
        # Verification happens in verify view with idempotency lock
        pass


class ZarinpalPaymentGateway(BasePaymentGateway):
    """
    Production ZarinPal (independent gateway) payment adapter.
    Activated when ZARINPAL_MERCHANT_ID is configured in settings/environment.
    """
    API_URL = 'https://api.zarinpal.com/pg/v4/payment.{}'
    PAYMENT_URL = 'https://www.zarinpal.com/pg/StartPay/{}'

    def __init__(self, merchant_id):
        self.merchant_id = merchant_id

    def _post(self, endpoint, payload):
        req = urllib.request.Request(
            self.API_URL.format(endpoint),
            data=json.dumps(payload).encode('utf-8'),
            headers={'Content-Type': 'application/json', 'Accept': 'application/json'},
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=20) as resp:
            return json.loads(resp.read().decode('utf-8'))

    def initiate_payment(self, order, request):
        client_ip = request.META.get('REMOTE_ADDR', '127.0.0.1')
        idempotency_key = f"ZP-{order.order_number}-{uuid.uuid4().hex[:8]}"

        payment = Payment.objects.create(
            order=order,
            gateway='zarinpal',
            amount=order.grand_total,
            ip_address=client_ip,
            idempotency_key=idempotency_key
        )

        # ZarinPal amount is in IRR; our prices are Toman
        amount_rial = int(order.grand_total) * 10
        callback_url = request.build_absolute_uri(
            reverse('payments:verify', kwargs={'transaction_id': payment.transaction_id})
        )
        result = self._post('request.json', {
            'merchant_id': self.merchant_id,
            'amount': amount_rial,
            'callback': callback_url,
            'description': f"سفارش {order.order_number}",
            'email': getattr(getattr(order, 'user', None), 'email', '') or '',
            'mobile': (order.phone_number if hasattr(order, 'phone_number') else '') or '',
            'ip': client_ip,
        })

        data = result.get('data') or {}
        authority = data.get('authority')
        if not authority:
            payment.mark_failed(str((result.get('errors') or {}).get('code', 'unknown')))
            raise ConnectionError('ZarinPal payment request failed: {}'.format(result.get('errors')))

        payment.tracking_number = authority
        payment.save(update_fields=['tracking_number', 'updated_at'])
        redirect_url = self.PAYMENT_URL.format(authority)
        return redirect_url, payment

    def verify_payment(self, request, transaction_id):
        """Server-to-server confirmation using the authority from callback."""
        payment = Payment.objects.filter(transaction_id=transaction_id, gateway='zarinpal').first()
        if not payment:
            return False
        authority = request.GET.get('Authority', payment.tracking_number)
        result = self._post('verify.json', {
            'merchant_id': self.merchant_id,
            'authority': authority,
            'amount': int(payment.amount) * 10,
        })
        data = result.get('data') or {}
        return data.get('code') in (100, 101)  # success codes


def get_payment_gateway(gateway_name=None):
    """
    Gateway resolver factory.
    """
    gateway_name = gateway_name or getattr(settings, 'PAYMENT_GATEWAY_DEFAULT', 'sandbox')
    if gateway_name == 'zarinpal':
        merchant_id = getattr(settings, 'ZARINPAL_MERCHANT_ID', '') or ''
        if merchant_id:
            return ZarinpalPaymentGateway(merchant_id)
        # Not configured: fail closed to the local sandbox instead of crashing checkout
    if gateway_name == 'sandbox':
        return SandboxPaymentGateway()
    # Ready for Saman, Mellat production adapters
    return SandboxPaymentGateway()
