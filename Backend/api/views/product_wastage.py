from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Sum, Count
from django.utils import timezone
from datetime import timedelta

from api.models import ProductWastage, Product, WastageReason, User
from api.serializers import (
    ProductWastageListSerializer,
    ProductWastageDetailSerializer,
    ProductWastageCreateSerializer,
)


class ProductWastageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for product wastage management.
    
    Endpoints:
    - GET /api/product-wastages/ - List all wastages
    - POST /api/product-wastages/ - Create new wastage
    - GET /api/product-wastages/{id}/ - Get wastage details
    - DELETE /api/product-wastages/{id}/ - Delete wastage (Manager only)
    - GET /api/product-wastages/analytics/ - Wastage analytics
    """
    
    queryset = ProductWastage.objects.select_related(
        'product_id',
        'reason_id',
        'reported_by'
    ).all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action."""
        if self.action == 'create':
            return ProductWastageCreateSerializer
        elif self.action == 'retrieve':
            return ProductWastageDetailSerializer
        return ProductWastageListSerializer
    
    def get_permissions(self):
        """Set permissions based on action."""
        if self.action == 'destroy':
            # Only Manager can delete
            from rest_framework.permissions import IsAuthenticated
            # Will be checked in destroy method
            pass
        return super().get_permissions()
    
    def list(self, request, *args, **kwargs):
        """
        List all wastages with optional filters.
        
        Query parameters:
        - product_id: Filter by product
        - reason_id: Filter by reason
        - reported_by: Filter by reporter
        - date_from: Filter by start date (YYYY-MM-DD)
        - date_to: Filter by end date (YYYY-MM-DD)
        - min_loss: Filter by minimum loss amount
        """
        queryset = self.get_queryset()
        
        # Apply filters
        product_id = request.query_params.get('product_id')
        if product_id:
            queryset = queryset.filter(product_id=product_id)
        
        reason_id = request.query_params.get('reason_id')
        if reason_id:
            queryset = queryset.filter(reason_id=reason_id)
        
        reported_by = request.query_params.get('reported_by')
        if reported_by:
            queryset = queryset.filter(reported_by=reported_by)
        
        date_from = request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        
        date_to = request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
        
        min_loss = request.query_params.get('min_loss')
        if min_loss:
            queryset = queryset.filter(total_loss__gte=float(min_loss))
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request, *args, **kwargs):
        """
        Create a new product wastage record.
        Only Baker, Cashier, and Manager can create.
        """
        # Check permission
        user = request.user
        if user.role not in ['Baker', 'Cashier', 'Manager']:
            return Response(
                {'detail': 'Only Baker, Cashier, or Manager can report wastage.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Set reported_by to current user if not provided
        data = request.data.copy()
        if 'reported_by' not in data or not data['reported_by']:
            data['reported_by'] = user.id
        
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Return detail serializer in response
        detail_serializer = ProductWastageDetailSerializer(serializer.instance)
        return Response(detail_serializer.data, status=status.HTTP_201_CREATED)
    
    def retrieve(self, request, *args, **kwargs):
        """Retrieve wastage details."""
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete/undo wastage record.
        Only Manager can delete.
        Restores product stock.
        """
        user = request.user
        if user.role != 'Manager':
            return Response(
                {'detail': 'Only Manager can delete wastage records.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        instance = self.get_object()
        
        # Restore product stock
        product = instance.product_id
        product.current_stock += instance.quantity
        product.save()
        
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """
        Get wastage analytics.
        
        Returns:
        - Total wastage amount
        - Wastage by reason
        - Wastage by product
        - Daily wastage trend
        """
        queryset = self.get_queryset()
        
        # Apply optional date filters
        date_from = request.query_params.get('date_from')
        if date_from:
            queryset = queryset.filter(created_at__date__gte=date_from)
        
        date_to = request.query_params.get('date_to')
        if date_to:
            queryset = queryset.filter(created_at__date__lte=date_to)
        
        # Total wastage
        total_loss = queryset.aggregate(Sum('total_loss'))['total_loss__sum'] or 0
        total_quantity = queryset.aggregate(Sum('quantity'))['quantity__sum'] or 0
        total_count = queryset.count()
        
        # Wastage by reason
        by_reason = queryset.values('reason_id__reason').annotate(
            count=Count('id'),
            total_loss=Sum('total_loss'),
            total_quantity=Sum('quantity')
        ).order_by('-total_loss')
        
        # Wastage by product
        by_product = queryset.values('product_id__name').annotate(
            count=Count('id'),
            total_loss=Sum('total_loss'),
            total_quantity=Sum('quantity')
        ).order_by('-total_loss')[:10]  # Top 10
        
        # Daily trend (last 30 days)
        thirty_days_ago = timezone.now() - timedelta(days=30)
        daily_trend = queryset.filter(
            created_at__gte=thirty_days_ago
        ).values('created_at__date').annotate(
            total_loss=Sum('total_loss'),
            count=Count('id')
        ).order_by('created_at__date')
        
        return Response({
            'summary': {
                'total_loss': float(total_loss),
                'total_quantity': float(total_quantity),
                'total_records': total_count,
            },
            'by_reason': list(by_reason),
            'by_product': list(by_product),
            'daily_trend': list(daily_trend),
        })
    
    @action(detail=False, methods=['get'], url_path='product/(?P<product_id>[^/.]+)/history')
    def product_history(self, request, product_id=None):
        """
        Get wastage history for a specific product.
        
        Parameters:
        - product_id: Product ID
        """
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {'detail': 'Product not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        wastages = self.get_queryset().filter(product_id=product_id)
        
        # Apply pagination
        page = self.paginate_queryset(wastages)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(wastages, many=True)
        return Response(serializer.data)
