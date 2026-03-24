from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.utils import timezone
from datetime import timedelta
from api.models import ProductBatch, Product
from api.serializers import (
    ProductBatchListSerializer,
    ProductBatchDetailSerializer,
    ProductBatchCreateSerializer,
    ProductBatchUpdateSerializer,
    ProductBatchUseBatchSerializer,
    ProductBatchExpiringSerializer,
)


class IsBaker(IsAuthenticated):
    """Permission: Only Baker role"""
    
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.user.role == 'Baker'


class IsBakerOrManager(IsAuthenticated):
    """Permission: Baker can create/use, Manager can do everything"""
    
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.user.role in ['Baker', 'Manager']


class IsStorekeeper(IsAuthenticated):
    """Permission: Only Storekeeper role"""
    
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.user.role == 'Storekeeper'


class IsStorkeeperOrManager(IsAuthenticated):
    """Permission: Storekeeper read-only, Manager full access"""
    
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.user.role in ['Storekeeper', 'Manager']


class IsManagerOnly(IsAuthenticated):
    """Permission: Only Manager role"""
    
    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return request.user.role == 'Manager'


class ProductBatchViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Product Batch management.
    
    Endpoints:
    - GET    /api/product-batches/        - List all batches
    - POST   /api/product-batches/        - Create batch (Baker)
    - GET    /api/product-batches/{id}/   - Get batch details
    - PUT    /api/product-batches/{id}/   - Update batch (Baker/Manager)
    - DELETE /api/product-batches/{id}/   - Delete batch (Manager)
    - GET    /api/product-batches/expiring/ - Get expiring soon (within 2 days)
    - GET    /api/products/{id}/batches/  - Get batches for specific product
    - POST   /api/product-batches/{id}/use-batch/ - Use batch quantity (Baker/Manager)
    
    Permissions:
    - Baker: Create batches, use batches, update own batches
    - Storekeeper: View only
    - Manager: Full access (CRUD + all operations)
    - Others: No access
    """
    
    queryset = ProductBatch.objects.all().prefetch_related('product_id')
    serializer_class = ProductBatchListSerializer
    permission_classes = [IsStorkeeperOrManager]
    
    def get_serializer_class(self):
        """Route to appropriate serializer based on action"""
        if self.action == 'create':
            return ProductBatchCreateSerializer
        elif self.action in ['retrieve']:
            return ProductBatchDetailSerializer
        elif self.action in ['update', 'partial_update']:
            return ProductBatchUpdateSerializer
        elif self.action == 'use_batch':
            return ProductBatchUseBatchSerializer
        elif self.action == 'get_expiring':
            return ProductBatchExpiringSerializer
        return ProductBatchListSerializer
    
    def get_permissions(self):
        """Set permissions based on action"""
        if self.action == 'create':
            return [IsBakerOrManager()]  # Baker can create, Manager can too
        elif self.action in ['update', 'partial_update']:
            return [IsBakerOrManager()]  # Baker can update, Manager can too
        elif self.action == 'use_batch':
            return [IsBakerOrManager()]  # Baker can use, Manager can too
        elif self.action == 'destroy':
            return [IsManagerOnly()]  # Only Manager can delete
        elif self.action == 'get_expiring':
            return [IsBakerOrManager()]  # Baker and Manager can check
        return [IsStorkeeperOrManager()]  # Storekeeper read-only, Manager full access
    
    def get_queryset(self):
        """Filter batches based on user role"""
        queryset = ProductBatch.objects.all().prefetch_related('product_id')
        
        # Apply filters
        product_id = self.request.query_params.get('product_id')
        status = self.request.query_params.get('status')
        
        if product_id:
            queryset = queryset.filter(product_id__id=product_id)
        
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        """
        Create a new product batch.
        
        When batch is created:
        1. Auto-generate batch_id (PROD-BATCH-1001, etc.)
        2. Auto-calculate expire_date from product.shelf_life
        3. Add quantity to product.current_stock
        4. Create ProductStockHistory entry for audit trail
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        batch = serializer.save()
        
        # Return created batch in detail format
        output_serializer = ProductBatchDetailSerializer(batch)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete a batch and deduct quantity from product stock.
        Only Manager can delete batches.
        """
        batch = self.get_object()
        batch.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['get'], url_path='expiring')
    def get_expiring(self, request):
        """
        Get batches expiring soon (within 2 days).
        
        Useful for prioritizing which batches to use first in production.
        """
        today = timezone.now().date()
        expiry_threshold = today + timedelta(days=2)
        
        expiring_batches = self.get_queryset().filter(
            expire_date__lte=expiry_threshold,
            expire_date__gte=today,
            status='Active'
        ).order_by('expire_date')
        
        serializer = self.get_serializer(expiring_batches, many=True)
        return Response({
            'count': expiring_batches.count(),
            'results': serializer.data
        })
    
    @action(detail=True, methods=['post'], url_path='use-batch')
    def use_batch(self, request, pk=None):
        """
        Use a quantity from the batch for production.
        Deducts used quantity from product stock and creates audit trail.
        """
        batch = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        quantity_used = serializer.validated_data['quantity_used']
        reason = serializer.validated_data.get('reason', 'Production use')
        
        # Try to use batch
        if batch.use_batch(quantity_used):
            return Response({
                'success': True,
                'message': f"Successfully used {quantity_used} units from batch {batch.batch_id}",
                'batch': ProductBatchDetailSerializer(batch).data
            })
        else:
            return Response(
                {
                    'success': False,
                    'error': f"Not enough quantity in batch. Available: {batch.quantity}"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'], url_path='product/(?P<product_id>[0-9]+)')
    def get_product_batches(self, request, product_id=None):
        """
        Get all batches for a specific product.
        Useful for production planning.
        """
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        batches = self.get_queryset().filter(
            product_id=product,
            status='Active'
        ).order_by('expire_date')
        
        serializer = self.get_serializer(batches, many=True)
        
        return Response({
            'product_id': product.id,
            'product_name': product.name,
            'total_quantity': sum(b.quantity for b in batches),
            'batch_count': batches.count(),
            'batches': serializer.data
        })
    
    @action(detail=False, methods=['get'], url_path='summary')
    def batch_summary(self, request):
        """
        Get summary of all batches.
        Shows total production quantity, expiring batches, etc.
        """
        all_batches = self.get_queryset()
        active_batches = all_batches.filter(status='Active')
        today = timezone.now().date()
        expiry_threshold = today + timedelta(days=2)
        
        expiring_batches = active_batches.filter(
            expire_date__lte=expiry_threshold,
            expire_date__gte=today
        )
        
        expired_batches = all_batches.filter(status='Expired')
        
        return Response({
            'total_batches': all_batches.count(),
            'active_batches': active_batches.count(),
            'active_quantity': sum(b.quantity for b in active_batches),
            'expiring_soon': expiring_batches.count(),
            'expired_batches': expired_batches.count(),
        })
