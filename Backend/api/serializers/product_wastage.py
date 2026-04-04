from rest_framework import serializers
from decimal import Decimal
from api.models import ProductWastage, Product, WastageReason, User


class ProductWastageListSerializer(serializers.ModelSerializer):
    """
    List serializer for product wastages.
    Shows summary information without nested objects.
    """
    product_name = serializers.CharField(source='product_id.name', read_only=True)
    category_name = serializers.CharField(source='product_id.category_id.name', read_only=True)
    reason_text = serializers.CharField(source='reason_id.reason', read_only=True)
    reported_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductWastage
        fields = [
            'id',
            'wastage_id',
            'product_id',
            'product_name',
            'category_name',
            'quantity',
            'unit_cost',
            'total_loss',
            'reason_id',
            'reason_text',
            'reported_by',
            'reported_by_name',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'wastage_id',
            'product_name',
            'category_name',
            'reason_text',
            'reported_by_name',
            'total_loss',
            'created_at',
        ]
    
    def get_reported_by_name(self, obj):
        """Get the full name or username of the reporter."""
        if obj.reported_by:
            full_name = obj.reported_by.get_full_name()
            return full_name if full_name else obj.reported_by.username
        return "System"


class ProductWastageDetailSerializer(serializers.ModelSerializer):
    """
    Detail serializer for product wastages.
    Includes nested product, reason, and user information.
    """
    # Nested product info
    product_detail = serializers.SerializerMethodField()
    
    # Nested reason info
    reason_detail = serializers.SerializerMethodField()
    
    # Nested user info
    reported_by_detail = serializers.SerializerMethodField()
    
    class Meta:
        model = ProductWastage
        fields = [
            'id',
            'wastage_id',
            'product_id',
            'product_detail',
            'quantity',
            'unit_cost',
            'total_loss',
            'reason_id',
            'reason_detail',
            'reported_by',
            'reported_by_detail',
            'notes',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'wastage_id',
            'product_detail',
            'reason_detail',
            'reported_by_detail',
            'total_loss',
            'created_at',
            'updated_at',
        ]
    
    def get_product_detail(self, obj):
        """Get product details."""
        if obj.product_id:
            return {
                'id': obj.product_id.id,
                'product_id': obj.product_id.product_id,
                'name': obj.product_id.name,
                'cost_price': str(obj.product_id.cost_price),
                'selling_price': str(obj.product_id.selling_price),
                'current_stock': str(obj.product_id.current_stock),
            }
        return None
    
    def get_reason_detail(self, obj):
        """Get wastage reason details."""
        if obj.reason_id:
            return {
                'id': obj.reason_id.id,
                'reason_id': obj.reason_id.reason_id,
                'reason': obj.reason_id.reason,
                'description': obj.reason_id.description,
            }
        return None
    
    def get_reported_by_detail(self, obj):
        """Get reporter details."""
        if obj.reported_by:
            return {
                'id': obj.reported_by.id,
                'username': obj.reported_by.username,
                'full_name': obj.reported_by.get_full_name(),
                'role': obj.reported_by.role,
                'email': obj.reported_by.email,
            }
        return None


class ProductWastageCreateSerializer(serializers.ModelSerializer):
    """
    Create serializer for product wastages.
    Includes validation and returns created wastage_id in response.
    Automatically deducts from batch and product stock.
    """
    batch_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    class Meta:
        model = ProductWastage
        fields = [
            'id',
            'wastage_id',
            'product_id',
            'batch_id',
            'batch',
            'quantity',
            'unit_cost',
            'reason_id',
            'reported_by',
            'notes',
        ]
        read_only_fields = ['id', 'wastage_id', 'batch']
    
    def validate_quantity(self, value):
        """Validate that quantity is positive."""
        if not value or value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0")
        return value
    
    def validate_unit_cost(self, value):
        """Validate that unit cost is non-negative."""
        if value is None or value < 0:
            raise serializers.ValidationError("Unit cost cannot be negative")
        return value
    
    def validate_product_id(self, value):
        """Validate that product exists."""
        if not value:
            raise serializers.ValidationError("Product is required")
        if not Product.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Product does not exist")
        return value
    
    def validate_reason_id(self, value):
        """Validate that reason exists."""
        if not value:
            raise serializers.ValidationError("Wastage reason is required")
        if not WastageReason.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Wastage reason does not exist")
        if (value.reason or '').strip().lower() == 'expired':
            raise serializers.ValidationError(
                "'Expired' is reserved for automated system expiration and cannot be selected manually."
            )
        return value
    
    def validate(self, data):
        """
        Validate the entire wastage record.
        Check that product has sufficient stock.
        """
        product = data.get('product_id')
        quantity = data.get('quantity')
        batch_id = self.initial_data.get('batch_id')
        
        if product and quantity:
            # Check if product has enough stock
            if product.current_stock < quantity:
                raise serializers.ValidationError(
                    f"Insufficient stock. Available: {product.current_stock}, "
                    f"Trying to waste: {quantity}"
                )
            
            # If batch_id is provided, validate batch exists and has enough qty
            if batch_id:
                from api.models import ProductBatch
                try:
                    batch = ProductBatch.objects.get(id=batch_id)
                    if batch.current_qty < quantity:
                        raise serializers.ValidationError(
                            f"Insufficient batch stock. Available: {batch.current_qty}, "
                            f"Trying to waste: {quantity}"
                        )
                except ProductBatch.DoesNotExist:
                    raise serializers.ValidationError("Batch does not exist")
        
        return data
    
    def create(self, validated_data):
        """
        Create the wastage record. Stock deduction happens in the model's save() method.
        """
        # Get batch_id from initial data (since it's write_only)
        batch_id = self.initial_data.get('batch_id')
        
        # Link batch if provided
        if batch_id:
            from api.models import ProductBatch
            try:
                batch = ProductBatch.objects.get(id=batch_id)
                validated_data['batch'] = batch
            except ProductBatch.DoesNotExist:
                pass
        
        # Create wastage record
        # The model's save() method will handle all stock deductions
        wastage = ProductWastage.objects.create(**validated_data)
        
        return wastage
