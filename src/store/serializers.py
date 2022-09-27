from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Book, UserBookRelation


class BookReadersSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['id', 'username']


class BookSerializer(serializers.ModelSerializer):
    count_likes = serializers.IntegerField(read_only=True)
    count_bookmarks = serializers.IntegerField(read_only=True)
    end_price = serializers.DecimalField(
        read_only=True,
        max_digits=7,
        decimal_places=2,
    )
    owner_name = serializers.CharField(
        read_only=True,
        default=None
    )
    # На поле reader - вешаем сериализатор
    reader = BookReadersSerializer(many=True, read_only=True)

    class Meta:
        model = Book
        fields = [
            'id',
            'name',
            'price',
            'author',
            'count_likes',
            'rating',
            'count_bookmarks',
            'owner_name',
            'reader',
            'discount',
            'end_price',
        ]


class UserBookRelationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserBookRelation
        fields = ['book', 'rate', 'like', 'is_bookmark']
