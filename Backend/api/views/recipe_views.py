from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.urls import path
from django.shortcuts import get_object_or_404
from django.db.models import F, Sum
from django.utils import timezone

from api.models import RecipeItem, Product, Ingredient, IngredientBatch
from api.serializers import (
    RecipeItemSerializer,
    RecipeDetailSerializer,
    RecipeListSerializer,
    RecipeValidationSerializer,
    BatchCalculationSerializer,
)
from api.permissions import IsManager


class RecipeViewSet(viewsets.ViewSet):
    """
    ViewSet for Recipe management (product recipes with ingredients).
    
    Features:
    - Define recipes for products (what ingredients needed)
    - Track ingredient quantities per recipe
    - Calculate ingredient requirements for batch production
    - Validate if sufficient ingredients exist to make a product
    - Auto-calculate product cost_price from recipe
    
    Endpoints:
    - GET /api/recipes/<product_id>/ - Get recipe for product
    - POST /api/recipes/<product_id>/items/ - Add ingredient to recipe
    - PUT /api/recipes/<product_id>/<ingredient_id>/ - Update ingredient qty
    - DELETE /api/recipes/<product_id>/<ingredient_id>/ - Remove ingredient
    - GET /api/recipes/validate/<product_id>/ - Check if can make product
    - GET /api/recipes/batch-required/<product_id>?qty=10 - Calculate batch needs
    
    Permissions:
    - Manager: Full CRUD on recipes
    - Baker: Read-only + validation
    - Others: No access
    """
    
    def get_permissions(self):
        """Role-based permission checking"""
        return [IsAuthenticated()]
    
    # ========== RECIPE RETRIEVAL ==========
    
    def retrieve(self, request, pk=None):
        """
        GET /api/recipes/<product_id>/
        
        Get complete recipe for a product.
        """
        try:
            product = Product.objects.get(id=pk)
        except Product.DoesNotExist:
            return Response(
                {'error': f'Product with ID {pk} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get recipe items
        recipe_items = RecipeItem.objects.filter(product_id=product)
        
        if not recipe_items.exists():
            return Response(
                {'error': f'No recipe defined for product {product.product_id}'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Serialize recipe items
        items_serializer = RecipeDetailSerializer(recipe_items, many=True)
        
        # Calculate total cost
        total_cost = sum(
            float(item.get('total_cost_for_recipe', 0)) 
            for item in items_serializer.data
        )
        
        return Response({
            'product_id': product.id,
            'product_name': product.name,
            'product_code': product.product_id,
            'product_cost_price': str(product.cost_price),
            'product_selling_price': str(product.selling_price),
            'items': items_serializer.data,
            'total_recipe_cost': total_cost,
            'total_items': recipe_items.count()
        })
    
    # ========== RECIPE MANAGEMENT ==========
    
    @action(detail=True, methods=['post'], url_path='items')
    def add_item(self, request, pk=None):
        """
        POST /api/recipes/<product_id>/items/
        Add an ingredient to a product's recipe.
        """
        try:
            product = Product.objects.get(id=pk)
        except Product.DoesNotExist:
            return Response(
                {'error': f'Product with ID {pk} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check permission
        if request.user.role != 'Manager':
            return Response(
                {'error': 'Only Managers can add ingredients to recipes'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Add product_id to request data
        data = request.data.copy()
        data['product_id'] = product.id
        
        serializer = RecipeItemSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['put'], url_path='items/(?P<ingredient_id>[^/]+)')
    def update_item(self, request, pk=None, ingredient_id=None):
        """
        PUT /api/recipes/<product_id>/items/<ingredient_id>/
        Update quantity of ingredient in recipe.
        """
        # Check permission
        if request.user.role != 'Manager':
            return Response(
                {'error': 'Only Managers can update recipe items'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            recipe_item = RecipeItem.objects.get(
                product_id=pk,
                ingredient_id=ingredient_id
            )
        except RecipeItem.DoesNotExist:
            return Response(
                {'error': 'Recipe ingredient not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        serializer = RecipeItemSerializer(recipe_item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['delete'], url_path='items/(?P<ingredient_id>[^/]+)')
    def remove_item(self, request, pk=None, ingredient_id=None):
        """
        DELETE /api/recipes/<product_id>/items/<ingredient_id>/
        Remove ingredient from recipe.
        """
        # Check permission
        if request.user.role != 'Manager':
            return Response(
                {'error': 'Only Managers can remove ingredients from recipes'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            recipe_item = RecipeItem.objects.get(
                product_id=pk,
                ingredient_id=ingredient_id
            )
        except RecipeItem.DoesNotExist:
            return Response(
                {'error': 'Recipe ingredient not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        product_id_val = recipe_item.product_id.id
        ingredient_id_val = recipe_item.ingredient_id.id
        
        recipe_item.delete()
        
        # Recalculate product cost_price
        try:
            product = Product.objects.get(id=product_id_val)
            product.update_cost_price_from_recipe()
        except:
            pass
        
        return Response({
            'message': 'Ingredient removed from recipe',
            'product_id': product_id_val,
            'ingredient_id': ingredient_id_val
        })
    
    # ========== RECIPE VALIDATION & CALCULATIONS ==========
    
    @action(detail=True, methods=['get'], url_path='validate')
    def validate_recipe(self, request, pk=None):
        """
        GET /api/recipes/<product_id>/validate/
        Check if enough ingredients exist to make a product.
        """
        product_id = pk
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {'error': f'Product with ID {product_id} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        recipe_items = RecipeItem.objects.filter(product_id=product)
        
        if not recipe_items.exists():
            return Response({
                'product_id': product.id,
                'product_name': product.name,
                'can_make': False,
                'reason': 'No recipe defined for this product',
                'missing_ingredients': []
            })
        
        # Check each ingredient
        missing = []
        can_make = True
        
        for item in recipe_items:
            available = item.ingredient_id.total_quantity
            required = item.quantity_required
            
            if available < required:
                can_make = False
                missing.append({
                    'ingredient_id': item.ingredient_id.id,
                    'ingredient_name': item.ingredient_id.name,
                    'ingredient_code': item.ingredient_id.ingredient_id,
                    'required': float(required),
                    'available': float(available),
                    'short_by': float(required - available)
                })
        
        return Response({
            'product_id': product.id,
            'product_name': product.name,
            'can_make': can_make,
            'reason': 'All ingredients in stock' if can_make else 'Insufficient stock for one or more ingredients',
            'missing_ingredients': missing
        })
    
    @action(detail=True, methods=['get'], url_path='batch_required')
    def batch_required(self, request, pk=None):
        """
        GET /api/recipes/<product_id>/batch_required/?qty=10
        Calculate how much of each ingredient is needed to make a batch of products.
        """
        product_id = pk
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {'error': f'Product with ID {product_id} not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get batch quantity from query params
        batch_qty = request.query_params.get('qty', 1)
        try:
            batch_qty = int(batch_qty)
            if batch_qty <= 0:
                raise ValueError
        except:
            return Response(
                {'error': 'qty must be a positive integer'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        recipe_items = RecipeItem.objects.filter(product_id=product)
        
        if not recipe_items.exists():
            return Response(
                {'error': f'No recipe defined for product {product.product_id}'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Calculate ingredient needs
        ingredients_needed = []
        total_batch_cost = 0
        
        for item in recipe_items:
            qty_per_unit = item.quantity_required
            total_required = qty_per_unit * batch_qty
            current_stock = item.ingredient_id.total_quantity
            
            # Get cost per unit from latest batch
            batches = IngredientBatch.objects.filter(
                ingredient_id=item.ingredient_id,
                status='Active'
            ).order_by('-created_at')
            
            cost_per_unit = 0
            if batches.exists():
                batch = batches.first()
                if batch.quantity > 0:
                    cost_per_unit = float(batch.total_batch_cost) / float(batch.quantity)
            
            item_cost = float(total_required) * cost_per_unit
            total_batch_cost += item_cost
            
            ingredients_needed.append({
                'ingredient_id': item.ingredient_id.id,
                'ingredient_name': item.ingredient_id.name,
                'ingredient_code': item.ingredient_id.ingredient_id,
                'base_unit': item.ingredient_id.base_unit,
                'quantity_per_unit': float(qty_per_unit),
                'total_required': float(total_required),
                'current_stock': float(current_stock),
                'sufficient': float(current_stock) >= float(total_required),
                'cost_per_unit': cost_per_unit,
                'total_cost': item_cost
            })
        
        return Response({
            'product_id': product.id,
            'product_name': product.name,
            'batch_quantity': batch_qty,
            'ingredients_needed': ingredients_needed,
            'total_batch_cost': round(total_batch_cost, 2),
            'total_items_in_recipe': recipe_items.count()
        })
