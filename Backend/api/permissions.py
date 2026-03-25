"""
Custom permission classes for BakeryOS API
Implements role-based access control for all endpoints

Role Hierarchy:
- Manager: Full system access (users, products, ingredients, sales, wastage, discounts, analytics)
- Storekeeper: Ingredient & batch management (can read products, sales)
- Baker: Production & batch creation (can read ingredients, products, sales)
- Cashier: POS/Billing operations (can create sales, read products)
- Clerk: General staff (read-only access)

Permission Classes:
1. Single Role: IsManager, IsStorekeeper, IsBaker, IsCashier
2. Multiple Roles: IsManagerOrStorekeeper, IsManagerOrBaker, IsCashierOrManager, etc.
3. Special: IsManagerOrReadOnly, IsManagerOrSelf
"""

from rest_framework.permissions import BasePermission, IsAuthenticated


# ============================================================================
# SINGLE ROLE PERMISSION CLASSES
# ============================================================================

class IsManager(IsAuthenticated):
    """
    Permission class: Only Manager role can access
    Used for: User CRUD, product CRUD, discount CRUD, wastage deletion, analytics
    """
    def has_permission(self, request, view):
        return (
            super().has_permission(request, view) and 
            request.user.role == 'Manager'
        )


class IsStorekeeper(IsAuthenticated):
    """
    Permission class: Only Storekeeper role can access
    Used for: Ingredient and batch management specifically
    """
    def has_permission(self, request, view):
        return (
            super().has_permission(request, view) and 
            request.user.role == 'Storekeeper'
        )


class IsBaker(IsAuthenticated):
    """
    Permission class: Only Baker role can access
    Used for: Product batch creation and production management
    """
    def has_permission(self, request, view):
        return (
            super().has_permission(request, view) and 
            request.user.role == 'Baker'
        )


class IsCashier(IsAuthenticated):
    """
    Permission class: Only Cashier role can access
    Used for: POS/Billing/Sale creation operations
    """
    def has_permission(self, request, view):
        return (
            super().has_permission(request, view) and 
            request.user.role == 'Cashier'
        )


# ============================================================================
# MULTI-ROLE PERMISSION CLASSES
# ============================================================================

class IsManagerOrStorekeeper(IsAuthenticated):
    """
    Permission class: Manager or Storekeeper can access
    Used for: Ingredient CRUD (shared between Manager and Storekeeper)
    """
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.user.role in ['Manager', 'Storekeeper']


class IsManagerOrBaker(IsAuthenticated):
    """
    Permission class: Manager or Baker can access
    Used for: Production-related operations
    """
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.user.role in ['Manager', 'Baker']


class IsManagerOrStorekeeperOrBaker(IsAuthenticated):
    """
    Permission class: Manager, Storekeeper, or Baker can access
    Used for: Read-only access to ingredients/products for multiple roles
    """
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.user.role in ['Manager', 'Storekeeper', 'Baker']


class IsCashierOrManager(IsAuthenticated):
    """
    Permission class: Manager can view/delete all sales, Cashier can create sales
    Used for: Sales/POS operations with manager oversight
    """
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.user.role in ['Manager', 'Cashier']


class IsManagerOrReadOnly(IsAuthenticated):
    """
    Permission class: Manager can do anything, others can only view
    Used for: Product management, ingredient management, category management
    
    Allows:
    - Manager: GET, POST, PUT, PATCH, DELETE
    - Others: GET, HEAD, OPTIONS only
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
    Permission class: Manager can manage anyone, users can update own profile only
    Used for: User profile updates and self-service operations
    
    Features:
    - Manager: Full access to all user profiles
    - Regular users: Can only retrieve/update own profile
    - Restrictions: Regular users cannot change their role or status
    
    Has Object-Level Permissions:
    - Manager role bypasses object checks
    - Non-managers can only access objects they own (obj.id == request.user.id)
    - POST/PUT/PATCH: Non-managers cannot modify 'role' or 'status' fields
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
        
        # Otherwise deny - users cannot access other users' profiles
        return False


# ============================================================================
# WASTAGE-SPECIFIC PERMISSION CLASSES
# ============================================================================

class CanReportProductWastage(IsAuthenticated):
    """
    Permission class: Baker, Cashier, or Manager can report product wastage
    Used for: ProductWastage creation
    
    Allows:
    - Baker: Report wastage
    - Cashier: Report wastage (during sales operations)
    - Manager: Report and delete wastage
    """
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.user.role in ['Baker', 'Cashier', 'Manager']


class CanReportIngredientWastage(IsAuthenticated):
    """
    Permission class: Storekeeper or Manager can report ingredient wastage
    Used for: IngredientWastage creation
    
    Allows:
    - Storekeeper: Report ingredient wastage
    - Manager: Report and delete wastage
    """
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.user.role in ['Storekeeper', 'Manager']


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
