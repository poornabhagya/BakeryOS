from rest_framework import serializers
from api.models import RecipeItem, Product, Ingredient, IngredientBatch


class RecipeItemSerializer(serializers.ModelSerializer):
    """
    Simple serializer for recipe items.
    Used for creating/updating recipe items.
    """
    ingredient_name = serializers.CharField(source='ingredient_id.name', read_only=True)
    ingredient_code = serializers.CharField(source='ingredient_id.ingredient_id', read_only=True)
    base_unit = serializers.CharField(source='ingredient_id.base_unit', read_only=True)
    
    class Meta:
        model = RecipeItem
        fields = ['id', 'product_id', 'ingredient_id', 'ingredient_name', 'ingredient_code', 
                  'quantity_required', 'base_unit', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']
    
    def validate_quantity_required(self, value):
        """Validate quantity_required is positive"""
        if value <= 0:
            raise serializers.ValidationError("Quantity required must be greater than 0")
        return value
    
    def validate(self, data):
        """Check for duplicate ingredients in same recipe"""
        product_id = data.get('product_id')
        ingredient_id = data.get('ingredient_id')
        
        # Check if this combination already exists (excluding current instance)
        instance = self.instance
        existing = RecipeItem.objects.filter(
            product_id=product_id,
            ingredient_id=ingredient_id
        )
        
        if instance:
            existing = existing.exclude(id=instance.id)
        
        if existing.exists():
            raise serializers.ValidationError({
                'ingredient_id': f"This ingredient is already in the recipe for {product_id.name}"
            })
        
        return data


class RecipeDetailSerializer(serializers.ModelSerializer):
    """
    Detailed recipe serializer with expanded ingredient information.
    Used for GET /api/recipes/{product_id}/ endpoint.
    """
    product_name = serializers.CharField(source='product_id.name', read_only=True)
    product_code = serializers.CharField(source='product_id.product_id', read_only=True)
    
    # Full ingredient details
    ingredient_name = serializers.CharField(source='ingredient_id.name', read_only=True)
    ingredient_code = serializers.CharField(source='ingredient_id.ingredient_id', read_only=True)
    ingredient_category = serializers.CharField(source='ingredient_id.category_id.name', read_only=True)
    ingredient_supplier = serializers.CharField(source='ingredient_id.supplier', read_only=True)
    base_unit = serializers.CharField(source='ingredient_id.base_unit', read_only=True)
    
    # Current status
    current_stock = serializers.SerializerMethodField()
    ingredient_cost_per_unit = serializers.SerializerMethodField()
    total_cost_for_recipe = serializers.SerializerMethodField()
    
    class Meta:
        model = RecipeItem
        fields = [
            'id', 'product_id', 'product_name', 'product_code',
            'ingredient_id', 'ingredient_name', 'ingredient_code', 'ingredient_category',
            'ingredient_supplier', 'base_unit', 'quantity_required',
            'current_stock', 'ingredient_cost_per_unit', 'total_cost_for_recipe',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_current_stock(self, obj):
        """Get current stock for this ingredient"""
        return obj.ingredient_id.total_quantity
    
    def get_ingredient_cost_per_unit(self, obj):
        """Get cost per unit from most recent batch"""
        batches = IngredientBatch.objects.filter(
            ingredient_id=obj.ingredient_id,
            status='Active'
        ).order_by('-created_at')
        
        if batches.exists():
            batch = batches.first()
            if batch.quantity > 0:
                return float(batch.total_batch_cost) / float(batch.quantity)
        return 0
    
    def get_total_cost_for_recipe(self, obj):
        """Calculate total cost for this ingredient in recipe"""
        cost_per_unit = self.get_ingredient_cost_per_unit(obj)
        return float(obj.quantity_required) * cost_per_unit


class RecipeListSerializer(serializers.Serializer):
    """
    List serializer to show all recipe items for a product.
    Used for GET /api/recipes/{product_id}/ endpoint.
    """
    product_id = serializers.IntegerField()
    product_name = serializers.CharField()
    product_code = serializers.CharField()
    product_cost_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    product_selling_price = serializers.DecimalField(max_digits=10, decimal_places=2)
    items = RecipeDetailSerializer(source='recipe_items', many=True)
    total_recipe_cost = serializers.SerializerMethodField()
    total_items = serializers.IntegerField()
    
    def get_total_recipe_cost(self, obj):
        """Sum of all ingredient costs in recipe"""
        return sum(
            float(item.get('total_cost_for_recipe', 0))
            for item in obj['items']
        )


class RecipeValidationSerializer(serializers.Serializer):
    """
    Serializer for recipe validation results.
    Used for GET /api/recipes/validate/{product_id}/ endpoint.
    """
    product_id = serializers.IntegerField()
    product_name = serializers.CharField()
    can_make = serializers.BooleanField()
    reason = serializers.CharField(allow_blank=True)
    missing_ingredients = serializers.ListField(child=serializers.DictField())


class BatchCalculationSerializer(serializers.Serializer):
    """
    Serializer for batch ingredient requirement calculation.
    Used for GET /api/recipes/batch-required/{product_id}?qty=10 endpoint.
    """
    product_id = serializers.IntegerField()
    product_name = serializers.CharField()
    batch_quantity = serializers.DecimalField(max_digits=10, decimal_places=2)
    ingredients_needed = serializers.ListField(child=serializers.DictField())
    total_batch_cost = serializers.DecimalField(max_digits=10, decimal_places=2)
    total_items_in_recipe = serializers.IntegerField()
