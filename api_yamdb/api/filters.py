from django_filters import rest_framework as filters

from reviews.models import Title


class TitlesFilter(filters.FilterSet):
    category = filters.CharFilter(
        field_name='category__slug',
    )
    genre = filters.CharFilter(
        field_name='genre__slug',
    )

    class Meta:
        model = Title
        fields = ['name', 'year', 'category', 'genre']
