import re

from django.core.exceptions import ValidationError


def hex_validator(color: str) -> str:
    """Проверяет является ли строка HEX кодом"""

    match = re.search(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', color)

    if not match:
        raise ValidationError('Value should be a HEX code')
    return color
