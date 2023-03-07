from django.db import models

from users.models import User
from .validators import validate_rating, validate_year
from .utils import slugify


class CategoryGenreAbstract(models.Model):
    """
    Абстрактная модель, включающая поля slug и title, а также
    переопределенный метод save(), генерирующий slug при его отсутствии.
    """
    slug = models.SlugField(
        verbose_name='Slug',
        unique=True,
        max_length=50,
        blank=True,
        help_text='Если оставить пустым, то заполнится автоматически.'
    )
    name = models.CharField(
        verbose_name='Наименование',
        max_length=256,
    )

    class Meta:
        abstract = True
        ordering = ['-id']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name[:50])
        super().save(*args, **kwargs)


class Category(CategoryGenreAbstract):
    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ['-id']


class Genre(CategoryGenreAbstract):
    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ['-id']


class Title(models.Model):
    name = models.CharField(
        verbose_name='Название',
        max_length=256
    )
    year = models.IntegerField(
        verbose_name='Дата выхода',
        validators=[validate_year],
        blank=True
    )
    description = models.TextField(
        verbose_name='Описание',
        null=True,
        blank=True
    )
    genre = models.ManyToManyField(
        Genre,
        verbose_name='Жанр',
        through='GenreTitle'
    )
    category = models.ForeignKey(
        Category,
        verbose_name='Категория',
        on_delete=models.SET_NULL,
        related_name='titles',
        null=True
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ['-id']


class GenreTitle(models.Model):
    title = models.ForeignKey(
        Title,
        verbose_name='Произведение',
        on_delete=models.CASCADE)
    genre = models.ForeignKey(
        Genre,
        verbose_name='Жанр',
        on_delete=models.CASCADE)

    def __str__(self):
        return f'Произведение "{self.title}", жанр: {self.genre}'

    class Meta:
        verbose_name = 'Произведение и жанр'
        verbose_name_plural = 'Произведения и жанры'
        ordering = ['-id']


class ReviewCommentAbstract(models.Model):
    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
    )
    text = models.TextField(
        verbose_name='Текст'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата написания'
    )

    class Meta:
        abstract = True
        ordering = ['-id']

    def __str__(self):
        return self.text[:30]


class Review(ReviewCommentAbstract):
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        verbose_name='Тайтл',
        related_name='reviews'
    )
    score = models.SmallIntegerField(
        verbose_name='Оценка',
        validators=[validate_rating],
        help_text='От 1 до 10'
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        constraints = [
            models.UniqueConstraint(
                fields=['author', 'title'],
                name='one_author_review'
            )
        ]
        ordering = ['-id']


class Comment(ReviewCommentAbstract):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        verbose_name='Отзыв',
        related_name='comments'
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ['-id']
