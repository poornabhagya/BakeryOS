from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import F, Q
from django.utils import timezone
# django_filters removed due to Django 6.0 compatibility
# from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination

from api.models import Product, Category
from api.serializers import (
    ProductListSerializer,
    ProductDetailSerializer,
    ProductCreateSerializer,
    ProductSearchSerializer,
    ProductFilterSerializer,
)
from api.permissions import IsManager, IsManagerOrReadOnly
from api.utils.query_optimization import OptimizedQueryMixin, StandardPagination


class ProductPagination(PageNumberPagination):
    """Custom pagination for product list endpoints"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class ProductViewSet(OptimizedQueryMixin, viewsets.ModelViewSet):
    """
    ViewSet for Product management (bakery items).
    
    Features:
    - Auto-generated product_id (#PROD-1001, #PROD-1002, etc.)
    - Dynamic profit margin calculation
    - Category-based organization
    - Stock management and low-stock alerts
    - Search and filtering capabilities
    - Recipe linkage for production
    - Query optimized with select_related/prefetch_related
    - Pagination on all list endpoints
    
    Endpoints:
    - GET /api/products/ - List products (paginated, filtered, ordered)
    - POST /api/products/ - Create product (Manager only)
    - GET /api/products/{id}/ - Get product details
    - PUT /api/products/{id}/ - Update product (Manager only)
    - PATCH /api/products/{id}/ - Partial update (Manager only)
    - DELETE /api/products/{id}/ - Delete product (Manager only)
    - GET /api/products/category/{category_id}/ - Filter by category
    - GET /api/products/low-stock/ - Get low-stock products
    - GET /api/products/out-of-stock/ - Get out-of-stock products
    - GET /api/products/{id}/recipe/ - Get recipe (custom action)
    
    Permissions:
    - Manager: Full CRUD
    - Baker: Read-only
    - Storekeeper: Read-only
    - Cashier: Read-only
    """
    
    queryset = Product.objects.all()
    filter_backends = [SearchFilter, OrderingFilter]
    pagination_class = ProductPagination
    
    # Query optimization profiles
    optimized_relations = {
        'list': {
            'select_related': ['category_id'],
            'prefetch_related': [],
        },
        'retrieve': {
            'select_related': ['category_id'],
            'prefetch_related': ['batches', 'stock_history'],
        },
        'low_stock': {
            'select_related': ['category_id'],
            'prefetch_related': [],
        },
        'out_of_stock': {
            'select_related': ['category_id'],
            'prefetch_related': [],
        },
        'by_category': {
            'select_related': ['category_id'],
            'prefetch_related': [],
        }
    }
    
    # Filter configuration
    filterset_fields = ['category_id']  # 'status' is a @property, not a DB field
    search_fields = ['product_id', 'name', 'category_id__name']
    ordering_fields = ['selling_price', 'current_stock', 'name', 'created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Route to appropriate serializer based on action"""
        if self.action == 'list':
            return ProductListSerializer
        elif self.action == 'retrieve':
            return ProductDetailSerializer
        elif self.action == 'create':
            return ProductCreateSerializer
        elif self.action == 'update' or self.action == 'partial_update':
            return ProductCreateSerializer
        elif self.action == 'search':
            return ProductSearchSerializer
        return ProductListSerializer
    
    def get_permissions(self):
        """Role-based permission checking"""
        if self.action in ['list', 'retrieve', 'low_stock', 'out_of_stock', 'by_category', 'recipe']:
            # Read-only endpoints: any authenticated user
            return [IsAuthenticated()]
        elif self.action in ['create', 'update', 'partial_update', 'destroy']:
            # Write endpoints: Manager only
            return [IsManager()]
        return [IsAuthenticated()]
    
    # ========== STANDARD CRUD ENDPOINTS ==========
    # Inherited from ModelViewSet:
    # - list: GET /api/products/
    # - create: POST /api/products/
    # - retrieve: GET /api/products/{id}/
    # - update: PUT /api/products/{id}/
    # - partial_update: PATCH /api/products/{id}/
    # - destroy: DELETE /api/products/{id}/
    
    # ========== CUSTOM ENDPOINTS ==========
    
    @action(detail=False, methods=['get'])
    def low_stock(self, request):
        """
        GET /api/products/low-stock/
        
        Return all products with low stock (current_stock < 10).
        Useful for alerts and restocking.
        
        Response: [ ProductListSerializer ]
        """
        queryset = self.queryset.filter(current_stock__lt=10)
        serializer = ProductListSerializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def out_of_stock(self, request):
        """
        GET /api/products/out-of-stock/
        
        Return all products that are completely out of stock.
        
        Response: [ ProductListSerializer ]
        """
        queryset = self.queryset.filter(current_stock__lte=0)
        serializer = ProductListSerializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'], url_path='by-category/(?P<category_id>[^/.]+)')
    def by_category(self, request, category_id=None):
        """
        GET /api/products/by-category/{category_id}/
        
        Return all products in a specific category.
        
        Parameters:
        - category_id: Category ID (numeric)
        
        Response: [ ProductListSerializer ]
        """
        try:
            category = Category.objects.get(id=category_id, type='Product')
        except Category.DoesNotExist:
            return Response(
                {'error': f'Product category with ID {category_id} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        queryset = self.queryset.filter(category_id=category_id)
        serializer = ProductListSerializer(queryset, many=True)
        return Response({
            'category': {
                'id': category.id,
                'name': category.name,
                'type': category.type
            },
            'count': queryset.count(),
            'results': serializer.data
        })
    
    @action(detail=True, methods=['get'])
    def recipe(self, request, pk=None):
        """
        GET /api/products/{id}/recipe/
        
        Get the recipe for a product (what ingredients are needed to make it).
        Returns list of RecipeItem objects with ingredient details.
        
        Future Integration: RecipeItem model will contain:
        - ingredient_id, ingredient_name, quantity_required, unit
        
        Response:
        {
            'product_id': '#PROD-1001',
            'product_name': 'White Bread',
            'items': [
                {
                    'ingredient': '#I001 - All Purpose Flour',
                    'quantity_required': 2.5,
                    'unit': 'kg'
                }
            ]
        }
        """
        try:
            product = self.get_object()
        except Product.DoesNotExist:
            return Response(
                {'error': 'Product not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # For now, return placeholder until RecipeItem model is created
        # In Task 3.5, this will query RecipeItem objects
        return Response({
            'product_id': product.product_id,
            'product_name': product.name,
            'message': 'Recipe feature coming in Task 3.5'
        })
    
    @action(detail=False, methods=['post'])
    def bulk_update_stock(self, request):
        """
        POST /api/products/bulk-update-stock/
        
        Update stock for multiple products at once.
        Useful for production batch creation.
        
        Request Body:
        {
            'updates': [
                {'product_id': 1, 'change': 10},  // add 10
                {'product_id': 2, 'change': -5},  // remove 5
            ]
        }
        """
        if request.user.role != 'Manager':
            return Response(
                {'error': 'Only Managers can bulk update stock'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            updates = request.data.get('updates', [])
            updated_count = 0
            
            for update in updates:
                product_id = update.get('product_id')
                change = update.get('change', 0)
                
                try:
                    product = Product.objects.get(id=product_id)
                    product.current_stock = max(0, product.current_stock + change)
                    product.save()
                    updated_count += 1
                except Product.DoesNotExist:
                    pass
            
            return Response({
                'message': f'Updated {updated_count} products',
                'updated_count': updated_count
            })
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
