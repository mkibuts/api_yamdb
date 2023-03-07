import re
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from django.contrib.auth import get_user_model
import random
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, MaxLengthValidator

from users.models import User
from reviews.models import Category, Genre, Title, Review, Comment

User = get_user_model()


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        lookup_field = 'slug'
        fields = ('name', 'slug')

    def validate_name(self, value):
        if len(value) > 256:
            raise serializers.ValidationError(
                'Слишком длинное название категории'
            )
        return value

    def validate_slug(self, value):
        if not re.match(r"^[-a-zA-Z0-9_]+$", value):
            raise serializers.ValidationError(
                'недопустимые символы'
            )
        if len(value) > 50:
            raise serializers.ValidationError(
                'Слишком длинный слаг. Надо не более 50 символов'
            )
        return value


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        lookup_field = 'slug'
        fields = ('name', 'slug')


class TitleSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(read_only=True)
    genre = serializers.SlugRelatedField(
        slug_field='slug', many=True, queryset=Genre.objects.all()
    )
    category = CategorySerializer()

    class Meta:
        model = Title
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')


class ReviewSerializer(serializers.ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, data):
        request = self.context['request']
        if request.method != 'POST':
            return data

        title_id = self.context['view'].kwargs['title_id']
        title = get_object_or_404(Title, pk=title_id)
        if title.reviews.filter(author__id=request.user.id):
            raise serializers.ValidationError(
                'Вы не можете оставлять более одного отзыва.')
        return data


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
