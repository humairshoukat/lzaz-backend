from rest_framework import serializers
from app.models import ProductFamily, AttributeGroup, ProductFamilyAttribute


class AttributeGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeGroup
        fields = ['id', 'name', 'values']


class ProductFamilySerializer(serializers.ModelSerializer):
    attribute_groups = serializers.SerializerMethodField()

    class Meta:
        model = ProductFamily
        fields = ['id', 'name', 'attribute_groups']

    def get_attribute_groups(self, obj):
        family_attributes = ProductFamilyAttribute.objects.filter(family=obj).values_list('attribute', flat=True)
        attribute_groups = AttributeGroup.objects.filter(id__in=family_attributes, deleted_at=None)
        serializer = AttributeGroupSerializer(attribute_groups, many=True)
        return serializer.data


class AddProductFamilySerializer(serializers.Serializer):
    name = serializers.CharField(required=False)
    attribute_groups = serializers.ListField(required=False)
    remove_attribute = serializers.BooleanField(required=False)
