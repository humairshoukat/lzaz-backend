from rest_framework import serializers
from app.models import User


class AddUserSerializer(serializers.Serializer):
    name = serializers.CharField(required=True)
    email = serializers.EmailField(required=True)
    role = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    picture = serializers.FileField(required=False)


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    password = serializers.CharField(required=True)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email', 'role', 'profile_picture', 'account_access']


class ResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(required=True)
    hash = serializers.CharField(required=True)
    secret = serializers.CharField(required=True)


class PaginationSerializer(serializers.Serializer):
    page = serializers.IntegerField(required=False)
    limit = serializers.IntegerField(required=False)
    search = serializers.CharField(required=False)
