from django.core.exceptions import ValidationError
from django.utils import timezone


def validate_rating(value):
    if (value > 10) or (value < 1):
        raise ValidationError(
            'Введите значение от 1 до 10')


def validate_year(year):
    if year > timezone.now().year:
        raise ValidationError(
            ('%(year)s год еще не наступил'),
            params={'year': year},
        )
