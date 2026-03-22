"""
User Management ViewSet for Task 2.3: User Management CRUD API
Implements all 6 endpoints with proper permission classes and validation
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django_filters.rest_framework import DjangoFilterBackend

from api.permissions import IsManager, IsManagerOrSelf
from api.serializers.user_serializers import (
    UserListSerializer,
    UserDetailSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
    UserStatusSerializer,
    UserMinimalSerializer
)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    Complete User Management API
    
    Endpoints:
    - GET /api/users/ (list all users - Manager only)
    - POST /api/users/ (create user - Manager only)
    - GET /api/users/{id}/ (get user details)
    - PUT /api/users/{id}/ (update user - Manager or self)
    - DELETE /api/users/{id}/ (delete user - Manager only)
    - PATCH /api/users/{id}/status/ (change status - Manager only)
    
    Permissions:
    - list: Manager only
    - create: Manager only
    - retrieve: Any authenticated user (self or Manager)
    - update: Self (limited) or Manager
    - partial_update: Self (limited) or Manager
    - destroy: Manager only
    - status action: Manager only
    """
    
    queryset = User.objects.all()
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'status']
    search_fields = ['username', 'full_name', 'email', 'employee_id', 'contact']
    ordering_fields = ['id', 'username', 'created_at', 'full_name', 'employee_id']
    ordering = ['-created_at']  # Default: newest first
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return UserListSerializer
        elif self.action == 'create':
            return UserCreateSerializer
        elif self.action == 'retrieve':
            return UserDetailSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        elif self.action == 'status':
            return UserStatusSerializer
        return UserDetailSerializer
    
    def get_permissions(self):
        """Return permission classes based on action"""
        if self.action == 'list':
            # Only Manager can list all users
            permission_classes = [IsManager]
        elif self.action == 'create':
            # Only Manager can create users
            permission_classes = [IsManager]
        elif self.action == 'retrieve':
            # Any authenticated user can view details (permission_object checks)
            permission_classes = [IsAuthenticated, IsManagerOrSelf]
        elif self.action in ['update', 'partial_update']:
            # Self can update own (limited), Manager can update anyone
            permission_classes = [IsAuthenticated, IsManagerOrSelf]
        elif self.action == 'destroy':
            # Only Manager can delete
            permission_classes = [IsManager]
        elif self.action == 'status':
            # Only Manager can change status
            permission_classes = [IsManager]
        elif self.action == 'managers':
            # Only Manager can list managers
            permission_classes = [IsManager]
        elif self.action == 'statistics':
            # Only Manager can view statistics
            permission_classes = [IsManager]
        elif self.action in ['reset_password']:
            # Only Manager can reset passwords
            permission_classes = [IsManager]
        elif self.action in ['change_password']:
            # Any authenticated user can change their own password
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]
        
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        """Return full queryset - permissions are checked at object level"""
        # Return all users - permission checks happen at object level
        return User.objects.all()
    
    def list(self, request, *args, **kwargs):
        """
        LIST /api/users/
        Get all users with filtering and search
        Manager only
        
        Query Parameters:
        - role: Filter by role (Manager, Cashier, Baker, Storekeeper)
        - status: Filter by status (active, inactive, suspended)
        - search: Search by username, full_name, email, employee_id, contact
        - ordering: Sort by id, username, created_at, full_name, employee_id
        
        Response: 200 OK with list of users
        """
        return super().list(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        """
        CREATE /api/users/
        Create a new user
        Manager only
        
        Request Body:
        {
            "username": "string",
            "password": "string (8+ chars, uppercase, lowercase, number)",
            "password_confirm": "string",
            "email": "string",
            "full_name": "string",
            "contact": "string",
            "nic": "string",
            "role": "Manager|Cashier|Baker|Storekeeper"
        }
        
        Response: 201 Created with user details
        Response: 400 Bad Request if validation fails
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Return the created user with full details (sans password)
        read_serializer = UserDetailSerializer(serializer.instance)
        return Response(read_serializer.data, status=status.HTTP_201_CREATED)
    
    def retrieve(self, request, *args, **kwargs):
        """
        RETRIEVE /api/users/{id}/
        Get specific user details
        Any authenticated user can view their own, Manager can view anyone
        
        Response: 200 OK with user details
        Response: 403 Forbidden if not authorized
        """
        instance = self.get_object()
        
        # Check permissions
        self.check_object_permissions(request, instance)
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def update(self, request, *args, **kwargs):
        """
        UPDATE /api/users/{id}/
        Update user (full update with PUT)
        Manager can update anyone, users can update own profile (limited fields)
        
        Self-update limitations:
        - Cannot change: role, status, is_active
        - Can change: email, full_name, contact, nic
        
        Manager can change: everything except password
        
        Response: 200 OK with updated user
        Response: 400 Bad Request if validation fails
        Response: 403 Forbidden if not authorized
        """
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        
        # Check permissions
        self.check_object_permissions(request, instance)
        
        # Restrict fields for non-managers updating themselves
        data = request.data.copy()
        if request.user.role != 'Manager' and request.user.id == instance.id:
            # Remove role, status for self-updates
            restricted_fields = ['role', 'status', 'is_active']
            for field in restricted_fields:
                data.pop(field, None)
        
        serializer = self.get_serializer(instance, data=data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """
        DELETE /api/users/{id}/
        Delete user (soft delete via status change)
        Manager only
        
        Note: We implement as soft delete - mark as inactive instead of removing
        
        Response: 204 No Content if successful
        Response: 403 Forbidden if not Manager
        """
        instance = self.get_object()
        
        # Prevent deleting self
        if request.user.id == instance.id:
            return Response(
                {'detail': 'Cannot delete your own account'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Soft delete: mark as inactive instead of removing from DB
        instance.status = 'inactive'
        instance.is_active = False
        instance.save()
        
        return Response(
            {'detail': 'User deleted (marked as inactive)'},
            status=status.HTTP_204_NO_CONTENT
        )
    
    @action(detail=True, methods=['patch'], permission_classes=[IsManager])
    def status(self, request, pk=None):
        """
        PATCH /api/users/{id}/status/
        Change user status (active, inactive, suspended)
        Manager only
        
        Request Body:
        {
            "status": "active|inactive|suspended"
        }
        
        Response: 200 OK with updated user
        Response: 400 Bad Request if validation fails
        Response: 403 Forbidden if not Manager
        """
        user = self.get_object()
        
        # Check if trying to change own status
        if request.user.id == user.id:
            return Response(
                {'detail': 'You cannot change your own status'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = UserStatusSerializer(
            user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        
        # Return full user details
        read_serializer = UserDetailSerializer(serializer.instance)
        return Response(read_serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """
        GET /api/users/me/
        Get current authenticated user's details
        
        Response: 200 OK with current user info
        """
        serializer = UserDetailSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], permission_classes=[IsManager])
    def managers(self, request):
        """
        GET /api/users/managers/
        Get all Manager users
        Manager only
        
        Response: 200 OK with list of managers
        """
        managers = User.objects.filter(role='Manager')
        serializer = UserMinimalSerializer(managers, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsManager])
    def reset_password(self, request, pk=None):
        """
        POST /api/users/{id}/reset_password/
        Reset user password to a temporary password
        Manager only
        
        Request Body:
        {
            "new_password": "string"
        }
        
        Note: In production, you'd generate a random password and send via email
        
        Response: 200 OK
        Response: 403 Forbidden if not Manager
        """
        user = self.get_object()
        new_password = request.data.get('new_password')
        
        if not new_password or len(new_password) < 8:
            return Response(
                {'detail': 'Password must be at least 8 characters'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(new_password)
        user.save()
        
        return Response(
            {'detail': f'Password reset for {user.username}'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def change_password(self, request, pk=None):
        """
        POST /api/users/{id}/change_password/
        Change own password (any user can change their own)
        
        Request Body:
        {
            "old_password": "string",
            "new_password": "string"
        }
        
        Response: 200 OK
        Response: 400 Bad Request if old password wrong
        Response: 403 Forbidden if not authorized
        """
        user = self.get_object()
        
        # Only allow changing own password
        if request.user.id != user.id:
            return Response(
                {'detail': 'You can only change your own password'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')
        
        if not old_password or not new_password:
            return Response(
                {'detail': 'Both old_password and new_password are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify old password
        if not user.check_password(old_password):
            return Response(
                {'detail': 'Old password is incorrect'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Set new password
        user.set_password(new_password)
        user.save()
        
        return Response(
            {'detail': 'Password changed successfully'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'], permission_classes=[IsManager])
    def statistics(self, request):
        """
        GET /api/users/statistics/
        Get user statistics (count by role, status, etc.)
        Manager only
        
        Response: 200 OK with stats
        """
        from django.db.models import Count
        
        stats = {
            'total_users': User.objects.count(),
            'active_users': User.objects.filter(status='active').count(),
            'by_role': dict(
                User.objects
                .values('role')
                .annotate(count=Count('id'))
                .values_list('role', 'count')
            ),
            'by_status': dict(
                User.objects
                .values('status')
                .annotate(count=Count('id'))
                .values_list('status', 'count')
            )
        }
        
        return Response(stats)
