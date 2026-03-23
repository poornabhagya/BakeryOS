from rest_framework import serializers
from api.models import Ingredient, Category


class IngredientListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for ingredient list views.
    
    Includes: id, ingredient_id, name, category info, quantity status
    """
    category_name = serializers.CharField(source='category_id.name', read_only=True)
    stock_status = serializers.CharField(read_only=True)
    
    class Meta:
        model = Ingredient
        fields = [
            'id',
            'ingredient_id',
            'name',
            'category_id',
            'category_name',
            'tracking_type',
            'base_unit',
            'total_quantity',
            'low_stock_threshold',
            'stock_status',
            'is_active',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'ingredient_id',
            'total_quantity',
            'stock_status',
            'created_at',
        ]


class IngredientDetailSerializer(serializers.ModelSerializer):
    """
    Complete serializer for ingredient detail view.
    
    Includes: All fields + batch count, recipe count, supplier info
    """
    category_name = serializers.CharField(source='category_id.name', read_only=True)
    stock_status = serializers.CharField(read_only=True)
    batch_count = serializers.SerializerMethodField()
    is_low_stock = serializers.SerializerMethodField()
    is_out_of_stock = serializers.SerializerMethodField()
    shelf_life_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Ingredient
        fields = [
            'id',
            'ingredient_id',
            'name',
            'category_id',
            'category_name',
            'supplier',
            'supplier_contact',
            'tracking_type',
            'base_unit',
            'total_quantity',
            'low_stock_threshold',
            'shelf_life',
            'shelf_unit',
            'shelf_life_display',
            'stock_status',
            'is_low_stock',
            'is_out_of_stock',
            'batch_count',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'ingredient_id',
            'total_quantity',
            'stock_status',
            'is_low_stock',
            'is_out_of_stock',
            'batch_count',
            'shelf_life_display',
            'created_at',
            'updated_at',
        ]
    
    def get_batch_count(self, obj):
        """Get count of active batches for this ingredient"""
        # Will be implemented after IngredientBatch model is created
        return 0
    
    def get_is_low_stock(self, obj):
        """Get low stock status"""
        return obj.is_low_stock()
    
    def get_is_out_of_stock(self, obj):
        """Get out of stock status"""
        return obj.is_out_of_stock()
    
    def get_shelf_life_display(self, obj):
        """Get formatted shelf life display"""
        return f"{obj.shelf_life} {obj.get_shelf_unit_display().lower()}"


class IngredientCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new ingredients.
    
    Includes comprehensive validation.
    """
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.filter(type='Ingredient'))
    
    class Meta:
        model = Ingredient
        fields = [
            'name',
            'category_id',
            'supplier',
            'supplier_contact',
            'tracking_type',
            'base_unit',
            'low_stock_threshold',
            'shelf_life',
            'shelf_unit',
        ]
    
    def validate_category_id(self, value):
        """Ensure category is Ingredient type"""
        if value.type != 'Ingredient':
            raise serializers.ValidationError(
                f"Category '{value.name}' is a {value.type} category. "
                "Please select an Ingredient-type category."
            )
        return value
    
    def validate_name(self, value):
        """Validate ingredient name"""
        if not value or not value.strip():
            raise serializers.ValidationError("Name cannot be empty.")
        if len(value) < 2:
            raise serializers.ValidationError("Name must be at least 2 characters.")
        if len(value) > 100:
            raise serializers.ValidationError("Name must be at most 100 characters.")
        return value.strip()
    
    def validate_base_unit(self, value):
        """Validate base unit"""
        if not value or not value.strip():
            raise serializers.ValidationError("Base unit cannot be empty.")
        if len(value) > 20:
            raise serializers.ValidationError("Base unit must be at most 20 characters.")
        return value.strip()
    
    def validate_low_stock_threshold(self, value):
        """Validate low stock threshold"""
        if value < 0:
            raise serializers.ValidationError("Low stock threshold cannot be negative.")
        return value
    
    def validate_shelf_life(self, value):
        """Validate shelf life"""
        if value <= 0:
            raise serializers.ValidationError("Shelf life must be greater than 0.")
        return value
    
    def validate(self, data):
        """Validate combined fields"""
        # Check for duplicate name in same category
        category = data.get('category_id')
        name = data.get('name')
        
        if category and name:
            existing = Ingredient.objects.filter(
                category_id=category,
                name__iexact=name
            ).exists()
            
            if existing:
                raise serializers.ValidationError(
                    f"An ingredient named '{name}' already exists in category '{category.name}'."
                )
        
        return data
    
    def create(self, validated_data):
        """Create ingredient instance"""
        return Ingredient.objects.create(**validated_data)


class IngredientUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating existing ingredients.
    
    Only allows updating specific fields (not name, category, tracking_type).
    """
    
    class Meta:
        model = Ingredient
        fields = [
            'supplier',
            'supplier_contact',
            'base_unit',
            'low_stock_threshold',
            'shelf_life',
            'shelf_unit',
            'is_active',
        ]
    
    def validate_base_unit(self, value):
        """Validate base unit"""
        if not value or not value.strip():
            raise serializers.ValidationError("Base unit cannot be empty.")
        return value.strip()
    
    def validate_low_stock_threshold(self, value):
        """Validate low stock threshold"""
        if value < 0:
            raise serializers.ValidationError("Low stock threshold cannot be negative.")
        return value
    
    def validate_shelf_life(self, value):
        """Validate shelf life"""
        if value <= 0:
            raise serializers.ValidationError("Shelf life must be greater than 0.")
        return value


class IngredientMinimalSerializer(serializers.ModelSerializer):
    """
    Minimal serializer for embedding in other responses.
    
    Useful when showing ingredient info in batches, recipes, etc.
    """
    
    class Meta:
        model = Ingredient
        fields = [
            'id',
            'ingredient_id',
            'name',
            'base_unit',
            'total_quantity',
            'stock_status',
        ]
        read_only_fields = fields
