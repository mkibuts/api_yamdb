from rest_framework import permissions


class IsAuthorOrStaffOrReadOnly(permissions.BasePermission):
    """
    Допускает к редактированию автора контента или модераторам и выше.
    """
    def has_object_permission(self, request, view, obj):
        staff = ('admin', 'moderator')
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user
                or request.user.role in staff
                or request.user.is_superuser)


class AdminOrReadOnly(permissions.BasePermission):
    """
    Допускает к редактированию только администраторов, остальным только чтение.
    """
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.role == 'admin'
                or request.user.is_superuser)
