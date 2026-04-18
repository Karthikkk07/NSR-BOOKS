from rest_framework import serializers
from .models import Book, QueryCache

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'

class QueryCacheSerializer(serializers.ModelSerializer):
    class Meta:
        model = QueryCache
        fields = '__all__'
