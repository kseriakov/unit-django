from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status

from ..mixins.book import BookMixin
from ..models import Book, UserBookRelation
from ..serializers import BookSerializer


class BookAPITest(APITestCase, BookMixin):
    def setUp(self) -> None:
        # Создаем пользователя для post запроса
        self.user = get_user_model().objects.create(username='user1')
        # Логинимся под созданным пользователем
        self.client.force_login(self.user)

        self.url = reverse('books-list')

        self._books = [
            Book.objects.create(
                name='Book 1',
                price=1000,
                author='Author1',
                owner=self.user,
                discount=0.5,
            ),
            Book.objects.create(
                name='Book 2',
                price=121,
                author='Author2'
            ),
            Book.objects.create(
                name='Book 2 Author1',
                price=121,
                author='Author3',
                owner=self.user
            ),
        ]

        UserBookRelation.objects.create(
            user=self.user,
            book=self._books[0],
            like=True,
            is_bookmark=True,
            rate=4
        )

        self.books = self.get_books_queryset()

        # Для проверки, что все поля, определенные в сериализаторе, выдаются
        self.serializer_fields = {
            item[0] for item in BookSerializer().get_fields()
        }

    def start_test(self, response, serializer_data, http_status):
        response_field_names = {
            item[0] for item in response.data[0]
        }

        self.assertEqual(http_status, response.status_code)
        self.assertEqual(response.data, serializer_data)
        self.assertEqual(
            self.serializer_fields,
            response_field_names
        )

    def test_get(self):
        serializer_data = BookSerializer(
            self.books,
            many=True
        ).data

        # Так можно посчитать сколько запросов было в менеджере
        with CaptureQueriesContext(connection) as queries:
            response = self.client.get(self.url)

        self.start_test(
            response,
            serializer_data,
            status.HTTP_200_OK
        )

    def test_search(self):
        books_data = self.get_books_queryset().filter(
            pk__in=(self._books[0].pk,
                    self._books[2].pk)
        )

        serializer_data = BookSerializer(
            books_data,
            many=True
        ).data

        response = self.client.get(
            self.url,
            {'search': 'Author1'}
        )
        self.start_test(
            response,
            serializer_data,
            status.HTTP_200_OK
        )

    def test_ordering_id(self):
        books_ordering_on_id = self.get_books_queryset(
        ).order_by('-id')

        serializer_data = BookSerializer(
            books_ordering_on_id,
            many=True
        ).data
        response = self.client.get(self.url, {'ordering': '-id'})

        self.start_test(
            response,
            serializer_data,
            status.HTTP_200_OK
        )

    def test_ordering_price(self):
        books_ordering_on_price = self.get_books_queryset(
        ).order_by('price')

        serializer_data = BookSerializer(
            books_ordering_on_price,
            many=True
        ).data

        response = self.client.get(
            self.url,
            {'ordering': 'price'}
        )

        self.start_test(
            response,
            serializer_data,
            status.HTTP_200_OK
        )

    def test_create(self):
        self.assertEqual(3, Book.objects.all().count())

        data = {
            'id': 4,
            'name': 'Book 4',
            'price': 4,
            'author': 'Author4',
        }

        response = self.client.post(self.url, data)

        self.assertEqual(
            status.HTTP_201_CREATED,
            response.status_code
        )
        self.assertEqual(4, Book.objects.all().count())

    def test_update(self):
        data = {
            'name': self._books[0].name,
            'price': 10100,
            'author': self._books[0].author,
        }

        url = reverse(
            'books-detail',
            kwargs={'pk': self._books[0].pk}
        )
        response = self.client.put(url, data)

        self._books[0].refresh_from_db()

        self.assertEqual(
            status.HTTP_200_OK,
            response.status_code
        )
        self.assertEqual(10100, self._books[0].price)

    def test_delete(self):
        url = reverse(
            'books-detail',
            kwargs={'pk': self._books[2].pk})
        response = self.client.delete(url)

        self.assertEqual(
            status.HTTP_204_NO_CONTENT,
            response.status_code
        )

        self.assertNotEqual(
            len(self._books),
            Book.objects.all().count()
        )

    def test_update_not_owner(self):
        data = {
            'name': self._books[1].name,
            'price': 1,
            'author': self._books[1].author,
        }

        url = reverse(
            'books-detail',
            kwargs={'pk': self._books[1].pk}
        )
        response = self.client.put(url, data)

        self._books[0].refresh_from_db()

        self.assertEqual(
            status.HTTP_403_FORBIDDEN,
            response.status_code
        )
        self.assertNotEqual(1, self._books[1].price)

    def test_delete_not_owner(self):
        url = reverse(
            'books-detail',
            kwargs={'pk': self._books[1].pk}
        )
        response = self.client.delete(url)

        self.assertEqual(
            status.HTTP_403_FORBIDDEN,
            response.status_code
        )
        self.assertEqual(len(self._books), Book.objects.all().count())


class UserBookRelationPITest(APITestCase):
    def setUp(self) -> None:
        self.users = [
            get_user_model().objects.create(username='user1'),
            get_user_model().objects.create(username='user2'),
            get_user_model().objects.create(username='user3'),
        ]

        self.books = [
            Book.objects.create(
                name='Book 1',
                price=1213,
                author='Author1',
                owner=self.users[0]
            ),
            Book.objects.create(
                name='Book 2',
                price=121,
                author='Author2',
                owner=self.users[1],
            ),
            Book.objects.create(
                name='Book 3',
                price=121,
                author='Author3',
                owner=self.users[2]
            ),
        ]

    def test_set_like(self):
        self.default(
            self.books[1],
            self.users[0],
            'like', True
        )

    def test_set_bookmark(self):
        self.default(
            self.books[0],
            self.users[1],
            'is_bookmark', True
        )

    def test_rate(self):
        self.default(
            self.books[2],
            self.users[2],
            'rate', 5
        )

    def test_wrong_rate(self):
        self.default(
            self.books[2],
            self.users[2],
            'rate', 10,
            status.HTTP_400_BAD_REQUEST
        )

    def default(
            self,
            book: Book,
            user: get_user_model(),
            attr: str,
            value_attr: int | bool,
            status_code: str = status.HTTP_200_OK
    ) -> None:
        url = reverse('relations-detail', args=(book.pk,))
        self.client.force_login(user)
        data = {attr: value_attr}

        response = self.client.patch(url, data)
        book.refresh_from_db()
        relation = UserBookRelation.objects.filter(
            user=user,
            book=book
        )
        self.assertEqual(status_code, response.status_code)
        if status_code == 200:
            self.assertNotEqual(0, len(relation))
            self.assertEqual(
                value_attr,
                relation.values()[0][attr]
            )
