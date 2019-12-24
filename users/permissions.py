from rest_framework import permissions

class IsAuthenticated(permissions.IsAuthenticated):
    def has_permission(self, request, view):
        return super(IsAuthenticatedOrCreate, self).has_permission(request, view)

class IsUser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.id == request.user.id