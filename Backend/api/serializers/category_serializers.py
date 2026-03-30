from rest_framework import serializers
from api.models import Category


class CategoryListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing categories (lightweight)
    Shows: category_id, name, type, description, low_stock_alert
    """
    
    class Meta:
        model = Category
        fields = [
            'id',
            'category_id',
            'name',
            'type',
            'description',
            'low_stock_alert',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'category_id',
            'created_at',
            'updated_at',
        ]


class CategoryDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed category view
    Includes all fields with read-only timestamps
    """
    
    # Count of items in this category (optional)
    item_count = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Category
        fields = [
            'id',
            'category_id',
            'name',
            'type',
            'description',
            'low_stock_alert',
            'item_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'category_id',
            'created_at',
            'updated_at',
        ]
    
    def get_item_count(self, obj):
        """
        Return count of items in this category
        (Products or Ingredients depending on type)
        """
        # This will be implemented when we have Product and Ingredient models
        return 0


class CategoryCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating categories
    Requires: name, type
    Optional: description, low_stock_alert
    """
    
    class Meta:
        model = Category
        fields = [
            'name',
            'type',
            'description',
            'low_stock_alert',
        ]
    
    def validate_name(self, value):
        """
        Validate that name:
        - Is not empty
        - Is unique for the given type
        """
        if not value or not value.strip():
            raise serializers.ValidationError(
                "Category name cannot be empty."
            )
        
        # Check uniqueness with type
        type_value = self.initial_data.get('type')
        if type_value:
            existing = Category.objects.filter(
                name__iexact=value.strip(),
                type=type_value
            ).exists()
            
            if existing:
                raise serializers.ValidationError(
                    f"A category named '{value}' already exists for type '{type_value}'."
                )
        
        return value.strip()
    
    def validate_type(self, value):
        """
        Validate that type is one of the allowed choices
        """
        valid_types = ['Product', 'Ingredient']
        if value not in valid_types:
            raise serializers.ValidationError(
                f"Type must be one of {valid_types}. Got: {value}"
            )
        return value
    
    def create(self, validated_data):
        """Create category with auto-generated ID"""
        return Category.objects.create(**validated_data)


class CategoryUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating categories
    
    Updatable fields:
    - name: Can be updated for existing categories
    - description: Optional detailed description
    - low_stock_alert: Optional threshold (null for Ingredient categories)
    
    Read-only fields:
    - type: Cannot be changed once created
    - category_id: Auto-generated, immutable
    """
    
    class Meta:
        model = Category
        fields = [
            'name',
            'description',
            'low_stock_alert',
        ]
        read_only_fields = [
            'type',
            'category_id',
        ]


class CategoryMinimalSerializer(serializers.ModelSerializer):
    """
    Minimal serializer for embedding in other serializers
    Shows: category_id, name, type
    """
    
    class Meta:
        model = Category
        fields = [
            'id',
            'category_id',
            'name',
            'type',
        ]
        read_only_fields = fields
