"""
Custom permission classes for BakeryOS API
Implements role-based access control for all endpoints
"""

from rest_framework.permissions import BasePermission, IsAuthenticated


class IsManager(IsAuthenticated):
    """
    Permission class: Only Manager role can access
    Used for: Creating users, deleting users, managing discounts, etc.
    """
    def has_permission(self, request, view):
        return (
            super().has_permission(request, view) and 
            request.user.role == 'Manager'
        )


class IsManagerOrReadOnly(IsAuthenticated):
    """
    Permission class: Manager can do anything, others can only view
    Used for: Product management, ingredient management, etc.
    """
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        
        # Allow all authenticated users for safe methods
        if request.method in ['GET', 'HEAD', 'OPTIONS']:
            return True
        
        # Only Manager for write operations
        return request.user.role == 'Manager'


class IsManagerOrSelf(IsAuthenticated):
    """
    Permission class: Manager can manage anyone, users can update own profile
    Used for: User profile updates
    Restrictions:
    - Regular users can only update own profile
    - Users cannot change their own role or status
    - Only Manager can change role or status
    """
    def has_object_permission(self, request, view, obj):
        # Manager can do anything
        if request.user.role == 'Manager':
            return True
        
        # Users can only access their own profile
        if request.user.id == obj.id:
            # For PUT/PATCH, check if trying to change role/status
            if request.method in ['PUT', 'PATCH']:
                # If 'role' or 'status' in request data, deny
                if 'role' in request.data or 'status' in request.data:
                    return False
            return True
        
        # Otherwise deny
        return False


class IsStorekeeper(IsAuthenticated):
    """
    Permission class: Only Storekeeper role can access
    Used for: Ingredient and batch management
    """
    def has_permission(self, request, view):
        return (
            super().has_permission(request, view) and 
            request.user.role == 'Storekeeper'
        )


class IsBaker(IsAuthenticated):
    """
    Permission class: Only Baker role can access
    Used for: Production and batch creation
    """
    def has_permission(self, request, view):
        return (
            super().has_permission(request, view) and 
            request.user.role == 'Baker'
        )


class IsCashier(IsAuthenticated):
    """
    Permission class: Only Cashier role can access
    Used for: POS/Billing operations
    """
    def has_permission(self, request, view):
        return (
            super().has_permission(request, view) and 
            request.user.role == 'Cashier'
        )


class HasRolePermission(IsAuthenticated):
    """
    Permission class: Check specific role requirements
    Usage: 
        permission_classes = [HasRolePermission]
        required_roles = ['Manager', 'Cashier']
    """
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        
        # Get required roles from view if specified
        required_roles = getattr(view, 'required_roles', None)
        if required_roles is None:
            return True
        
        return request.user.role in required_roles


class CanManageUsers(IsAuthenticated):
    """
    Advanced permission: 
    - Only Manager can list/create/delete users
    - Anyone can view their own profile or get user details (if not restricted)
    - Users can update own profile (except role/status)
    """
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        
        # Manager can do anything
        if request.user.role == 'Manager':
            return True
        
        # Non-managers can only do GET on specific user details
        if request.method == 'GET':
            return True
        
        # Non-managers cannot list, create, or delete
        return False
    
    def has_object_permission(self, request, view, obj):
        # Manager can do anything
        if request.user.role == 'Manager':
            return True
        
        # Users can only GET their own profile
        if request.method == 'GET' and request.user.id == obj.id:
            return True
        
        # Users cannot PUT/PATCH/DELETE
        return False
