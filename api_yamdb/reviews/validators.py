from django.core.exceptions import ValidationError


def validate_rating(value):
    if (value > 10) or (value < 1):
        raise ValidationError(
            'Введите значение от 1 до 10'
        )
