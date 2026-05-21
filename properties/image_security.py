import os
import sys
from io import BytesIO

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import InMemoryUploadedFile
from PIL import Image


ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
MAX_IMAGE_SIZE_BYTES = 5 * 1024 * 1024  # 5 MB


def validate_image_upload(file_obj):
    """
    Valida extension y tamano maximo.
    """
    if not file_obj:
        raise ValidationError("No se recibio ningun archivo de imagen.")

    _, ext = os.path.splitext(file_obj.name or "")
    ext = ext.lower()
    if ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError("Formato no permitido. Usa: jpg, jpeg, png o webp.")

    size = getattr(file_obj, "size", None)
    if size and size > MAX_IMAGE_SIZE_BYTES:
        raise ValidationError("La imagen supera el tamano maximo permitido de 5 MB.")

    try:
        file_obj.seek(0)
        image = Image.open(file_obj)
        image.verify()
        file_obj.seek(0)
    except Exception as exc:
        raise ValidationError("El archivo no es una imagen valida.") from exc


def optimize_image_for_storage(file_obj, max_width=1920):
    """
    Redimensiona manteniendo proporcion si el ancho supera max_width.
    Conserva formato entre JPEG/PNG/WEBP.
    """
    file_obj.seek(0)
    image = Image.open(file_obj)

    original_format = (image.format or "").upper()
    if original_format not in {"JPEG", "JPG", "PNG", "WEBP"}:
        original_format = "JPEG"

    if image.width > max_width:
        new_height = int((max_width / image.width) * image.height)
        image = image.resize((max_width, new_height), Image.Resampling.LANCZOS)

    output = BytesIO()
    base_name, _ = os.path.splitext(file_obj.name)

    if original_format in {"JPEG", "JPG"}:
        if image.mode in ("RGBA", "LA", "P"):
            image = image.convert("RGB")
        image.save(output, format="JPEG", quality=88, optimize=True)
        filename = f"{base_name}.jpg"
        content_type = "image/jpeg"
    elif original_format == "PNG":
        image.save(output, format="PNG", optimize=True)
        filename = f"{base_name}.png"
        content_type = "image/png"
    else:
        if image.mode in ("RGBA", "LA", "P"):
            image = image.convert("RGBA")
        else:
            image = image.convert("RGB")
        image.save(output, format="WEBP", quality=85, method=6)
        filename = f"{base_name}.webp"
        content_type = "image/webp"

    output.seek(0)
    optimized = InMemoryUploadedFile(
        output,
        "ImageField",
        filename,
        content_type,
        sys.getsizeof(output),
        None,
    )
    return optimized
