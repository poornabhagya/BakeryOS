from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend

from api.models import Category
from api.permissions import IsManager
from api.serializers import (
    CategoryListSerializer,
    CategoryDetailSerializer,
    CategoryCreateSerializer,
    CategoryUpdateSerializer,
)
from api.utils.query_optimization import OptimizedQueryMixin


class CategoryPagination(PageNumberPagination):
    """Custom pagination for category list endpoints"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class CategoryViewSet(OptimizedQueryMixin, viewsets.ModelViewSet):
    """
    ViewSet for Category management.
    
    Features:
    - Pagination on list endpoints
    - Query optimized with select_related/prefetch_related
    - Filtering by type (Product/Ingredient)
    - Search capability
    
    Endpoints:
    - GET    /api/categories/              List all categories (paginated)
    - POST   /api/categories/              Create new category (Manager only)
    - GET    /api/categories/{id}/         Get category details
    - PUT    /api/categories/{id}/         Update category (Manager only)
    - PATCH  /api/categories/{id}/         Partial update
    - DELETE /api/categories/{id}/         Delete category (Manager only)
    - GET    /api/categories/by-type/      Filter by type (Product/Ingredient)
    """
    
    queryset = Category.objects.all()
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    pagination_class = CategoryPagination
    
    # Query optimization profiles
    optimized_relations = {
        'list': {
            'select_related': [],
            'prefetch_related': [],
        },
        'retrieve': {
            'select_related': [],
            'prefetch_related': [],
        },
        'by_type': {
            'select_related': [],
            'prefetch_related': [],
        }
    }
    
    # Filter by type
    filterset_fields = ['type']
    
    # Search by name and description
    search_fields = ['name', 'category_id', 'description']
    
    # Sort by name, type, creation date
    ordering_fields = ['name', 'type', 'created_at']
    ordering = ['type', 'name']
    
    def get_serializer_class(self):
        """
        Return appropriate serializer based on action
        """
        if self.action == 'list':
            return CategoryListSerializer
        elif self.action == 'create':
            return CategoryCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return CategoryUpdateSerializer
        else:  # retrieve, by_type, etc.
            return CategoryDetailSerializer
    
    def get_permissions(self):
        """
        Set permissions based on action:
        - list, retrieve: IsAuthenticated (all roles can view)
        - create, update, delete: IsManager only
        """
        if self.action in ['list', 'retrieve', 'by_type']:
            permission_classes = [IsAuthenticated]
        else:  # create, update, partial_update, destroy
            permission_classes = [IsManager]
        
        return [permission() for permission in permission_classes]
    
    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        url_path='by-type'
    )
    def by_type(self, request):
        """
        Get categories filtered by type
        
        Query params:
        - type: 'Product' or 'Ingredient'
        
        Example:
        GET /api/categories/by-type/?type=Product
        """
        category_type = request.query_params.get('type')
        
        if not category_type:
            return Response(
                {'detail': 'type query parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if category_type not in ['Product', 'Ingredient']:
            return Response(
                {'detail': f"type must be 'Product' or 'Ingredient', got: {category_type}"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        categories = Category.objects.filter(type=category_type)
        serializer = CategoryListSerializer(categories, many=True)
        
        return Response(serializer.data)
    
    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        url_path='products'
    )
    def products(self, request):
        """
        Get all product categories
        
        Example:
        GET /api/categories/products/
        """
        categories = Category.objects.filter(type='Product')
        serializer = CategoryListSerializer(categories, many=True)
        return Response(serializer.data)
    
    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        url_path='ingredients'
    )
    def ingredients(self, request):
        """
        Get all ingredient categories
        
        Example:
        GET /api/categories/ingredients/
        """
        categories = Category.objects.filter(type='Ingredient')
        serializer = CategoryListSerializer(categories, many=True)
        return Response(serializer.data)
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete a category
        
        Security: Manager only
        """
        category = self.get_object()
        
        # Optional: Check if category has items before deleting
        # If we have Products/Ingredients, we might want to prevent deletion
        # of categories that have items
        
        category.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
