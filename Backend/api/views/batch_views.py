from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import F, Q
from django.utils import timezone
from datetime import timedelta
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from api.models import IngredientBatch, Ingredient
from api.serializers import (
    BatchListSerializer,
    BatchDetailSerializer,
    BatchCreateSerializer,
    BatchConsumeSerializer,
)
from api.permissions import IsManager, IsManagerOrStorekeeper, IsManagerOrStorekeeperOrBaker


class BatchViewSet(viewsets.ModelViewSet):
    """
    ViewSet for IngredientBatch management.
    
    Features:
    - Auto-generated batch_id (BATCH-1001, BATCH-1002, etc.)
    - Quantity tracking with FIFO ordering
    - Expiry date management and alerts
    - Cost tracking for financial reporting
    - Automatic ingredient total_quantity sync
    
    Endpoints:
    - GET    /api/batches/                  List all batches (paginated, filtered)
    - POST   /api/batches/                  Create new batch
    - GET    /api/batches/{id}/             Get batch details
    - PUT    /api/batches/{id}/             Full update
    - PATCH  /api/batches/{id}/             Partial update
    - DELETE /api/batches/{id}/             Delete batch
    
    Custom Actions:
    - GET    /api/batches/expiring/         Get batches expiring within 2 days
    - GET    /api/batches/{id}/consume/     Consume from batch (FIFO)
    - GET    /api/ingredients/{id}/batches/ Get all active batches for ingredient (FIFO)
    
    Filtering:
    - ?ingredient_id=1         Filter by ingredient
    - ?status=Active           Filter by status (Active, Expired, Used)
    - ?expiring_within=7       Batches expiring within N days
    - ?search=BATCH-1001       Search by batch_id or ingredient name
    - ?ordering=expire_date    Sort by field
    
    Permissions:
    - Storekeeper: Full CRUD (create, update, delete)
    - Manager: Full access (can do everything)
    - Baker: Read-only (list, detail)
    - Cashier & Others: No access
    """
    
    queryset = IngredientBatch.objects.all().select_related('ingredient_id').order_by('expire_date')
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['ingredient_id', 'status']
    search_fields = ['batch_id', 'ingredient_id__name']
    ordering_fields = ['made_date', 'expire_date', 'current_qty', 'status', 'created_at']
    ordering = ['expire_date', 'made_date']  # FIFO ordering
    pagination_class = None  # No pagination for batches
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return BatchListSerializer
        elif self.action == 'create':
            return BatchCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return BatchCreateSerializer
        elif self.action == 'consume':
            return BatchConsumeSerializer
        else:  # retrieve, custom actions
            return BatchDetailSerializer
    
    def get_permissions(self):
        """
        Return appropriate permission classes based on action.
        
        Permissions:
        - list/retrieve: Storekeeper OR Manager OR Baker (read-only)
        - create/update/delete: Storekeeper OR Manager (write operations)
        - consume: Storekeeper OR Manager (for stock deduction)
        """
        if self.action in ['list', 'retrieve', 'by_ingredient', 'expiring']:
            # All authenticated users can view batches
            self.permission_classes = [IsManagerOrStorekeeperOrBaker]
        elif self.action in ['create', 'update', 'partial_update', 'destroy', 'consume']:
            # Only Storekeeper and Manager can modify
            self.permission_classes = [IsManagerOrStorekeeper]
        else:
            self.permission_classes = [IsAuthenticated]
        return [permission() for permission in self.permission_classes]
    
    def perform_create(self, serializer):
        """Create new batch and trigger ingredient quantity sync"""
        serializer.save()
    
    def perform_update(self, serializer):
        """Update batch and trigger ingredient quantity sync"""
        serializer.save()
    
    def perform_destroy(self, instance):
        """Delete batch and trigger ingredient quantity sync"""
        instance.delete()
    
    @action(detail=False, methods=['get'], url_path='expiring')
    def expiring(self, request):
        """
        Get batches expiring within specified number of days.
        
        Query Parameters:
        - days: Number of days to check (default: 2)
        
        Example:
        - GET /api/batches/expiring/?days=7
        """
        days_param = request.query_params.get('days', 2)
        try:
            days = int(days_param)
        except (ValueError, TypeError):
            days = 2
        
        expiry_date_threshold = timezone.now() + timedelta(days=days)
        
        batches = self.queryset.filter(
            status='Active',
            expire_date__lte=expiry_date_threshold,
            expire_date__gt=timezone.now()
        ).order_by('expire_date')
        
        serializer = self.get_serializer(batches, many=True)
        return Response({
            'count': batches.count(),
            'expiring_within_days': days,
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'], url_path='expired')
    def expired(self, request):
        """
        Get all expired batches.
        
        Example:
        - GET /api/batches/expired/
        """
        expired_batches = self.queryset.filter(
            Q(status='Expired') | Q(expire_date__lt=timezone.now())
        ).order_by('-expire_date')
        
        serializer = self.get_serializer(expired_batches, many=True)
        return Response({
            'count': expired_batches.count(),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'], url_path='out-of-stock')
    def out_of_stock(self, request):
        """
        Get batches that are fully consumed (current_qty == 0).
        
        Example:
        - GET /api/batches/out-of-stock/
        """
        empty_batches = self.queryset.filter(current_qty=0).order_by('-updated_at')
        
        serializer = self.get_serializer(empty_batches, many=True)
        return Response({
            'count': empty_batches.count(),
            'results': serializer.data
        })
    
    @action(detail=True, methods=['post'], url_path='consume')
    def consume(self, request, pk=None):
        """
        Consume (use) a quantity from this batch.
        
        Request body:
        {
            "amount": 25.50
        }
        
        Returns:
        {
            "success": true,
            "message": "Consumed 25.50 from batch",
            "remaining": 74.50,
            "batch_id": "BATCH-1001"
        }
        
        Example:
        - POST /api/batches/1/consume/
          Body: {"amount": 10}
        """
        batch = self.get_object()
        serializer = BatchConsumeSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        amount = serializer.validated_data['amount']
        result = batch.consume(amount)
        
        if result['success']:
            # Return updated batch details
            updated_serializer = BatchDetailSerializer(batch)
            return Response({
                'message': result['message'],
                'batch': updated_serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'error': result['message']
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'], url_path='by-ingredient/(?P<ingredient_id>[0-9]+)')
    def by_ingredient(self, request, ingredient_id=None):
        """
        Get all active batches for a specific ingredient (FIFO order).
        
        Example:
        - GET /api/batches/by-ingredient/1/
        
        Returns batches ordered by expiry date (oldest first) for FIFO consumption.
        """
        try:
            ingredient = Ingredient.objects.get(id=ingredient_id)
        except Ingredient.DoesNotExist:
            return Response(
                {'error': f'Ingredient #{ingredient_id} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        batches = self.queryset.filter(
            ingredient_id=ingredient,
            status='Active',
            current_qty__gt=0
        ).order_by('expire_date')
        
        serializer = self.get_serializer(batches, many=True)
        return Response({
            'ingredient_id': ingredient.id,
            'ingredient_name': ingredient.name,
            'count': batches.count(),
            'total_available': ingredient.total_quantity,
            'results': serializer.data
        })
    
    @action(detail=False, methods=['post'], url_path='update-expiry-status')
    def update_expiry_status(self, request):
        """
        Auto-update expiry status for all batches.
        Marks batches as Expired if expire_date has passed.
        
        This endpoint can be called periodically or on-demand.
        
        Example:
        - POST /api/batches/update-expiry-status/
        
        Returns:
        {
            "updated_count": 5,
            "message": "Updated 5 batches",
            "expired_batches": [...]
        }
        """
        now = timezone.now()
        updated_batches = IngredientBatch.objects.filter(
            status='Active',
            expire_date__lt=now
        ).update(status='Expired')
        
        expired_batches = IngredientBatch.objects.filter(
            status='Expired'
        ).order_by('-expire_date')[:10]
        
        serializer = self.get_serializer(expired_batches, many=True)
        return Response({
            'updated_count': updated_batches,
            'message': f'Updated {updated_batches} batches',
            'recent_expired': serializer.data
        })
