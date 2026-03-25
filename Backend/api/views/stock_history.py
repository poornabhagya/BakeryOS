from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
from django.db.models import Q
from datetime import datetime, timedelta

from api.models import ProductStockHistory, IngredientStockHistory
from api.serializers.stock_history_serializer import (
    ProductStockHistoryListSerializer,
    ProductStockHistoryDetailSerializer,
    IngredientStockHistoryListSerializer,
    IngredientStockHistoryDetailSerializer
)
from api.utils.query_optimization import OptimizedQueryMixin


class StockHistoryPagination(PageNumberPagination):
    """Custom pagination for stock history list endpoints"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class ProductStockHistoryViewSet(OptimizedQueryMixin, viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing product stock history (audit trail) with query optimization.
    
    Provides read-only access to all product stock transactions
    including sales, batch additions, wastage, and adjustments.
    
    Features:
    - Filter by product, transaction type, date range
    - Search by bill number
    - List and detail views
    - Pagination support
    - Ordering support
    - Query optimized with select_related/prefetch_related
    """
    
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    pagination_class = StockHistoryPagination
    filterset_fields = ['product_id', 'transaction_type']
    ordering = ['-created_at']
    ordering_fields = ['created_at', 'change_amount', 'qty_before']
    
    # Query optimization profiles
    optimized_relations = {
        'list': {
            'select_related': ['product', 'performed_by'],
            'prefetch_related': [],
        },
        'retrieve': {
            'select_related': ['product', 'performed_by'],
            'prefetch_related': [],
        }
    }
    
    def get_queryset(self):
        """Get stock history with filters applied"""
        queryset = ProductStockHistory.objects.all()
        
        # Filter by date range if provided
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__gte=start)
            except ValueError:
                pass
        
        if end_date:
            try:
                end = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__lte=end)
            except ValueError:
                pass
        
        # Search by bill number
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(sale_bill_number__icontains=search)
            )
        
        return queryset
    
    def get_serializer_class(self):
        """Use different serializers for list and detail views"""
        if self.action == 'retrieve':
            return ProductStockHistoryDetailSerializer
        return ProductStockHistoryListSerializer
    
    @action(detail=False, methods=['get'])
    def by_product(self, request, **kwargs):
        """Get stock history for a specific product"""
        product_id = request.query_params.get('product_id')
        if not product_id:
            return Response(
                {'error': 'product_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        history = ProductStockHistory.objects.filter(
            product_id=product_id
        ).order_by('-created_at')
        
        serializer = self.get_serializer(history, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def date_range(self, request, **kwargs):
        """Get stock history within a date range"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            return Response(
                {'error': 'Both start_date and end_date parameters are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Date format should be YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        history = ProductStockHistory.objects.filter(
            created_at__date__gte=start,
            created_at__date__lte=end
        ).order_by('-created_at')
        
        serializer = self.get_serializer(history, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def summary(self, request, **kwargs):
        """Get summary of stock transactions by type"""
        product_id = request.query_params.get('product_id')
        
        queryset = ProductStockHistory.objects.all()
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        
        summary = {}
        for trans_type in ['AddStock', 'UseStock', 'ReturnStock', 'WasteStock', 'StockAdjustment']:
            transactions = queryset.filter(transaction_type=trans_type)
            summary[trans_type] = {
                'count': transactions.count(),
                'total_change': sum(t.change_amount for t in transactions) if transactions.exists() else 0
            }
        
        return Response(summary)


class IngredientStockHistoryViewSet(OptimizedQueryMixin, viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing ingredient stock history (audit trail) with query optimization.
    
    Provides read-only access to all ingredient stock transactions
    including batch additions, usage, wastage, and adjustments.
    
    Features:
    - Filter by ingredient, batch, transaction type, date range
    - List and detail views
    - Pagination support
    - Ordering support
    - Summary by transaction type
    - Query optimized with select_related/prefetch_related
    """
    
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    pagination_class = StockHistoryPagination
    filterset_fields = ['ingredient_id', 'batch_id', 'transaction_type']
    ordering = ['-created_at']
    ordering_fields = ['created_at', 'change_amount', 'qty_before']
    
    # Query optimization profiles
    optimized_relations = {
        'list': {
            'select_related': ['ingredient', 'batch', 'performed_by'],
            'prefetch_related': [],
        },
        'retrieve': {
            'select_related': ['ingredient', 'batch', 'performed_by'],
            'prefetch_related': [],
        }
    }
    
    def get_queryset(self):
        """Get stock history with filters applied"""
        queryset = IngredientStockHistory.objects.all()
        
        # Filter by date range if provided
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if start_date:
            try:
                start = datetime.strptime(start_date, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__gte=start)
            except ValueError:
                pass
        
        if end_date:
            try:
                end = datetime.strptime(end_date, '%Y-%m-%d').date()
                queryset = queryset.filter(created_at__date__lte=end)
            except ValueError:
                pass
        
        # Search by reference ID
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(reference_id__icontains=search) |
                Q(notes__icontains=search)
            )
        
        return queryset
    
    def get_serializer_class(self):
        """Use different serializers for list and detail views"""
        if self.action == 'retrieve':
            return IngredientStockHistoryDetailSerializer
        return IngredientStockHistoryListSerializer
    
    @action(detail=False, methods=['get'])
    def by_ingredient(self, request, **kwargs):
        """Get stock history for a specific ingredient"""
        ingredient_id = request.query_params.get('ingredient_id')
        if not ingredient_id:
            return Response(
                {'error': 'ingredient_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        history = IngredientStockHistory.objects.filter(
            ingredient_id=ingredient_id
        ).order_by('-created_at')
        
        serializer = self.get_serializer(history, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def by_batch(self, request, **kwargs):
        """Get stock history for a specific batch"""
        batch_id = request.query_params.get('batch_id')
        if not batch_id:
            return Response(
                {'error': 'batch_id parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        history = IngredientStockHistory.objects.filter(
            batch_id=batch_id
        ).order_by('-created_at')
        
        serializer = self.get_serializer(history, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def date_range(self, request, **kwargs):
        """Get stock history within a date range"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if not start_date or not end_date:
            return Response(
                {'error': 'Both start_date and end_date parameters are required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Date format should be YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        history = IngredientStockHistory.objects.filter(
            created_at__date__gte=start,
            created_at__date__lte=end
        ).order_by('-created_at')
        
        serializer = self.get_serializer(history, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def summary(self, request, **kwargs):
        """Get summary of stock transactions by type"""
        ingredient_id = request.query_params.get('ingredient_id')
        
        queryset = IngredientStockHistory.objects.all()
        if ingredient_id:
            queryset = queryset.filter(ingredient_id=ingredient_id)
        
        summary = {}
        for trans_type in ['AddStock', 'UseStock', 'Wastage', 'Adjustment']:
            transactions = queryset.filter(transaction_type=trans_type)
            summary[trans_type] = {
                'count': transactions.count(),
                'total_change': sum(t.change_amount for t in transactions) if transactions.exists() else 0
            }
        
        return Response(summary)
