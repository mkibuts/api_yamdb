import re
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from django.contrib.auth import get_user_model
import random

from .models import User

User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=254, required=True)
    username = serializers.CharField(max_length=150, required=True)

    class Meta:
        model = User
        fields = ['email', 'username']

    def generate_code(self):
        random.seed()
        return str(random.randint(100000, 999999))

    def create(self, validated_data):
        email = validated_data.get('email')
        username = validated_data.get('username')
        if User.objects.filter(email=email, username=username).exists():
            raise serializers.ValidationError('Не ваша почта или ник!')
        return User.objects.create_user(
            email=email,
            username=username,
            is_active=False,
            confirmation_code=self.generate_code()
        )

    def validate_username(self, username):
        if username == 'me':
            raise serializers.ValidationError('Недопустимый username!')
        if not re.match(r'^[\w.@+-]+\Z', username):
            raise serializers.ValidationError(
                'Недопустимые символы')
        return username

    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('Эта почта уже занята!')
        return email


class VerifyUserSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()

    def validate_username(self, username):
        if username is None:
            raise serializers.ValidationError('Обязательное поле!')
        if not User.objects.filter(username=username).exists():
            raise serializers.ValidationError('Такого пользователя не '
                                              'существует!')
        if not re.match(r'^[\w.@+-]+\Z', username):
            raise serializers.ValidationError(
                'Недопустимые символы')
        return username

    def validate_confirmation_code(self, code):
        user = self.initial_data.get('username')
        if user is None:
            raise serializers.ValidationError('Пользователь не найден')
        access_code = get_object_or_404(User, username=user).confirmation_code
        if access_code != code:
            raise serializers.ValidationError(
                'Некорректный код подтверждения!')
        return code


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=150, required=True)
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    email = serializers.EmailField(max_length=254, required=True)

    class Meta:
        fields = (
            'username',
            "email",
            'first_name',
            'last_name',
            'bio',
            'role'
        )
        model = User

    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError('Эта почта уже занята!')
        return email

    def validate_role(self, role):
        roles = self.fields.fields.get('role').choices
        if role not in roles:
            raise serializers.ValidationError('Недопустимая роль!')
        return role

    def validate_username(self, username):
        if User.objects.filter(username=username).exists():
            raise serializers.ValidationError('Этот username уже занят!')
        if username == 'me':
            return 'Некорректный username'
        if not re.match(r'^[\w.@+-]+\Z', username):
            raise serializers.ValidationError(
                'Недопустимые символы')
        return username


class UserPATCHSerializer(UserSerializer):
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES, required=False)
    username = serializers.CharField(max_length=150, required=True)


class UserMeSerializer(UserSerializer):
    username = serializers.CharField(max_length=150, required=False)
    email = serializers.EmailField(max_length=254, required=False)
    first_name = serializers.CharField(
        max_length=150,
        required=False,
        allow_blank=True
    )
    last_name = serializers.CharField(
        max_length=150,
        required=False,
        allow_blank=True
    )

    def validate_role(self, role):
        username = self.instance.username
        user = get_object_or_404(User, username=username)
        if get_object_or_404(User, username=user).role != 'admin':
            raise serializers.ValidationError('Вам нельзя себе поменять роль!')
        roles = self.fields.fields.get('role').choices
        if role not in roles:
            raise serializers.ValidationError('Недопустимая роль!')
        return role
