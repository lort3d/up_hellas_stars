from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAuthenticatedOrReadOnly(BasePermission):
    """
    Custom permission to only allow authenticated users to perform write operations,
    while allowing read operations for everyone.
    """
    def has_permission(self, request, view):
        # Allow read-only methods for everyone
        if request.method in SAFE_METHODS:
            return True
        # Require authentication for write operations
        return request.user and request.user.is_authenticated