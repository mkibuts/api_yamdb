from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('moderator', 'Moderator'),
        ('user', 'User')
    ]
    role = models.CharField(
        verbose_name='Уровень доступа',
        choices=ROLE_CHOICES,
        max_length=9,
        default='user',
    )
    bio = models.TextField(
        verbose_name='Биография',
        blank=True,
    )
    email = models.EmailField(
        verbose_name='email',
        unique=True
    )
    confirmation_code = models.CharField(
        verbose_name='Код подтверждения',
        max_length=32,
        null=True
    )
    password = models.CharField(
        verbose_name='Пароль',
        max_length=128,
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
