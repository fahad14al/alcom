from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        # Ensure obj has a 'store' and 'owner' attribute to check
        if hasattr(obj, 'store') and hasattr(obj.store, 'owner'):
            return obj.store.owner == request.user
        return False

class IsSeller(permissions.BasePermission):
    """
    Allows access only to users who are marked as sellers.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            hasattr(request.user, 'type') and 
            request.user.type == 'SELLER'
        )

class IsStoreOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of a store to edit it.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user