from rest_framework import serializers
from decimal import Decimal
from api.models import IngredientWastage, Ingredient, IngredientBatch, WastageReason, User


class IngredientWastageListSerializer(serializers.ModelSerializer):
    """
    List serializer for ingredient wastages.
    Shows summary information without nested objects.
    """
    ingredient_name = serializers.CharField(source='ingredient_id.name', read_only=True)
    category_name = serializers.CharField(source='ingredient_id.category_id.name', read_only=True)
    batch_reference = serializers.SerializerMethodField()
    reason_text = serializers.CharField(source='reason_id.reason', read_only=True)
    reported_by_name = serializers.SerializerMethodField()
    
    class Meta:
        model = IngredientWastage
        fields = [
            'id',
            'wastage_id',
            'ingredient_id',
            'ingredient_name',
            'category_name',
            'batch_id',
            'batch_reference',
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
            'ingredient_name',
            'category_name',
            'batch_reference',
            'reason_text',
            'reported_by_name',
            'total_loss',
            'created_at',
        ]
    
    def get_batch_reference(self, obj):
        """Get batch reference if batch exists."""
        if obj.batch_id:
            return {
                'id': obj.batch_id.id,
                'batch_id': obj.batch_id.batch_id
            }
        return None
    
    def get_reported_by_name(self, obj):
        """Get the full name or username of the reporter."""
        if obj.reported_by:
            full_name = obj.reported_by.get_full_name()
            return full_name if full_name else obj.reported_by.username
        return "System"


class IngredientWastageDetailSerializer(serializers.ModelSerializer):
    """
    Detail serializer for ingredient wastages.
    Includes nested ingredient, batch, reason, and user information.
    """
    # Nested ingredient info
    ingredient_detail = serializers.SerializerMethodField()
    
    # Nested batch info
    batch_detail = serializers.SerializerMethodField()
    
    # Nested reason info
    reason_detail = serializers.SerializerMethodField()
    
    # Nested user info
    reported_by_detail = serializers.SerializerMethodField()
    
    class Meta:
        model = IngredientWastage
        fields = [
            'id',
            'wastage_id',
            'ingredient_id',
            'ingredient_detail',
            'batch_id',
            'batch_detail',
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
            'ingredient_detail',
            'batch_detail',
            'reason_detail',
            'reported_by_detail',
            'total_loss',
            'created_at',
            'updated_at',
        ]
    
    def get_ingredient_detail(self, obj):
        """Get ingredient details."""
        if obj.ingredient_id:
            return {
                'id': obj.ingredient_id.id,
                'ingredient_id': obj.ingredient_id.ingredient_id,
                'name': obj.ingredient_id.name,
                'supplier': obj.ingredient_id.supplier,
                'base_unit': obj.ingredient_id.base_unit,
                'total_quantity': str(obj.ingredient_id.total_quantity),
            }
        return None
    
    def get_batch_detail(self, obj):
        """Get batch details if available."""
        if obj.batch_id:
            return {
                'id': obj.batch_id.id,
                'batch_id': obj.batch_id.batch_id,
                'quantity': str(obj.batch_id.quantity),
                'current_qty': str(obj.batch_id.current_qty),
                'made_date': obj.batch_id.made_date,
                'expire_date': obj.batch_id.expire_date,
                'status': obj.batch_id.status,
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


class IngredientWastageCreateSerializer(serializers.ModelSerializer):
    """
    Create serializer for ingredient wastages.
    Includes validation and returns created wastage_id in response.
    """
    class Meta:
        model = IngredientWastage
        fields = [
            'id',
            'wastage_id',
            'ingredient_id',
            'batch_id',
            'quantity',
            'unit_cost',
            'reason_id',
            'reported_by',
            'notes',
        ]
        read_only_fields = ['id', 'wastage_id']
    
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
    
    def validate_ingredient_id(self, value):
        """Validate that ingredient exists."""
        if not value:
            raise serializers.ValidationError("Ingredient is required")
        if not Ingredient.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Ingredient does not exist")
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
        Check that ingredient and optional batch have sufficient quantity.
        """
        ingredient = data.get('ingredient_id')
        batch = data.get('batch_id')
        quantity = data.get('quantity')
        
        if ingredient and quantity:
            # Check if ingredient has enough quantity
            if ingredient.total_quantity < quantity:
                raise serializers.ValidationError(
                    f"Insufficient ingredient quantity. Available: {ingredient.total_quantity}, "
                    f"Trying to waste: {quantity}"
                )

        if batch and quantity:
            # Ensure the selected batch has enough remaining stock
            if batch.current_qty < quantity:
                raise serializers.ValidationError(
                    f"Insufficient batch quantity. Available in batch {batch.batch_id}: {batch.current_qty}, "
                    f"Trying to waste: {quantity}"
                )
        
        return data
    
    def create(self, validated_data):
        """
        Create the wastage record and deduct stock.

        If a batch is linked, deduct from that batch's current_qty and save the batch.
        Batch save triggers ingredient total sync via existing batch signals.

        If no batch is linked, deduct directly from ingredient total_quantity.
        """
        ingredient = validated_data['ingredient_id']
        batch = validated_data.get('batch_id')
        quantity = validated_data['quantity']

        # Normalize to cost-per-base-unit for accurate loss calculation.
        if batch and batch.quantity and batch.quantity > 0:
            batch_total_cost = batch.total_batch_cost if batch.total_batch_cost is not None else Decimal('0')
            validated_data['unit_cost'] = batch_total_cost / batch.quantity

        # Deduct from specific batch stock when linked
        if batch:
            batch.current_qty -= quantity
            batch.save()
        else:
            # Fallback path for wastage records without a linked batch
            ingredient.total_quantity -= quantity
            ingredient.save()
        
        # Create wastage record (save() will generate wastage_id)
        wastage = IngredientWastage.objects.create(**validated_data)
        
        return wastage
