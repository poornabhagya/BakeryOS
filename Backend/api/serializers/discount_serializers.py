from rest_framework import serializers
from api.models import Discount, Category, Product
from django.core.exceptions import ValidationError


class DiscountListSerializer(serializers.ModelSerializer):
    """Serializer for listing discounts with basic info"""
    
    target_category_name = serializers.CharField(
        source='target_category_id.name',
        read_only=True,
        allow_null=True
    )
    target_product_name = serializers.CharField(
        source='target_product_id.name',
        read_only=True,
        allow_null=True
    )
    
    class Meta:
        model = Discount
        fields = [
            'id',
            'discount_id',
            'name',
            'discount_type',
            'value',
            'applicable_to',
            'target_category_id',
            'target_category_name',
            'target_product_id',
            'target_product_name',
            'start_date',
            'end_date',
            'is_active',
            'created_at',
        ]
        read_only_fields = ['id', 'discount_id', 'created_at']


class DiscountDetailSerializer(serializers.ModelSerializer):
    """Serializer for discount details with all info"""
    
    target_category = serializers.SerializerMethodField()
    target_product = serializers.SerializerMethodField()
    is_applicable_now = serializers.SerializerMethodField()
    
    class Meta:
        model = Discount
        fields = [
            'id',
            'discount_id',
            'name',
            'description',
            'discount_type',
            'value',
            'applicable_to',
            'target_category_id',
            'target_category',
            'target_product_id',
            'target_product',
            'start_date',
            'end_date',
            'start_time',
            'end_time',
            'is_active',
            'is_applicable_now',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'discount_id', 'created_at', 'updated_at']
    
    def get_target_category(self, obj):
        """Get category details"""
        if obj.target_category_id:
            return {
                'id': obj.target_category_id.id,
                'category_id': obj.target_category_id.category_id,
                'name': obj.target_category_id.name,
            }
        return None
    
    def get_target_product(self, obj):
        """Get product details"""
        if obj.target_product_id:
            return {
                'id': obj.target_product_id.id,
                'product_id': obj.target_product_id.product_id,
                'name': obj.target_product_id.name,
                'selling_price': str(obj.target_product_id.selling_price),
            }
        return None
    
    def get_is_applicable_now(self, obj):
        """Check if applicable at current time"""
        return obj.is_applicable_now()


class DiscountCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating/updating discounts with validation"""
    
    class Meta:
        model = Discount
        fields = [
            'name',
            'description',
            'discount_type',
            'value',
            'applicable_to',
            'target_category_id',
            'target_product_id',
            'start_date',
            'end_date',
            'start_time',
            'end_time',
            'is_active',
        ]
    
    def validate(self, data):
        """Custom validation for discount constraints"""
        
        # Validate discount value
        discount_type = data.get('discount_type', 'Percentage')
        value = data.get('value')
        
        if discount_type == 'Percentage':
            if not (0 < value <= 100):
                raise serializers.ValidationError(
                    {'value': 'Percentage must be between 0 and 100'}
                )
        elif discount_type == 'FixedAmount':
            if value <= 0:
                raise serializers.ValidationError(
                    {'value': 'Fixed amount must be greater than 0'}
                )
        
        # Validate date range
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise serializers.ValidationError(
                {'start_date': 'Start date cannot be after end date'}
            )
        
        # Validate time range
        start_time = data.get('start_time')
        end_time = data.get('end_time')
        
        if start_time and end_time and start_time >= end_time:
            raise serializers.ValidationError(
                {'start_time': 'Start time must be before end time'}
            )
        
        # Validate applicable_to constraints
        applicable_to = data.get('applicable_to', 'All')
        category_id = data.get('target_category_id')
        product_id = data.get('target_product_id')
        
        if applicable_to == 'Category':
            if not category_id:
                raise serializers.ValidationError(
                    {'target_category_id': 'Category is required for category discounts'}
                )
            if product_id:
                raise serializers.ValidationError(
                    {'target_product_id': 'Product should not be set for category discounts'}
                )
        elif applicable_to == 'Product':
            if not product_id:
                raise serializers.ValidationError(
                    {'target_product_id': 'Product is required for product discounts'}
                )
            if category_id:
                raise serializers.ValidationError(
                    {'target_category_id': 'Category should not be set for product discounts'}
                )
        elif applicable_to == 'All':
            if category_id or product_id:
                raise serializers.ValidationError(
                    'No specific target should be set for discounts applicable to all products'
                )
        
        return data


class DiscountValidationSerializer(serializers.Serializer):
    """Serializer for validating if discount can be applied to a product"""
    
    discount_id = serializers.IntegerField()
    product_id = serializers.IntegerField()
    
    is_applicable = serializers.BooleanField(read_only=True)
    reason = serializers.CharField(read_only=True)
    discount_details = serializers.SerializerMethodField(read_only=True)
    
    def get_discount_details(self, obj):
        """Get discount details if applicable"""
        if obj.get('is_applicable'):
            discount = Discount.objects.get(id=obj['discount_id'])
            return {
                'discount_id': discount.discount_id,
                'name': discount.name,
                'type': discount.discount_type,
                'value': str(discount.value),
            }
        return None


class DiscountApplySerializer(serializers.Serializer):
    """Serializer for applying discount to an amount"""
    
    discount_id = serializers.IntegerField()
    original_amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    
    discount_amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    final_amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    discount_details = serializers.SerializerMethodField(read_only=True)
    
    def get_discount_details(self, obj):
        """Get discount details"""
        discount = Discount.objects.get(id=obj['discount_id'])
        return {
            'discount_id': discount.discount_id,
            'name': discount.name,
            'type': discount.discount_type,
            'value': str(discount.value),
        }
