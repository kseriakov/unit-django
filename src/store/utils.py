from django.db.models import Avg

from store.models import UserBookRelation


def set_rating(book):
    data = UserBookRelation.objects.filter(
        book=book).aggregate(rating=Avg('rate'))
    rating = data.get('rating')

    if rating:
        book.rating = rating
        book.save()