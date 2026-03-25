from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import F, Count
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from api.models import Ingredient, Category
from api.serializers import (
    IngredientListSerializer,
    IngredientDetailSerializer,
    IngredientCreateSerializer,
    IngredientUpdateSerializer,
)
from api.permissions import IsManager, IsStorekeeper, IsBaker, IsManagerOrStorekeeper, IsManagerOrStorekeeperOrBaker


class IngredientViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Ingredient management.
    
    Endpoints:
    - GET    /api/ingredients/              List all ingredients
    - POST   /api/ingredients/              Create new ingredient
    - GET    /api/ingredients/{id}/         Get ingredient details
    - PUT    /api/ingredients/{id}/         Full update
    - PATCH  /api/ingredients/{id}/         Partial update
    - DELETE /api/ingredients/{id}/         Delete (soft delete)
    
    Custom Actions:
    - GET    /api/ingredients/low-stock/    Get low-stock ingredients
    - GET    /api/ingredients/{id}/history/ Get stock history
    
    Filtering:
    - ?category_id=1        Filter by category
    - ?is_low_stock=true    Filter low stock only
    - ?is_active=true       Show only active
    - ?search=Flour         Search by name
    - ?ordering=name        Sort by field
    """
    
    queryset = Ingredient.objects.filter(is_active=True)
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['category_id', 'is_active']
    search_fields = ['ingredient_id', 'name', 'supplier']
    ordering_fields = ['name', 'category_id', 'total_quantity', 'created_at']
    ordering = ['category_id', 'name']
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return IngredientListSerializer
        elif self.action == 'create':
            return IngredientCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return IngredientUpdateSerializer
        else:  # retrieve, custom actions
            return IngredientDetailSerializer
    
    def get_permissions(self):
        """
        Return appropriate permission classes based on action.
        
        Permissions:
        - list/retrieve/history: Manager OR Storekeeper OR Baker
        - create/update: Manager OR Storekeeper
        - delete: Manager only
        - low-stock: Manager OR Storekeeper OR Baker
        """
        if self.action in ['list', 'retrieve', 'history', 'low_stock']:
            # All authenticated users can view
            self.permission_classes = [IsManagerOrStorekeeperOrBaker]
        elif self.action in ['create', 'update', 'partial_update']:
            # Manager and Storekeeper can create/update
            self.permission_classes = [IsManagerOrStorekeeper]
        elif self.action == 'destroy':
            # Only Manager can delete
            self.permission_classes = [IsManager]
        else:
            self.permission_classes = [IsAuthenticated]
        
        return super().get_permissions()
    
    def list(self, request, *args, **kwargs):
        """
        List all ingredients with filtering and search.
        
        Query Parameters:
        - category_id: Filter by category
        - is_active: Filter by active status
        - search: Search by name, ingredient_id, supplier
        - ordering: Sort by name, category_id, total_quantity, created_at
        - is_low_stock: (custom) Filter by low stock status
        """
        # Handle custom is_low_stock filter
        is_low_stock = request.query_params.get('is_low_stock')
        if is_low_stock and is_low_stock.lower() == 'true':
            self.queryset = self.queryset.filter(
                total_quantity__lt=F('low_stock_threshold')
            )
        
        return super().list(request, *args, **kwargs)
    
    def create(self, request, *args, **kwargs):
        """Create new ingredient"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        
        # Return detail view of created ingredient
        headers = self.get_success_headers(serializer.data)
        ingredient = serializer.instance
        detail_serializer = IngredientDetailSerializer(ingredient)
        return Response(detail_serializer.data, status=status.HTTP_201_CREATED, headers=headers)
    
    def destroy(self, request, *args, **kwargs):
        """
        Soft delete: Mark as inactive instead of deleting.
        
        This prevents breaking foreign key relationships with batches.
        """
        instance = self.get_object()
        # Check if has active batches
        # After IngredientBatch model: batches = instance.batches.filter(status='Active')
        # if batches.exists():
        #     return Response(
        #         {'error': f'Cannot delete ingredient with {batches.count()} active batches.'},
        #         status=status.HTTP_400_BAD_REQUEST
        #     )
        
        instance.is_active = False
        instance.save()
        
        return Response(
            {'message': f'Ingredient {instance.ingredient_id} marked as inactive.'},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['get'], permission_classes=[IsManagerOrStorekeeperOrBaker])
    def low_stock(self, request):
        """
        Get ingredients below low_stock_threshold.
        
        Endpoint: GET /api/ingredients/low-stock/
        
        Response: List of low-stock ingredients with quantity info
        """
        low_stock_ingredients = self.queryset.filter(
            total_quantity__lt=F('low_stock_threshold'),
            is_active=True
        ).order_by('total_quantity')
        
        serializer = IngredientListSerializer(low_stock_ingredients, many=True)
        return Response({
            'count': low_stock_ingredients.count(),
            'results': serializer.data
        })
    
    @action(detail=True, methods=['get'], permission_classes=[IsManagerOrStorekeeperOrBaker])
    def history(self, request, pk=None):
        """
        Get stock history for ingredient.
        
        Endpoint: GET /api/ingredients/{id}/history/
        
        Returns: Stock transactions (will be implemented with IngredientStockHistory)
        """
        ingredient = self.get_object()
        
        return Response({
            'ingredient_id': ingredient.ingredient_id,
            'name': ingredient.name,
            'current_quantity': str(ingredient.total_quantity),
            'history': {
                'message': 'Stock history will be available after IngredientStockHistory model is created',
                'transactions': []
            }
        })
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """
        Get ingredients grouped by category.
        
        Endpoint: GET /api/ingredients/by-category/
        
        Response: Grouped ingredients by category
        """
        categories = Category.objects.filter(
            type='Ingredient'
        ).prefetch_related('ingredients')
        
        result = []
        for category in categories:
            ingredients = category.ingredients.filter(is_active=True)
            result.append({
                'category_id': category.id,
                'category_name': category.name,
                'count': ingredients.count(),
                'ingredients': IngredientListSerializer(ingredients, many=True).data
            })
        
        return Response(result)
    
    @action(detail=False, methods=['get'])
    def out_of_stock(self, request):
        """
        Get out-of-stock ingredients.
        
        Endpoint: GET /api/ingredients/out-of-stock/
        
        Response: List of ingredients with 0 quantity
        """
        out_of_stock = self.queryset.filter(
            total_quantity__lte=0,
            is_active=True
        )
        
        serializer = IngredientListSerializer(out_of_stock, many=True)
        return Response({
            'count': out_of_stock.count(),
            'results': serializer.data
        })
    
    @action(detail=True, methods=['post'])
    def reset_quantity(self, request, pk=None):
        """
        Reset total_quantity to 0 (admin action).
        
        Endpoint: POST /api/ingredients/{id}/reset-quantity/
        
        Only for Manager
        """
        if request.user.role != 'Manager':
            return Response(
                {'error': 'Only managers can reset quantities.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        ingredient = self.get_object()
        ingredient.total_quantity = 0
        ingredient.save()
        
        serializer = IngredientDetailSerializer(ingredient)
        return Response({
            'message': f'Quantity reset for {ingredient.ingredient_id}',
            'ingredient': serializer.data
        })
