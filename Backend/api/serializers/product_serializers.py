from rest_framework import serializers
from api.models import Product, Category


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
    """
    class Meta:
        model = Product
        fields = [
            'category_id', 'name', 'description', 'image_url',
            'cost_price', 'selling_price', 'current_stock',
            'shelf_life', 'shelf_unit'
        ]
    
    def validate(self, data):
        """Custom validation for product data"""
        # Check cost_price > 0
        if data.get('cost_price', 0) <= 0:
            raise serializers.ValidationError({
                'cost_price': 'Cost price must be greater than 0'
            })
        
        # Check selling_price > cost_price (should make profit)
        cost = data.get('cost_price')
        selling = data.get('selling_price')
        if cost and selling and selling <= cost:
            raise serializers.ValidationError({
                'selling_price': 'Selling price must be greater than cost price'
            })
        
        # Check shelf_life > 0
        if data.get('shelf_life', 0) <= 0:
            raise serializers.ValidationError({
                'shelf_life': 'Shelf life must be at least 1'
            })
        
        # Check current_stock >= 0
        if data.get('current_stock', 0) < 0:
            raise serializers.ValidationError({
                'current_stock': 'Stock quantity cannot be negative'
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
                    'name': f'Product "{name}" already exists in this category'
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
