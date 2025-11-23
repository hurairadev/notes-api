from rest_framework.permissions import BasePermission


class CanUpdateRetrieveDeleteNote(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_authenticated:
            return obj.user.id == request.user.id
        return False
