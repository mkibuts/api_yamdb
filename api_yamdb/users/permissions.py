from rest_framework import permissions


class AdminOnly(permissions.BasePermission):
    """
    Допускает только администраторов.
    """
    def has_permission(self, request, view):
        if request.user:
            return request.user.role == 'admin' or request.user.is_superuser
