from django.db import models

from users.models import User
from .validators import validate_rating


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
