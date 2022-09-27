from django.db.models import Count, Case, When, Value, Avg
from django.shortcuts import render, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.mixins import UpdateModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet, GenericViewSet

from .mixins.book import BookMixin
from .models import Book, UserBookRelation
from .permissions import IsOwnerOrStaffOrReadOnly
from .serializers import BookSerializer, UserBookRelationSerializer


class BookViewSet(ModelViewSet, BookMixin):
    serializer_class = BookSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    permission_classes = [IsOwnerOrStaffOrReadOnly]
    filterset_fields = ['price']
    search_fields = ['name', 'author']
    ordering_fields = ['id', 'price']

    def get_queryset(self):
        return self.get_books_queryset()

    def perform_create(self, serializer):
        serializer.validated_data['owner'] = self.request.user
        super().perform_create(serializer)


class UserBookRelationView(UpdateModelMixin, GenericViewSet):
    queryset = UserBookRelation.objects.all()
    serializer_class = UserBookRelationSerializer
    permission_classes = [IsAuthenticated]
    # Поле модели, которое будет использовано для поиска экземпляра UserBookRelation
    lookup_field = 'book_id'

    def get_object(self):
        filter_kwargs = {
            self.lookup_field: self.kwargs[self.lookup_field],
            'user_id': self.request.user.id
        }

        obj, _ = UserBookRelation.objects.get_or_create(**filter_kwargs)

        self.check_object_permissions(self.request, obj)

        return obj


def auth_github(request):
    return render(request, 'oauth.html')
