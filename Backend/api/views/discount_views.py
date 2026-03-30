from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from django.db.models import Q, Prefetch
from datetime import datetime

from api.models import Discount, Product, Category
from api.serializers import (
    DiscountListSerializer,
    DiscountDetailSerializer,
    DiscountCreateSerializer,
    DiscountValidationSerializer,
    DiscountApplySerializer,
)
from api.permissions import IsManager
from api.utils.query_optimization import OptimizedQueryMixin


class DiscountPagination(PageNumberPagination):
    """Custom pagination for discount list endpoints"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class DiscountViewSet(OptimizedQueryMixin, viewsets.ModelViewSet):
    """
    ViewSet for Discount management with query optimization.
    
    Features:
    - Full CRUD on discounts
    - List active discounts
    - Validate if discount applies to product
    - Calculate discount amount
    - Toggle active/inactive
    
    Endpoints:
    - GET /api/discounts/ - List all discounts (Manager, paginated)
    - POST /api/discounts/ - Create discount (Manager)
    - GET /api/discounts/{id}/ - Get discount details
    - PUT /api/discounts/{id}/ - Update discount (Manager)
    - DELETE /api/discounts/{id}/ - Delete discount (Manager)
    - GET /api/discounts/active/ - Get active discounts
    - PATCH /api/discounts/{id}/toggle/ - Toggle active/inactive (Manager)
    - POST /api/discounts/{id}/validate/ - Check if applies to product
    - POST /api/discounts/{id}/apply/ - Calculate discount amount
    
    Permissions:
    - Manager: Full CRUD + all actions
    - Others: Read-only or no access
    """
    
    queryset = Discount.objects.all()
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    pagination_class = DiscountPagination
    
    # Query optimization profiles
    optimized_relations = {
        'list': {
            'select_related': ['target_category_id', 'target_product_id'],
            'prefetch_related': [],
        },
        'retrieve': {
            'select_related': ['target_category_id', 'target_product_id'],
            'prefetch_related': [],
        },
        'active': {
            'select_related': ['target_category_id', 'target_product_id'],
            'prefetch_related': [],
        }
    }
    
    search_fields = ['name', 'discount_id', 'description']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return DiscountListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return DiscountCreateSerializer
        else:
            return DiscountDetailSerializer
    
    def get_permissions(self):
        """Role-based permission checking"""
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'toggle']:
            # Manager only for write operations
            return [IsManager()]
        else:
            # Authenticated users for read operations
            return [IsAuthenticated()]
    
    def create(self, request, *args, **kwargs):
        """Create new discount (Manager only)"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            self.perform_create(serializer)
            
            # Return with detail serializer
            discount = Discount.objects.get(id=serializer.instance.id)
            detail_serializer = DiscountDetailSerializer(discount)
            
            return Response(
                detail_serializer.data,
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def update(self, request, *args, **kwargs):
        """Update discount (Manager only)"""
        try:
            partial = kwargs.pop('partial', False)
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)
            
            # Return with detail serializer
            detail_serializer = DiscountDetailSerializer(instance)
            return Response(detail_serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def active(self, request):
        """
        GET /api/discounts/active/
        Get all active discounts applicable now.
        """
        now = timezone.now()
        
        # Query active discounts
        discounts = Discount.objects.filter(is_active=True).all()
        
        # Filter by date range
        applicable = []
        for discount in discounts:
            if discount.is_applicable_at(now):
                applicable.append(discount)
        
        serializer = DiscountListSerializer(applicable, many=True)
        
        return Response({
            'count': len(applicable),
            'results': serializer.data,
            'current_datetime': now.isoformat(),
        })
    
    @action(detail=True, methods=['patch'])
    def toggle(self, request, pk=None):
        """
        PATCH /api/discounts/{id}/toggle/
        Toggle discount active/inactive status (Manager only)
        """
        discount = self.get_object()
        discount.is_active = not discount.is_active
        discount.save()
        
        serializer = DiscountDetailSerializer(discount)
        
        return Response({
            'message': f'Discount {"activated" if discount.is_active else "deactivated"}',
            'discount': serializer.data,
        })
    
    @action(detail=True, methods=['post'])
    def validate(self, request, pk=None):
        """
        POST /api/discounts/{id}/validate/
        Check if discount is applicable to a specific product at current time.
        
        Request body:
        {
            "product_id": 1
        }
        """
        discount = self.get_object()
        product_id = request.data.get('product_id')
        
        if not product_id:
            return Response(
                {'error': 'product_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {'error': f'Product with ID {product_id} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        now = timezone.now()
        
        # Check applicability
        is_time_applicable = discount.is_applicable_at(now)
        is_product_applicable = discount.is_applicable_to_product(product)
        is_active = discount.is_active
        
        is_applicable = is_active and is_time_applicable and is_product_applicable
        
        # Build reason message
        if not is_active:
            reason = 'Discount is not active'
        elif not is_time_applicable:
            reason = 'Discount is not applicable at current time'
        elif not is_product_applicable:
            reason = 'Discount does not apply to this product'
        else:
            reason = 'Discount is applicable'
        
        return Response({
            'discount_id': discount.id,
            'discount_code': discount.discount_id,
            'product_id': product_id,
            'product_name': product.name,
            'is_applicable': is_applicable,
            'reason': reason,
            'discount': {
                'discount_id': discount.discount_id,
                'name': discount.name,
                'type': discount.discount_type,
                'value': str(discount.value),
            } if is_applicable else None,
        })
    
    @action(detail=True, methods=['post'])
    def apply(self, request, pk=None):
        """
        POST /api/discounts/{id}/apply/
        Calculate discount amount for a given price.
        
        Request body:
        {
            "amount": 1000,
            "product_id": 1  (optional, for validation)
        }
        """
        discount = self.get_object()
        amount = request.data.get('amount')
        product_id = request.data.get('product_id')
        
        if amount is None:
            return Response(
                {'error': 'amount is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            amount = float(amount)
            if amount < 0:
                raise ValueError
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid amount'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Optional: Validate product compatibility
        if product_id:
            try:
                product = Product.objects.get(id=product_id)
                if not discount.is_applicable_to_product(product):
                    return Response(
                        {'error': 'Discount does not apply to this product'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            except Product.DoesNotExist:
                return Response(
                    {'error': f'Product with ID {product_id} not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        # Check if applicable now
        now = timezone.now()
        if not discount.is_applicable_at(now):
            return Response(
                {'error': 'Discount is not applicable at current time'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Calculate discount
        discount_amount = discount.calculate_discount_amount(amount)
        final_amount = amount - discount_amount
        
        return Response({
            'original_amount': str(amount),
            'discount_amount': str(round(discount_amount, 2)),
            'final_amount': str(round(final_amount, 2)),
            'discount': {
                'discount_id': discount.discount_id,
                'name': discount.name,
                'type': discount.discount_type,
                'value': str(discount.value),
            },
        })
    
    @action(detail=False, methods=['post'])
    def batch_validate(self, request):
        """
        POST /api/discounts/batch-validate/
        Check multiple discounts against a product.
        
        Request body:
        {
            "product_id": 1,
            "discount_ids": [1, 2, 3]
        }
        """
        product_id = request.data.get('product_id')
        discount_ids = request.data.get('discount_ids', [])
        
        if not product_id:
            return Response(
                {'error': 'product_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not discount_ids:
            return Response(
                {'error': 'discount_ids is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {'error': f'Product with ID {product_id} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        now = timezone.now()
        applicable_discounts = []
        
        for discount_id in discount_ids:
            try:
                discount = Discount.objects.get(id=discount_id)
                
                if (discount.is_active and 
                    discount.is_applicable_at(now) and 
                    discount.is_applicable_to_product(product)):
                    
                    applicable_discounts.append({
                        'id': discount.id,
                        'discount_id': discount.discount_id,
                        'name': discount.name,
                        'type': discount.discount_type,
                        'value': str(discount.value),
                    })
            except Discount.DoesNotExist:
                pass
        
        return Response({
            'product_id': product_id,
            'product_name': product.name,
            'applicable_discounts': applicable_discounts,
            'count': len(applicable_discounts),
        })
    
    @action(detail=False, methods=['post'])
    def batch_apply(self, request):
        """
        POST /api/discounts/batch-apply/
        Apply multiple discounts and get final price.
        
        Request body:
        {
            "amount": 1000,
            "discount_ids": [1, 2]
        }
        """
        amount = request.data.get('amount')
        discount_ids = request.data.get('discount_ids', [])
        
        if amount is None:
            return Response(
                {'error': 'amount is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            amount = float(amount)
            if amount < 0:
                raise ValueError
        except (ValueError, TypeError):
            return Response(
                {'error': 'Invalid amount'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not discount_ids:
            return Response(
                {'error': 'discount_ids is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        now = timezone.now()
        applied_discounts = []
        total_discount = 0
        
        for discount_id in discount_ids:
            try:
                discount = Discount.objects.get(id=discount_id)
                
                if (discount.is_active and 
                    discount.is_applicable_at(now)):
                    
                    discount_amt = discount.calculate_discount_amount(amount)
                    total_discount += discount_amt
                    
                    applied_discounts.append({
                        'discount_id': discount.discount_id,
                        'name': discount.name,
                        'type': discount.discount_type,
                        'value': str(discount.value),
                        'discount_amount': str(round(discount_amt, 2)),
                    })
            except Discount.DoesNotExist:
                pass
        
        final_amount = amount - total_discount
        
        return Response({
            'original_amount': str(amount),
            'applied_discounts': applied_discounts,
            'total_discount_amount': str(round(total_discount, 2)),
            'final_amount': str(round(final_amount, 2)),
        })
