import re
from datetime import datetime as d

from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from rest_framework.relations import SlugRelatedField
from django.contrib.auth.tokens import default_token_generator

from users.models import User
from reviews.models import Category, Genre, Title, Review, Comment


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('name', 'slug')
        lookup_field = 'slug'


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('name', 'slug')
        lookup_field = 'slug'


class TitleReadSerializer(serializers.ModelSerializer):
    rating = serializers.IntegerField(
        source='reviews__score__avg', read_only=True
    )
    genre = GenreSerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'rating', 'description', 'genre', 'category'
        )


class TitleCreateSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True
    )
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )

    class Meta:
        model = Title
        fields = (
            'id', 'name', 'year', 'description', 'genre', 'category'
        )

    def validate_year(self, value):
        current_year = d.now().year
        if value > current_year:
            raise serializers.ValidationError(
                f'Год не может указан больше текущего ({current_year}).'
            )
        return value


class CommentSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(read_only=True, slug_field='username')

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')


class ReviewSerializer(serializers.ModelSerializer):
    author = SlugRelatedField(
        read_only=True,
        slug_field='username',
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')

    def validate(self, data):
        request = self.context.get('request')
        if request.method != 'POST':
            return data

        title_id = self.context.get('view').kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if title.reviews.filter(author__id=request.user.id):
            raise serializers.ValidationError(
                'Вы не можете оставлять более одного отзыва.')
        return data


class RegistrationSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=254, required=True)
    username = serializers.CharField(max_length=150, required=True)

    class Meta:
        model = User
        fields = ['email', 'username']

    def create(self, validated_data):

        email = validated_data.get('email')
        username = validated_data.get('username')
        if User.objects.filter(email=email, username=username).exists():
            return User.objects.filter(email=email, username=username)
        else:
            if (User.objects.filter(username=username).exists()
                    or User.objects.filter(email=email).exists()):
                raise serializers.ValidationError(
                    {'username': ['Не ваша почта или ник!']}
                )
        return User.objects.create_user(
            email=email,
            username=username,
            is_active=False,
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
            raise serializers.ValidationError('Обязательное поле')
        if not re.match(r'^[\w.@+-]+\Z', username):
            raise serializers.ValidationError('Недопустимые символы')
        return username

    def validate_confirmation_code(self, code):
        username = self.initial_data.get('username')
        if username is None:
            raise serializers.ValidationError('Нельзя оставлять пустым')
        user = get_object_or_404(User, username=username)
        if not default_token_generator.check_token(user, code):
            raise serializers.ValidationError('Некорректный код')
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
        if not get_object_or_404(User, username=user).is_admin:
            raise serializers.ValidationError('Вам нельзя себе поменять роль!')
        roles = self.fields.fields.get('role').choices
        if role not in roles:
            raise serializers.ValidationError('Недопустимая роль!')
        return role

    def validate_username(self, username):
        try:
            get_object_or_404(User, username=username)
        except Exception:
            raise serializers.ValidationError('Пользователя не существует')
        return username
