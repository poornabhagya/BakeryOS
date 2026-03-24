from rest_framework import serializers
from api.models import ProductBatch, Product
from datetime import date, timedelta


class ProductBatchListSerializer(serializers.ModelSerializer):
    """Serializer for listing product batches with minimal info"""
    
    product_name = serializers.CharField(source='product_id.name', read_only=True)
    product_id_val = serializers.IntegerField(source='product_id.id', read_only=True)
    days_until_expiry = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductBatch
        fields = [
            'id',
            'batch_id',
            'product_id',
            'product_id_val',
            'product_name',
            'quantity',
            'made_date',
            'expire_date',
            'status',
            'days_until_expiry',
            'is_expired',
            'created_at'
        ]
        read_only_fields = fields
    
    def get_days_until_expiry(self, obj):
        """Get days remaining until expiry"""
        return obj.days_until_expiry
    
    def get_is_expired(self, obj):
        """Get expiry status"""
        return obj.is_expired


class ProductBatchDetailSerializer(serializers.ModelSerializer):
    """Serializer for product batch details with all information"""
    
    product_name = serializers.CharField(source='product_id.name', read_only=True)
    product_cost_price = serializers.DecimalField(
        source='product_id.cost_price',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    product_selling_price = serializers.DecimalField(
        source='product_id.selling_price',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    product_shelf_life = serializers.IntegerField(source='product_id.shelf_life', read_only=True)
    product_shelf_unit = serializers.CharField(source='product_id.shelf_unit', read_only=True)
    days_until_expiry = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    expiring_soon = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductBatch
        fields = [
            'id',
            'batch_id',
            'product_id',
            'product_name',
            'product_cost_price',
            'product_selling_price',
            'product_shelf_life',
            'product_shelf_unit',
            'quantity',
            'made_date',
            'expire_date',
            'status',
            'days_until_expiry',
            'is_expired',
            'expiring_soon',
            'notes',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'batch_id',
            'product_name',
            'product_cost_price',
            'product_selling_price',
            'product_shelf_life',
            'product_shelf_unit',
            'days_until_expiry',
            'is_expired',
            'expiring_soon',
            'created_at',
            'updated_at'
        ]
    
    def get_days_until_expiry(self, obj):
        """Get days remaining until expiry"""
        return obj.days_until_expiry
    
    def get_is_expired(self, obj):
        """Get expiry status"""
        return obj.is_expired
    
    def get_expiring_soon(self, obj):
        """Check if batch expires within 2 days"""
        return obj.expiring_soon


class ProductBatchCreateSerializer(serializers.Serializer):
    """Serializer for creating a new product batch"""
    
    product_id = serializers.IntegerField()
    quantity = serializers.DecimalField(max_digits=10, decimal_places=2)
    made_date = serializers.DateField()
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate_product_id(self, value):
        """Validate product exists"""
        try:
            product = Product.objects.get(id=value)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found")
        return value
    
    def validate_quantity(self, value):
        """Validate quantity is positive"""
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0")
        return value
    
    def validate_made_date(self, value):
        """Validate made_date is not in future"""
        if value > date.today():
            raise serializers.ValidationError("Made date cannot be in the future")
        return value
    
    def create(self, validated_data):
        """Create a new product batch"""
        product = Product.objects.get(id=validated_data['product_id'])
        
        batch = ProductBatch.objects.create(
            product_id=product,
            quantity=validated_data['quantity'],
            made_date=validated_data['made_date'],
            notes=validated_data.get('notes', '')
        )
        
        return batch


class ProductBatchUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating product batch"""
    
    class Meta:
        model = ProductBatch
        fields = [
            'quantity',
            'made_date',
            'status',
            'notes'
        ]
    
    def validate_quantity(self, value):
        """Validate quantity is positive"""
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0")
        return value
    
    def validate_made_date(self, value):
        """Validate made_date is not in future"""
        if value > date.today():
            raise serializers.ValidationError("Made date cannot be in the future")
        return value


class ProductBatchUseBatchSerializer(serializers.Serializer):
    """Serializer for using batch quantity"""
    
    quantity_used = serializers.DecimalField(max_digits=10, decimal_places=2)
    reason = serializers.CharField(required=False, allow_blank=True)
    
    def validate_quantity_used(self, value):
        """Validate quantity is positive"""
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0")
        return value


class ProductBatchExpiringSerializer(serializers.ModelSerializer):
    """Serializer for expiring batches"""
    
    product_name = serializers.CharField(source='product_id.name', read_only=True)
    days_until_expiry = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductBatch
        fields = [
            'id',
            'batch_id',
            'product_id',
            'product_name',
            'quantity',
            'expire_date',
            'days_until_expiry',
            'created_at'
        ]
        read_only_fields = fields
    
    def get_days_until_expiry(self, obj):
        """Get days remaining until expiry"""
        return obj.days_until_expiry
