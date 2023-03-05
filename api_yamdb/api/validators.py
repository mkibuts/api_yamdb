import re
from django.core.exceptions import ValidationError


def validate_categories_name(self, value):
    if len(value) > 256:
        raise ValidationError(
            'Слишком длинное название категории. Надо не более 256 символов'
        )


def validate_categories_slug(self, value):
    if not re.match(r'^[-a-zA-Z0-9_]+$', value):
        raise ValidationError(
            'недопустимые символы'
        )
    if len(value) > 50:
        raise ValidationError(
            'Слишком длинный слаг. Надо не более 50 символов'
        )
    return value
