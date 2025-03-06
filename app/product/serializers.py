from rest_framework import serializers
from app.models import Product


class AddProductSerializer(serializers.Serializer):
    sku = serializers.CharField(required=True)
    name = serializers.CharField(required=True)
    description = serializers.CharField(required=True)
    price = serializers.FloatField(required=True)
    family = serializers.IntegerField(required=False)
    details = serializers.JSONField(required=False)
    images = serializers.ListField(required=False)
    is_archived = serializers.BooleanField(required=False, default=True)
    is_published = serializers.BooleanField(required=False, default=False)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'sku', 'name', 'description', 'price', 'family', 'details', 'is_archived', 'is_published']


class AddMultipleProductSerializer(serializers.Serializer):
    products = ProductSerializer(many=True)  # Accepts a list of product objects


class PaginationSerializer(serializers.Serializer):
    page = serializers.IntegerField(required=False)
    limit = serializers.IntegerField(required=False)
    search = serializers.CharField(required=False)
    is_archived = serializers.BooleanField(required=False)
    is_published = serializers.BooleanField(required=False)
