from rest_framework import serializers
from api.models import Product, Category
from api.validators import (
    validate_positive_number, validate_non_negative_number,
    sanitize_string, sanitize_html
)
from decimal import Decimal


class ProductListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing products with calculated fields.
    Used for: GET /api/products/
    """
    category_name = serializers.CharField(source='category_id.name', read_only=True)
    profit_margin = serializers.SerializerMethodField()
    status = serializers.CharField(read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'product_id', 'name', 'category_id', 'category_name',
            'cost_price', 'selling_price', 'profit_margin',
            'current_stock', 'status', 'shelf_life', 'shelf_unit',
            'created_at'
        ]
        read_only_fields = ['product_id', 'created_at']
    
    def get_profit_margin(self, obj):
        """Return profit margin as percentage"""
        return round(obj.profit_margin, 2)


class ProductDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for detailed product information.
    Includes category details, profit margin, and recipe items.
    Used for: GET /api/products/{id}/
    """
    category_name = serializers.CharField(source='category_id.name', read_only=True)
    category_type = serializers.CharField(source='category_id.type', read_only=True)
    profit_margin = serializers.SerializerMethodField()
    status = serializers.CharField(read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)
    is_out_of_stock = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'product_id', 'name', 'description', 'image_url',
            'category_id', 'category_name', 'category_type',
            'cost_price', 'selling_price', 'profit_margin',
            'current_stock', 'status', 'is_low_stock', 'is_out_of_stock',
            'shelf_life', 'shelf_unit',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['product_id', 'created_at', 'updated_at']
    
    def get_profit_margin(self, obj):
        """Return profit margin as percentage with 2 decimals"""
        return round(obj.profit_margin, 2)


class ProductCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating products.
    Validates required fields and constraints.
    Used for: POST /api/products/, PUT /api/products/{id}/, PATCH /api/products/{id}/
    
    Validation:
    - name: Non-empty, unique per category, sanitized
    - cost_price: Must be positive (> 0)
    - selling_price: Must be > cost_price
    - shelf_life: Must be positive integer
    - current_stock: Must be non-negative
    """
    class Meta:
        model = Product
        fields = [
            'category_id', 'name', 'description', 'image_url',
            'cost_price', 'selling_price', 'current_stock',
            'shelf_life', 'shelf_unit'
        ]
    
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
    
    def create(self, validated_data):
        """Create product with auto-generated product_id"""
        return Product.objects.create(**validated_data)
    
    def update(self, instance, validated_data):
        """Update product fields"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class ProductSearchSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for search results.
    Used for: GET /api/products/?search=query
    """
    category_name = serializers.CharField(source='category_id.name', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'product_id', 'name', 'category_name',
            'selling_price', 'current_stock', 'status'
        ]
        read_only_fields = ['product_id']


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
