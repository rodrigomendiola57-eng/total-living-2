"""
Validación y asignación de fichas técnicas subidas (reemplaza PDF generado).
"""
import os

from django.core.exceptions import ValidationError

ALLOWED_TECHNICAL_SHEET_EXTENSIONS = {'.pdf', '.doc', '.docx'}
MAX_TECHNICAL_SHEET_BYTES = 15 * 1024 * 1024  # 15 MB

ACCEPT_ATTR = '.pdf,.doc,.docx,application/pdf,application/msword,application/vnd.openxmlformats-officedocument.wordprocessingml.document'


def validate_technical_sheet_upload(file_obj):
    if not file_obj:
        raise ValidationError('No se recibió ningún archivo de ficha técnica.')

    _, ext = os.path.splitext(file_obj.name or '')
    ext = ext.lower()
    if ext not in ALLOWED_TECHNICAL_SHEET_EXTENSIONS:
        raise ValidationError(
            'Formato no permitido. Usa PDF (.pdf) o Word (.doc, .docx).'
        )

    size = getattr(file_obj, 'size', None)
    if size and size > MAX_TECHNICAL_SHEET_BYTES:
        raise ValidationError('La ficha técnica supera el tamaño máximo permitido de 15 MB.')


def technical_sheet_basename(property_obj):
    if not property_obj.technical_sheet:
        return ''
    return os.path.basename(property_obj.technical_sheet.name)


def apply_technical_sheet(property_obj, *, uploaded_file=None, remove=False):
    """
    Actualiza el archivo de ficha técnica en una instancia Property (sin guardar).
    """
    if remove:
        if property_obj.technical_sheet:
            property_obj.technical_sheet.delete(save=False)
        property_obj.technical_sheet = None
        return

    if not uploaded_file:
        return

    validate_technical_sheet_upload(uploaded_file)
    if property_obj.technical_sheet:
        property_obj.technical_sheet.delete(save=False)
    property_obj.technical_sheet = uploaded_file
