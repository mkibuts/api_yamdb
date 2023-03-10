from rest_framework import permissions


class IsAuthorOrStaffOrReadOnly(permissions.BasePermission):
    """
    Допускает к редактированию автора контента или модераторам и выше.
    """
    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user
                or request.user.is_admin
                or request.user.is_moderator
                or request.user.is_superuser)


class AdminOrReadOnly(permissions.BasePermission):
    """
    Допускает к редактированию только администраторов, остальным только чтение.
    """
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_admin
                or request.user.is_superuser)


class AdminOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.user.is_authenticated
                and request.user.is_admin
                or request.user.is_superuser)


class AuthorOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return request.user == obj.author
