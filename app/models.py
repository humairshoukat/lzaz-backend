from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=255, blank=True, null=True)
    profile_picture = models.URLField(blank=True, null=True)
    account_access = models.BooleanField(default=True)
    hash = models.CharField(max_length=511, blank=True, null=True)
    secret = models.CharField(max_length=511, blank=True, null=True)
    hash_secret_expired = models.BooleanField(default=False)
    forgot_password = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return "{}".format(self.email)


class AttributeGroup(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    values = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)


class ProductFamily(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)


class ProductFamilyAttribute(models.Model):
    family = models.ForeignKey(ProductFamily, on_delete=models.CASCADE)
    attribute = models.ForeignKey(AttributeGroup, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)


class Product(models.Model):
    sku = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)
    description = models.CharField(max_length=4095, blank=True, null=True)
    price = models.FloatField(blank=True, null=True)
    family = models.ForeignKey(ProductFamily, on_delete=models.CASCADE, blank=True, null=True)
    details = models.JSONField(blank=True, null=True)
    images = models.JSONField(blank=True, null=True)
    is_archived = models.BooleanField(default=True)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)
