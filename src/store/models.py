from copy import copy
from typing import TypeVar

from django.db import models
from django.contrib.auth import get_user_model


class Book(models.Model):
    name = models.CharField(max_length=150)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    author = models.CharField(max_length=150)
    owner = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        related_name='books'
    )
    reader = models.ManyToManyField(
        get_user_model(),
        through='UserBookRelation',
        related_name='reading_books'
    )
    discount = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        default=None
    )
    rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        default=None
    )

    def __str__(self):
        return f'id {self.pk} : {self.name}'


class UserBookRelation(models.Model):
    RATING = (
        (1, 'Bad'),
        (2, 'Not bad'),
        (3, 'Normal'),
        (4, 'Good'),
        (5, 'Excellent')
    )
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE
    )
    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE
    )
    rate = models.SmallIntegerField(
        choices=RATING,
        null=True,
        blank=True
    )
    like = models.BooleanField(default=False)
    is_bookmark = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.user.username} - {self.book.name} - RATE: {self.rate}'

    def save(self, *args, **kwargs):
        creating = not self.pk
        super().save(*args, **kwargs)
        # Чтобы rating пересчитывался, только когда он изменяется
        self._monitor_update_rate(self.rate)

        # Второе условие для обновления рейтинга при создании экземпляра модели
        if self.update_rate or creating:
            from .utils import set_rating
            # При обновлении экземпляра, пересчитываем рейтинг книги
            set_rating(self.book)
            self.set_rating_done = True
        else:
            self.set_rating_done = False

    def _monitor_update_rate(self, rate: None | models.SmallIntegerField) -> None:
        self.update_rate = False

        if not hasattr(self, '_rate'):
            self._rate = None
        if self._rate != rate and rate is not None:
            self._rate = rate
            self.update_rate = True

