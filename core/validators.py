"""Shared upload + input validators (defense-in-depth for user-supplied files)."""
from django.core.exceptions import ValidationError

MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB
ALLOWED_IMAGE_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_IMAGE_DIMENSION = 4096  # px (width or height)


def validate_image_upload(value):
    """Rejects oversized, spoofed or corrupt images before they touch storage."""
    if not value:
        return

    if getattr(value, "size", 0) > MAX_IMAGE_SIZE_BYTES:
        raise ValidationError("حجم تصویر نباید بیشتر از ۵ مگابایت باشد.")

    content_type = getattr(value, "content_type", "")
    if content_type and content_type not in ALLOWED_IMAGE_CONTENT_TYPES:
        raise ValidationError("فرمت تصویر مجاز نیست (فقط JPG، PNG و WebP).")

    name = (getattr(value, "name", "") or "").lower()
    if "." in name and not any(name.endswith(ext) for ext in ALLOWED_IMAGE_EXTENSIONS):
        raise ValidationError("پسوند فایل تصویر مجاز نیست.")

    # Verify actual image bytes with Pillow (catches renamed scripts).
    try:
        from PIL import Image

        value.seek(0)
        with Image.open(value) as img:
            img.verify()
        value.seek(0)
        with Image.open(value) as img:
            if max(img.size) > MAX_IMAGE_DIMENSION:
                raise ValidationError("ابعاد تصویر بیش از حد بزرگ است.")
        value.seek(0)
    except ValidationError:
        raise
    except Exception:
        raise ValidationError("فایل آپلودشده یک تصویر معتبر نیست.")
