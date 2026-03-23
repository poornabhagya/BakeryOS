from rest_framework import serializers
from api.models import IngredientBatch, Ingredient
from django.utils import timezone


class BatchListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing batches.
    Used for list view with essential fields and status info.
    """
    ingredient_name = serializers.CharField(source='ingredient_id.name', read_only=True)
    ingredient_unit = serializers.CharField(source='ingredient_id.base_unit', read_only=True)
    is_expired = serializers.SerializerMethodField()
    days_until_expiry = serializers.SerializerMethodField()
    
    class Meta:
        model = IngredientBatch
        fields = [
            'id', 'batch_id', 'ingredient_id', 'ingredient_name', 'ingredient_unit',
            'quantity', 'current_qty', 'made_date', 'expire_date', 'status',
            'is_expired', 'days_until_expiry', 'created_at'
        ]
        read_only_fields = ['batch_id', 'created_at']
    
    def get_is_expired(self, obj):
        """Check if batch is expired"""
        return obj.is_expired
    
    def get_days_until_expiry(self, obj):
        """Get days until expiry"""
        return obj.days_until_expiry


class BatchDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for batch details.
    Includes ingredient details, computed fields, and financial info.
    """
    ingredient_name = serializers.CharField(source='ingredient_id.name', read_only=True)
    ingredient_unit = serializers.CharField(source='ingredient_id.base_unit', read_only=True)
    ingredient_tracking = serializers.CharField(
        source='ingredient_id.tracking_type',
        read_only=True
    )
    is_expired = serializers.SerializerMethodField()
    days_until_expiry = serializers.SerializerMethodField()
    remaining_qty = serializers.SerializerMethodField()
    total_cost = serializers.SerializerMethodField()
    expiry_progress = serializers.SerializerMethodField()
    
    class Meta:
        model = IngredientBatch
        fields = [
            'id', 'batch_id', 'ingredient_id', 'ingredient_name', 'ingredient_unit',
            'ingredient_tracking', 'quantity', 'current_qty', 'remaining_qty',
            'cost_price', 'total_cost', 'made_date', 'expire_date', 'status',
            'is_expired', 'days_until_expiry', 'expiry_progress', 'created_at', 'updated_at'
        ]
        read_only_fields = ['batch_id', 'created_at', 'updated_at']
    
    def get_is_expired(self, obj):
        """Check if batch is expired"""
        return obj.is_expired
    
    def get_days_until_expiry(self, obj):
        """Get days until expiry"""
        return obj.days_until_expiry
    
    def get_remaining_qty(self, obj):
        """Get remaining quantity (alias for current_qty)"""
        return obj.current_qty
    
    def get_total_cost(self, obj):
        """Calculate total cost"""
        return obj.total_cost
    
    def get_expiry_progress(self, obj):
        """Get expiry progress percentage"""
        return obj.expiry_progress


class BatchCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating/updating batches.
    Includes custom validation rules.
    """
    class Meta:
        model = IngredientBatch
        fields = [
            'ingredient_id', 'quantity', 'current_qty', 'cost_price',
            'made_date', 'expire_date'
        ]
    
    def validate_quantity(self, value):
        """Validate quantity is positive"""
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0.")
        return value
    
    def validate_current_qty(self, value):
        """Validate current_qty is non-negative"""
        if value < 0:
            raise serializers.ValidationError("Current quantity cannot be negative.")
        return value
    
    def validate_cost_price(self, value):
        """Validate cost_price if provided"""
        if value is not None and value <= 0:
            raise serializers.ValidationError("Cost price must be greater than 0 or null.")
        return value
    
    def validate(self, attrs):
        """
        Validate batch data:
        1. current_qty <= quantity
        2. expire_date >= made_date
        """
        made_date = attrs.get('made_date')
        expire_date = attrs.get('expire_date')
        quantity = attrs.get('quantity')
        current_qty = attrs.get('current_qty')
        
        # Validate expire_date >= made_date
        if made_date and expire_date and expire_date < made_date:
            raise serializers.ValidationError({
                'expire_date': 'Expiry date must be on or after made date.'
            })
        
        # Validate current_qty <= quantity
        if current_qty is not None and quantity and current_qty > quantity:
            raise serializers.ValidationError({
                'current_qty': 'Current quantity cannot exceed received quantity.'
            })
        
        # Set current_qty to quantity if not provided
        if current_qty is None:
            attrs['current_qty'] = quantity
        
        return attrs


class BatchConsumeSerializer(serializers.Serializer):
    """
    Serializer for consuming from a batch.
    Used for POST /batches/{id}/consume/ endpoint.
    """
    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=True,
        help_text="Amount to consume from batch"
    )
    
    def validate_amount(self, value):
        """Validate consume amount"""
        if value <= 0:
            raise serializers.ValidationError("Consume amount must be greater than 0.")
        return value


class BatchFilterSerializer(serializers.Serializer):
    """
    Serializer for batch filtering parameters.
    """
    ingredient_id = serializers.IntegerField(required=False)
    status = serializers.ChoiceField(
        choices=['Active', 'Expired', 'Used'],
        required=False
    )
    expiring_within = serializers.IntegerField(
        required=False,
        help_text="Days within which batches are expiring"
    )
