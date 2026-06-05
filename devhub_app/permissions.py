from rest_framework.permissions import BasePermission


class IsOwnerObjectPermission(BasePermission):
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, "owner"):
            return obj.owner_id == request.user.id
        if hasattr(obj, "author"):
            return obj.author_id == request.user.id
        if hasattr(obj, "user"):
            return obj.user_id == request.user.id
        return False
