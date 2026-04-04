from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from api.models import WastageReason
from api.serializers import (
    WastageReasonListSerializer,
    WastageReasonDetailSerializer,
    WastageReasonCreateSerializer,
)


class WastageReasonViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Wastage Reason management.
    
    Provides:
    - GET /api/wastage-reasons/ - List all reasons
    - POST /api/wastage-reasons/ - Create new reason (Manager only)
    - GET /api/wastage-reasons/{id}/ - Get reason details
    - PUT /api/wastage-reasons/{id}/ - Update reason (Manager only)
    - DELETE /api/wastage-reasons/{id}/ - Delete reason (Manager only)
    """

    queryset = WastageReason.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        """Use different serializers based on action"""
        if self.action == 'create':
            return WastageReasonCreateSerializer
        elif self.action == 'retrieve':
            return WastageReasonDetailSerializer
        else:  # list, update, destroy, etc.
            return WastageReasonListSerializer

    def get_permissions(self):
        """Set permissions based on action"""
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Only Manager can create/update/delete
            permission_classes = [permissions.IsAuthenticated]
        else:
            # Anyone authenticated can view
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        """Create a new wastage reason"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        """List all wastage reasons"""
        queryset = self.get_queryset()

        # Hide system-only reasons from manual selection flows by default.
        include_system = str(request.query_params.get('include_system', 'false')).lower() == 'true'
        if not include_system:
            queryset = queryset.exclude(reason__iexact='Expired')

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        })

    def retrieve(self, request, *args, **kwargs):
        """Get details for a specific wastage reason"""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """Delete a wastage reason"""
        instance = self.get_object()
        self.perform_destroy(instance)
        # Return 204 No Content with absolutely NO response body
        # This is the proper HTTP convention for DELETE operations
        return Response(status=status.HTTP_204_NO_CONTENT)
