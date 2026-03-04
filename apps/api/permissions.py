"""
Custom permissions for API endpoints
"""
from rest_framework import permissions


class IsStudent(permissions.BasePermission):
    """Allow access only to students"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_student


class IsTeacher(permissions.BasePermission):
    """Allow access only to teachers"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_teacher


class IsParent(permissions.BasePermission):
    """Allow access only to parents (when parent accounts are implemented)"""
    
    def has_permission(self, request, view):
        return request.user.is_authenticated and getattr(request.user, 'is_parent', False)


class IsStudentOrParent(permissions.BasePermission):
    """Allow access to students or their parents"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.is_student or getattr(request.user, 'is_parent', False)


class IsERPManagerOrDean(permissions.BasePermission):
    """Allow access only to ERP managers or deans"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.is_erp_manager or request.user.is_dean


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners to edit.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only to owner
        return obj.user == request.user
