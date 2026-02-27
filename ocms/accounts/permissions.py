# accounts/permissions.py
from rest_framework import permissions

class IsInstructor(permissions.BasePermission):
    """
    Permission to only allow instructors to access.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'INSTRUCTOR'

class IsAdmin(permissions.BasePermission):
    """
    Permission to only allow admins to access.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'ADMIN'

class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow admins to edit.
    Read-only allowed for anyone.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role == 'ADMIN'

class IsInstructorOrReadOnly(permissions.BasePermission):
    """
    Allow instructors to edit, others to read.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_authenticated and request.user.role == 'INSTRUCTOR'

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to allow owners to edit.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.instructor == request.user