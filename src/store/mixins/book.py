from django.db.models import Count, Case, When, Value, F
from typing import Sequence

from store.models import Book


class BookMixin:
    @classmethod
    def get_books_queryset(cls) -> Sequence:
        queryset = Book.objects.all().annotate(

            count_likes=Count(Case(When(
                userbookrelation__like=True,
                then=Value(1)
            ))),

            count_bookmarks=Count(Case(When(
                userbookrelation__is_bookmark=True,
                then=Value(1)
            ))),

            owner_name=F('owner__username'),

            end_price=Case(
                When(
                    discount__gt=0,
                    then=F('price') * (1 - F('discount'))),
                default=F('price')
            )
        ).select_related('owner').prefetch_related('reader')

        return queryset
