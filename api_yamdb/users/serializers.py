import random

from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from .models import User


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
        return username


class VerifyUserSerializer(serializers.Serializer):
    username = serializers.CharField()
    confirmation_code = serializers.CharField()

    def create(self, validated_data):
        user = get_object_or_404(User, username=validated_data)
        user.is_active = True
        user.save()
        return user

    def validate_username(self, username):
        if not User.objects.filter(username=username).exists():
            raise serializers.ValidationError('Такого пользователя не '
                                              'существует!')
        return username

    def validate_confirmation_code(self, code):
        user = self.initial_data.get('username')

        access_code = get_object_or_404(User, username=user).confirmation_code
        if access_code != code:
            raise serializers.ValidationError(
                'Некорректный код подтверждения!')
        return code


class UserSerializer(serializers.ModelSerializer):

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
        if (User.objects.filter(username=username).exists()
                and User.objects.filter(username=username).is_active):
            raise serializers.ValidationError(
                'Это имя пользователя уже занято!'
            )
        return username