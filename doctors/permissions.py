from rest_framework.permissions import BasePermission


class IsStaffUser(BasePermission):
    """Allow access only to staff (is_staff=True) users."""

    def has_permission(self, request, view):
        return request.user and request.user.is_staff
