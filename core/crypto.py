"""
Field-level encryption for sensitive PII at rest (Fernet / AES-128-CBC + HMAC).

Key management:
- Production: set DATA_ENCRYPTION_KEY env to a Fernet key (generate with
  `python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"`).
- Development fallback: derived deterministically from SECRET_KEY (documented,
  never use the fallback in production — see SECURITY.md).
"""
import base64
import hashlib

from django.conf import settings
from django.db import models

try:
    from cryptography.fernet import Fernet, InvalidToken
    _CRYPTO_AVAILABLE = True
except ImportError:  # pragma: no cover
    Fernet = None
    InvalidToken = Exception
    _CRYPTO_AVAILABLE = False

_ENCRYPTED_PREFIX = "enc1:"


def get_fernet():
    if not _CRYPTO_AVAILABLE:
        return None
    raw_key = getattr(settings, "DATA_ENCRYPTION_KEY", "") or ""
    if raw_key:
        key = raw_key.encode()
    else:
        # Dev fallback: derive a stable key from SECRET_KEY. Override in prod.
        digest = hashlib.sha256(f"shop-data-key::{settings.SECRET_KEY}".encode()).digest()
        key = base64.urlsafe_b64encode(digest)
    return Fernet(key)


def encrypt_value(plaintext):
    if plaintext is None or plaintext == "":
        return plaintext
    fernet = get_fernet()
    if fernet is None:
        return plaintext
    token = fernet.encrypt(str(plaintext).encode("utf-8")).decode("ascii")
    return f"{_ENCRYPTED_PREFIX}{token}"


def decrypt_value(value):
    if not value or not isinstance(value, str) or not value.startswith(_ENCRYPTED_PREFIX):
        return value
    fernet = get_fernet()
    if fernet is None:
        return value
    try:
        return fernet.decrypt(value[len(_ENCRYPTED_PREFIX):].encode("ascii")).decode("utf-8")
    except InvalidToken:
        return value


class EncryptedTextField(models.TextField):
    """TextField that transparently encrypts values before saving to the DB."""

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        if value is None:
            return value
        value = str(value)
        if value.startswith(_ENCRYPTED_PREFIX):
            return value
        return encrypt_value(value)

    def from_db_value(self, value, expression, connection):
        return decrypt_value(value)

    def to_python(self, value):
        value = super().to_python(value)
        return decrypt_value(value)


class EncryptedCharField(models.CharField):
    """CharField that transparently encrypts values before saving to the DB."""

    def get_prep_value(self, value):
        value = super().get_prep_value(value)
        if value is None:
            return value
        value = str(value)
        if value.startswith(_ENCRYPTED_PREFIX):
            return value
        return encrypt_value(value)

    def from_db_value(self, value, expression, connection):
        return decrypt_value(value)

    def to_python(self, value):
        value = super().to_python(value)
        return decrypt_value(value)
