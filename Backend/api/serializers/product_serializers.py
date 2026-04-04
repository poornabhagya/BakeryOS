from rest_framework import serializers
from django.db import transaction
from api.models import Product, Category, RecipeItem, Ingredient
from api.validators import (
    validate_positive_number, validate_non_negative_number,
    sanitize_string, sanitize_html
)
from decimal import Decimal


class RecipeItemSerializer(serializers.ModelSerializer):
    """
    Nested serializer for recipe items.
    Used when creating/updating products with recipes.
    """
    ingredient_name = serializers.CharField(source='ingredient_id.name', read_only=True)
    ingredient_unit = serializers.CharField(source='ingredient_id.base_unit', read_only=True)
    
    class Meta:
        model = RecipeItem
        fields = [
            'id', 'ingredient_id', 'ingredient_name', 'quantity_required', 'ingredient_unit'
        ]
        read_only_fields = ['id', 'ingredient_name', 'ingredient_unit']


class ProductListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing products with calculated fields.
    Used for: GET /api/products/
    
    IMPORTANT: Uses Product.current_stock as the absolute source of truth for quantity.
    """
    category_name = serializers.CharField(source='category_id.name', read_only=True)
    profit_margin = serializers.SerializerMethodField()
    status = serializers.CharField(read_only=True)
    quantity = serializers.SerializerMethodField()
    recipe_items = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'product_id', 'name', 'category_id', 'category_name',
            'cost_price', 'selling_price', 'profit_margin',
            'current_stock', 'quantity', 'status', 'shelf_life', 'shelf_unit',
            'recipe_items', 'created_at'
        ]
        read_only_fields = ['product_id', 'recipe_items', 'created_at', 'current_stock', 'quantity']
    
    def get_profit_margin(self, obj):
        """Return profit margin as percentage"""
        return round(obj.profit_margin, 2)
    
    def get_quantity(self, obj):
        """Return current product stock from Product.current_stock."""
        return float(obj.current_stock) if obj.current_stock else 0.0
    
    def get_recipe_items(self, obj):
        """Get recipe items for the product"""
        recipe_items = obj.recipe_items.all()
        return RecipeItemSerializer(recipe_items, many=True).data


class ProductDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed product information.
    Includes category details, profit margin, and recipe items.
    Used for: GET /api/products/{id}/
    
    IMPORTANT: Uses Product.current_stock as the absolute source of truth for quantity.
    """
    category_name = serializers.CharField(source='category_id.name', read_only=True)
    category_type = serializers.CharField(source='category_id.type', read_only=True)
    profit_margin = serializers.SerializerMethodField()
    status = serializers.CharField(read_only=True)
    is_low_stock = serializers.SerializerMethodField()
    is_out_of_stock = serializers.SerializerMethodField()
    quantity = serializers.SerializerMethodField()
    recipe_items = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'product_id', 'name', 'description', 'image_url',
            'category_id', 'category_name', 'category_type',
            'cost_price', 'selling_price', 'profit_margin',
            'current_stock', 'quantity', 'status', 'is_low_stock', 'is_out_of_stock',
            'shelf_life', 'shelf_unit', 'recipe_items',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['product_id', 'recipe_items', 'created_at', 'updated_at', 'current_stock', 'quantity']
    
    def get_profit_margin(self, obj):
        """Return profit margin as percentage with 2 decimals"""
        return round(obj.profit_margin, 2)
    
    def get_quantity(self, obj):
        """Return current product stock from Product.current_stock."""
        return float(obj.current_stock) if obj.current_stock else 0.0
    
    def get_is_low_stock(self, obj):
        """Check low stock status using Product.current_stock."""
        quantity = float(obj.current_stock) if obj.current_stock else 0.0
        return quantity < 10
    
    def get_is_out_of_stock(self, obj):
        """Check out-of-stock status using Product.current_stock."""
        quantity = float(obj.current_stock) if obj.current_stock else 0.0
        return quantity <= 0
    
    def get_recipe_items(self, obj):
        """Get recipe items for the product"""
        recipe_items = obj.recipe_items.all()
        return RecipeItemSerializer(recipe_items, many=True).data


class ProductCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating products.
    Validates required fields and constraints.
    Supports nested recipe items creation.
    Used for: POST /api/products/, PUT /api/products/{id}/, PATCH /api/products/{id}/
    
    Validation:
    - name: Non-empty, unique per category, sanitized
    - cost_price: Must be positive (> 0)
    - selling_price: Must be > cost_price
    - shelf_life: Must be positive integer
    - current_stock: Must be non-negative
    - recipe_items: Optional nested array of recipe items
    """
    # Nested recipe items for WRITE operations only - mark as write_only
    recipe_items = serializers.ListField(
        child=serializers.DictField(
            child=serializers.CharField(),
            allow_empty=False
        ),
        required=False,
        write_only=True,
        help_text="Array of recipe items: [{'ingredient_id': 1, 'quantity_required': '2.5'}, ...]"
    )
    
    class Meta:
        model = Product
        fields = [
            'id', 'product_id', 'category_id', 'name', 'description', 'image_url',
            'cost_price', 'selling_price', 'current_stock',
            'shelf_life', 'shelf_unit', 'recipe_items',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'product_id', 'created_at', 'updated_at']
    
    def validate_name(self, value):
        """Validate and sanitize product name"""
        if not value:
            raise serializers.ValidationError("Product name is required.")
        
        # Sanitize
        value = sanitize_string(value)
        
        if len(value) < 2:
            raise serializers.ValidationError("Product name must be at least 2 characters.")
        
        if len(value) > 255:
            raise serializers.ValidationError("Product name must not exceed 255 characters.")
        
        return value
    
    def validate_category_id(self, value):
        """Validate category exists"""
        if not Category.objects.filter(id=value.id, type='Product').exists():
            raise serializers.ValidationError("Selected category must be a Product category.")
        return value
    
    def validate_cost_price(self, value):
        """Validate cost price"""
        try:
            validate_positive_number(value)
        except serializers.ValidationError:
            raise serializers.ValidationError("Cost price must be greater than 0.")
        
        # Check it's 2 decimal places or less
        if isinstance(value, Decimal):
            if value.as_tuple().exponent < -2:
                raise serializers.ValidationError("Cost price can have maximum 2 decimal places.")
        
        return value
    
    def validate_selling_price(self, value):
        """Validate selling price"""
        try:
            validate_positive_number(value)
        except serializers.ValidationError:
            raise serializers.ValidationError("Selling price must be greater than 0.")
        
        # Check it's 2 decimal places or less
        if isinstance(value, Decimal):
            if value.as_tuple().exponent < -2:
                raise serializers.ValidationError("Selling price can have maximum 2 decimal places.")
        
        return value
    
    def validate_current_stock(self, value):
        """Validate current stock"""
        try:
            validate_non_negative_number(value)
        except serializers.ValidationError:
            raise serializers.ValidationError("Stock quantity cannot be negative.")
        return value
    
    def validate_shelf_life(self, value):
        """Validate shelf life"""
        if not value or value <= 0:
            raise serializers.ValidationError("Shelf life must be at least 1.")
        return value
    
    def validate_description(self, value):
        """Sanitize description"""
        if value:
            value = sanitize_html(value)
        return value

    def validate_recipe_items(self, value):
        """
        Validate writable nested recipe items payload.

        Expected item format:
        {'ingredient_id': <int>, 'quantity_required': <decimal-like string/number>}
        """
        if value is None:
            return []

        normalized_items = []
        seen_ingredient_ids = set()

        for idx, item in enumerate(value):
            if not isinstance(item, dict):
                raise serializers.ValidationError(
                    f"recipe_items[{idx}] must be an object"
                )

            ingredient_raw = item.get('ingredient_id')
            quantity_raw = item.get('quantity_required')

            if ingredient_raw in (None, ''):
                raise serializers.ValidationError(
                    f"recipe_items[{idx}].ingredient_id is required"
                )

            if quantity_raw in (None, ''):
                raise serializers.ValidationError(
                    f"recipe_items[{idx}].quantity_required is required"
                )

            try:
                ingredient_id = int(ingredient_raw)
            except (TypeError, ValueError):
                raise serializers.ValidationError(
                    f"recipe_items[{idx}].ingredient_id must be an integer"
                )

            try:
                quantity_required = Decimal(str(quantity_raw))
            except Exception:
                raise serializers.ValidationError(
                    f"recipe_items[{idx}].quantity_required must be a valid decimal"
                )

            if quantity_required <= 0:
                raise serializers.ValidationError(
                    f"recipe_items[{idx}].quantity_required must be greater than 0"
                )

            if ingredient_id in seen_ingredient_ids:
                raise serializers.ValidationError(
                    f"Duplicate ingredient_id {ingredient_id} in recipe_items"
                )

            if not Ingredient.objects.filter(id=ingredient_id).exists():
                raise serializers.ValidationError(
                    f"Ingredient with id {ingredient_id} does not exist"
                )

            seen_ingredient_ids.add(ingredient_id)
            normalized_items.append({
                'ingredient_id': ingredient_id,
                'quantity_required': quantity_required,
            })

        return normalized_items
    
    def validate(self, data):
        """Custom validation for product data"""
        # Validate selling price > cost price
        cost = data.get('cost_price')
        selling = data.get('selling_price')
        
        if cost and selling and selling <= cost:
            raise serializers.ValidationError({
                'selling_price': "Selling price must be greater than cost price."
            })
        
        # Check unique constraint: name per category
        category_id = data.get('category_id')
        name = data.get('name')
        
        if category_id and name:
            # If updating, exclude current instance
            queryset = Product.objects.filter(category_id=category_id, name=name)
            if self.instance:
                queryset = queryset.exclude(pk=self.instance.pk)
            
            if queryset.exists():
                raise serializers.ValidationError({
                    'name': f'Product "{name}" already exists in this category.'
                })
        
        return data
    
    @transaction.atomic
    def create(self, validated_data):
        """Create product and persist all validated nested recipe items atomically."""
        recipe_items_data = validated_data.pop('recipe_items', [])

        product = Product.objects.create(**validated_data)

        if recipe_items_data:
            ingredient_ids = [item['ingredient_id'] for item in recipe_items_data]
            ingredient_map = {
                ing.id: ing
                for ing in Ingredient.objects.filter(id__in=ingredient_ids)
            }

            recipe_objects = []
            for item in recipe_items_data:
                ingredient = ingredient_map.get(item['ingredient_id'])
                if ingredient is None:
                    raise serializers.ValidationError(
                        f"Ingredient with id {item['ingredient_id']} does not exist"
                    )

                recipe_objects.append(
                    RecipeItem(
                        product_id=product,
                        ingredient_id=ingredient,
                        quantity_required=item['quantity_required'],
                    )
                )

            RecipeItem.objects.bulk_create(recipe_objects)

        return product
    
    def to_representation(self, instance):
        """Override to include recipe_items in response"""
        data = super().to_representation(instance)
        # Add recipe items to the response
        recipe_items = instance.recipe_items.all()
        data['recipe_items'] = RecipeItemSerializer(recipe_items, many=True).data
        return data
    
    @transaction.atomic
    def update(self, instance, validated_data):
        """
        Update product and nested recipe items atomically.

        - Product scalar fields are updated normally.
        - If recipe_items is provided, existing recipe rows are replaced with the payload.
        - If recipe_items is omitted, existing recipe rows are left unchanged.
        """
        recipe_items_data = validated_data.pop('recipe_items', None)

        # Update main product fields first.
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # Only touch recipe rows when the client explicitly sends recipe_items.
        if recipe_items_data is not None:
            # Replace existing recipe rows with the provided set.
            instance.recipe_items.all().delete()

            if recipe_items_data:
                ingredient_ids = [item['ingredient_id'] for item in recipe_items_data]
                ingredient_map = {
                    ing.id: ing
                    for ing in Ingredient.objects.filter(id__in=ingredient_ids)
                }

                recipe_objects = []
                for item in recipe_items_data:
                    ingredient = ingredient_map.get(item['ingredient_id'])
                    if ingredient is None:
                        raise serializers.ValidationError(
                            f"Ingredient with id {item['ingredient_id']} does not exist"
                        )

                    recipe_objects.append(
                        RecipeItem(
                            product_id=instance,
                            ingredient_id=ingredient,
                            quantity_required=item['quantity_required'],
                        )
                    )

                RecipeItem.objects.bulk_create(recipe_objects)

        return instance


class ProductSearchSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for search results.
    Used for: GET /api/products/?search=query
    
    Uses Product.current_stock as the absolute source of truth for quantity.
    """
    category_name = serializers.CharField(source='category_id.name', read_only=True)
    quantity = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'product_id', 'name', 'category_name',
            'selling_price', 'quantity', 'status'
        ]
        read_only_fields = ['product_id', 'quantity']
    
    def get_quantity(self, obj):
        """Return current product stock from Product.current_stock."""
        return float(obj.current_stock) if obj.current_stock else 0.0


class ProductFilterSerializer(serializers.Serializer):
    """
    Serializer for validating product filter parameters.
    Used for query parameter validation.
    """
    category_id = serializers.IntegerField(required=False, min_value=1)
    status = serializers.ChoiceField(
        choices=['available', 'low_stock', 'out_of_stock'],
        required=False
    )
    search = serializers.CharField(required=False, max_length=100)
    ordering = serializers.ChoiceField(
        choices=['selling_price', '-selling_price', 'profit_margin', '-profit_margin', 'current_stock', '-current_stock', 'name', '-name'],
        required=False
    )
    page = serializers.IntegerField(required=False, min_value=1)
    page_size = serializers.IntegerField(required=False, min_value=1, max_value=100)
