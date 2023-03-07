import re
from rest_framework import serializers
from rest_framework.generics import get_object_or_404
from django.contrib.auth import get_user_model

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
