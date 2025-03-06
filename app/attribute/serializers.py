from rest_framework import serializers
from app.models import AttributeGroup


class AttributeGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = AttributeGroup
        fields = ['id', 'name', 'values']