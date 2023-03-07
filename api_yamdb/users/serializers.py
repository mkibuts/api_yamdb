import re
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from django.contrib.auth import get_user_model
import random

from .models import User

User = get_user_model()


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'username']

    def generate_code(self):
        random.seed()
        return str(random.randint(100000, 999999))

    def create(self, validated_data):
        return User.objects.create_user(
            email=validated_data.get('email'),
            username=validated_data.get('username'),
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
    username = serializers.CharField(max_length=150, required=False)
    first_name = serializers.CharField(max_length=150, required=False)
    last_name = serializers.CharField(max_length=150, required=False)
    email = serializers.EmailField(max_length=254, required=False)
    role = serializers.ChoiceField(read_only=True, choices=User.ROLE_CHOICES)

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

    def validate_username(self, username):
        if username == 'me':
            return 'Некорректный username'
        if not re.match(r'^[\w.@+-]+\Z', username):
            raise serializers.ValidationError(
                'Недопустимые символы')
        return username


# class UserPATCHSerializer(serializers.ModelSerializer):
#     # username = serializers.CharField(max_length=150, required=False,
#     #                                  read_only=True)
#     # first_name = serializers.CharField(max_length=150, required=False)
#     # last_name = serializers.CharField(max_length=150, required=False)
#     # email = serializers.EmailField(max_length=254, required=False,
#     #                                read_only=True)
#
#     class Meta:
#         fields = (
#             'username',
#             "email",
#             'first_name',
#             'last_name',
#             'bio',
#         )
#         model = User
#         read_only_fields = ('username', 'email')
#
#     # def create(self, serializer):
#     #     user = get_object_or_404(User, username=self.request.user)
#     #     username = user.username
#     #     email = user.email
#     #     serializers.save(email=email, username=username)
#
#     def validate_email(self, email):
#         MaxLengthValidator(254)(email)
#         return email
#
#     def validate_username(self, username):
#         if not User.objects.filter(username=username).exists():
#             return 'Нет такого пользователя!'
#         if username == 'me':
#             return 'Некорректный username'
#         RegexValidator(r'^[\w.@+-]+\Z')(username)
#         MaxLengthValidator(150)(username)
#         return username
