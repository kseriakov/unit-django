from django.contrib.auth import get_user_model as user
from django.test import TestCase

from ..mixins.book import BookMixin
from ..serializers import BookSerializer
from ..models import Book, UserBookRelation


class BookSerializerTest(TestCase, BookMixin):
    def setUp(self) -> None:
        self.user_1 = user().objects.create(username='user_1')
        self.user_2 = user().objects.create(username='user_2')
        self.user_3 = user().objects.create(username='user_3')

        self.book_data_1 = {
            'name': 'Test srl1',
            'price': 100,
            'author': 'author1',
            'discount': 0.5,
            'owner': self.user_1,
        }

        self.book_data_2 = {
            'name': 'Test srl2',
            'price': 112,
            'author': 'author2',
            'owner': self.user_2,
        }

        self.book_data_3 = {
            'name': 'Test srl3',
            'price': 113,
            'author': 'author3',
            'owner': self.user_3,
        }

        self.book_1 = Book.objects.create(**self.book_data_1)
        self.book_2 = Book.objects.create(**self.book_data_2)
        self.book_3 = Book.objects.create(**self.book_data_3)

        UserBookRelation.objects.create(
            user=self.user_1,
            book=self.book_1,
            like=True,
            is_bookmark=True,
            rate=5,
        )
        UserBookRelation.objects.create(
            user=self.user_2,
            book=self.book_1,
            like=True,
            is_bookmark=True,
            rate=4
        )
        UserBookRelation.objects.create(
            user=self.user_3,
            book=self.book_3,
            like=True,
            rate=3
        )
        UserBookRelation.objects.create(
            user=self.user_3,
            book=self.book_2,
        )

        self.srl_book_data = [
            {
                'id': self.book_1.id,
                'name': 'Test srl1',
                'price': '100.00',
                'author': 'author1',
                'count_likes': 2,
                'rating': '4.50',
                'count_bookmarks': 2,
                'owner_name': self.user_1.username,
                'reader': [
                    {
                        'id': self.user_1.id,
                        'username': self.user_1.username,
                    },
                    {
                        'id': self.user_2.id,
                        'username': self.user_2.username,
                    },
                ],
                'discount': '0.50',
                'end_price': '50.00'
            },
            {
                'id': self.book_2.id,
                'name': 'Test srl2',
                'price': '112.00',
                'author': 'author2',
                'count_likes': 0,
                'rating': None,
                'count_bookmarks': 0,
                'owner_name': self.user_2.username,
                'reader': [
                    {
                        'id': self.user_3.id,
                        'username': self.user_3.username,
                    },
                ],
                'discount': None,
                'end_price': '112.00',
            },
            {
                'id': self.book_3.id,
                'name': 'Test srl3',
                'price': '113.00',
                'author': 'author3',
                'count_likes': 1,
                'rating': '3.00',
                'count_bookmarks': 0,
                'owner_name': self.user_3.username,
                'reader': [
                    {
                        'id': self.user_3.id,
                        'username': self.user_3.username
                    },
                ],
                'discount': None,
                'end_price': '113.00',
            }
        ]

    def test_equal(self):
        data = self.get_books_queryset().order_by('id')
        serializer_data = BookSerializer(data, many=True).data

        self.assertEqual(self.srl_book_data, serializer_data)

    def test_update_book(self):
        relation = UserBookRelation.objects.create(
            user=self.user_3,
            book=self.book_1,
        )
        relation.like = True
        relation.save()

        self.assertFalse(relation.set_rating_done)
        self.assertFalse(relation.update_rate)

        relation.rate = 3
        relation.save()

        self.assertTrue(relation.set_rating_done)
        self.assertTrue(relation.update_rate)

        relation.like = False
        relation.save()

        self.assertFalse(relation.set_rating_done)
        self.assertFalse(relation.update_rate)

