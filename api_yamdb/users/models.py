from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    CONFIRMATION_CODE = 'confirmation_code'

    CHOICES = (
        (USER, 'user'),
        (MODERATOR, 'moderator'),
        (ADMIN, 'admin'),
    )
    username = models.CharField(
        'Имя пользователя',
        unique=True,
        blank=False,
        max_length=150
    )
    email = models.EmailField('email', unique=True)
    bio = models.TextField('Биография', blank=True)
    role = models.CharField(
        'Роль',
        max_length=255,
        choices=CHOICES,
        default=USER
    )
    confirmation_code = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=False)
