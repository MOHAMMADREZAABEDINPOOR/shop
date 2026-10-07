"""Image compression helpers (smaller files = faster pages, cheaper hosting)."""
import io

COMPRESSED_MAX_SIZE = (1600, 1600)
COMPRESSED_QUALITY = 82


def compress_image_field(field_file, max_size=COMPRESSED_MAX_SIZE, quality=COMPRESSED_QUALITY):
    """Downscales + re-encodes an ImageFieldFile in place. Never raises."""
    if not field_file:
        return
    try:
        from PIL import Image

        storage = field_file.storage
        if not storage.exists(field_file.name):
            return

        with storage.open(field_file.name, "rb") as f:
            raw = f.read()
        original_bytes = len(raw)

        with Image.open(io.BytesIO(raw)) as img:
            fmt = (img.format or "JPEG").upper()
            if fmt not in ("JPEG", "PNG", "WEBP"):
                return
            if max(img.size) <= max(max_size) and original_bytes <= 400 * 1024:
                return  # Already small enough.

            img = img.copy()
            if img.mode in ("RGBA", "LA", "PA"):
                background = Image.new("RGB", img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])
                img = background
            elif img.mode != "RGB":
                img = img.convert("RGB")

            img.thumbnail(max_size, Image.LANCZOS)
            buffer = io.BytesIO()
            save_format = "JPEG" if fmt in ("JPEG", "PNG") else "WEBP"
            img.save(buffer, format=save_format, quality=quality, optimize=True)
            buffer.seek(0)
            storage.delete(field_file.name)
            storage.save(field_file.name, buffer)
    except Exception:
        return
