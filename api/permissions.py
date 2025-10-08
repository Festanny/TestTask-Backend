from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    Разрешение, предоставляющее доступ только администраторам.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)
