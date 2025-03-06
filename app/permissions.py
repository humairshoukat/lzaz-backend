from rest_framework.permissions import BasePermission
from rest_framework.exceptions import AuthenticationFailed


class IsAuth(BasePermission):
    """
        Allows access only to authenticated users.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class IsAdmin(BasePermission):
    """
        Allows access only to authenticated admin users.
    """
    def has_permission(self, request, view):
        user = request.user
        return user and user.is_authenticated and user.role == 'admin'
