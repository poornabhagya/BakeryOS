from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, SAFE_METHODS
from rest_framework.pagination import PageNumberPagination
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.models import Q, Prefetch
from django.utils import timezone
from datetime import timedelta
from api.models import ProductBatch, Product
from api.services import produce_product
from api.serializers import (
    ProductBatchListSerializer,
    ProductBatchDetailSerializer,
    ProductBatchCreateSerializer,
    ProductBatchUpdateSerializer,
    ProductBatchUseBatchSerializer,
    ProductBatchExpiringSerializer,
)
from api.permissions import IsBaker, IsManagerOrBaker, IsManager, IsManagerOrStorekeeperOrBaker
from api.utils.query_optimization import OptimizedQueryMixin


class ProductBatchPagination(PageNumberPagination):
    """Custom pagination for product batch list endpoints"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class ProductBatchViewSet(OptimizedQueryMixin, viewsets.ModelViewSet):
    """
    ViewSet for Product Batch management with query optimization.
    
    Endpoints:
    - GET    /api/product-batches/        - List all batches (paginated)
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
    
    queryset = ProductBatch.objects.all()
    serializer_class = ProductBatchListSerializer
    pagination_class = ProductBatchPagination
    
    # Query optimization profiles
    optimized_relations = {
        'list': {
            'select_related': ['product_id'],
            'prefetch_related': [],
        },
        'retrieve': {
            'select_related': ['product_id'],
            'prefetch_related': ['stock_history'],
        },
        'expiring': {
            'select_related': ['product_id'],
            'prefetch_related': [],
        }
    }
    
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
        """Set permissions based on request type and action."""
        # Allow all authenticated users (including Cashier) to read batches/history.
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]

        # Restrict write operations.
        if self.action in ['create', 'update', 'partial_update', 'use_batch']:
            return [IsManagerOrBaker()]
        if self.action == 'destroy':
            return [IsManager()]

        # Fallback to manager-only for any other non-safe method.
        return [IsManager()]
    
    def get_queryset(self):
        """
        Filter batches based on query parameters.
        
        Supports:
        - product or product_id: Filter by product ID (e.g., ?product=1023)
        - status: Filter by batch status (e.g., ?status=Active)
        """
        queryset = ProductBatch.objects.all().select_related('product_id')
        
        # Get query parameters - support both 'product' and 'product_id' for compatibility
        product_param = self.request.query_params.get('product') or self.request.query_params.get('product_id')
        status = self.request.query_params.get('status')
        
        # Filter by product ID if provided
        if product_param:
            try:
                # Convert string parameter to integer
                product_id = int(product_param)
                # Filter by the product_id ForeignKey field
                queryset = queryset.filter(product_id=product_id)
            except (ValueError, TypeError) as e:
                # If conversion fails, log it and return empty queryset
                print(f"[ProductBatchViewSet] Invalid product_id parameter: {product_param}. Error: {e}")
                queryset = queryset.none()
        
        # Filter by status if provided
        if status:
            queryset = queryset.filter(status=status)
        
        return queryset
    
    def create(self, request, *args, **kwargs):
        """
        Create product stock through centralized production engine.

        Instead of serializer.save(), this endpoint now routes production to
        produce_product(product_id, quantity_to_produce), which performs:
        - strict ingredient FIFO deduction,
        - product running-balance increment,
        - product batch audit-log creation,
        - stock history creation.
        """
        product_id = request.data.get('product_id')
        quantity_to_produce = request.data.get('quantity')

        if product_id is None or quantity_to_produce is None:
            return Response(
                {'error': 'product_id and quantity are required'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            production_result = produce_product(
                product_id=int(product_id),
                quantity_to_produce=quantity_to_produce,
            )
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid product_id or quantity format'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except DjangoValidationError as exc:
            error_message = '; '.join(exc.messages) if getattr(exc, 'messages', None) else str(exc)
            return Response(
                {'error': error_message},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND,
            )

        created_batch = ProductBatch.objects.select_related('product_id').get(
            id=production_result['product_batch_id']
        )
        output_serializer = ProductBatchDetailSerializer(created_batch)
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
