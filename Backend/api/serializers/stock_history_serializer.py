from rest_framework import serializers
from api.models import ProductStockHistory, IngredientStockHistory, Product, Ingredient, User


class ProductStockHistoryListSerializer(serializers.ModelSerializer):
    """
    List serializer for product stock history.
    
    Includes nested product and user information for context
    in the history list view.
    """
    
    product_name = serializers.CharField(
        source='product_id.name',
        read_only=True
    )
    product_id_value = serializers.CharField(
        source='product_id.product_id',
        read_only=True
    )
    
    performed_by_name = serializers.CharField(
        source='user_id.full_name',
        read_only=True,
        allow_null=True
    )
    
    class Meta:
        model = ProductStockHistory
        fields = [
            'id',
            'product_id',
            'product_name',
            'product_id_value',
            'transaction_type',
            'qty_before',
            'qty_after',
            'change_amount',
            'sale_bill_number',
            'notes',
            'performed_by_name',
            'user_id',
            'created_at'
        ]
        read_only_fields = fields


class ProductStockHistoryDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for product stock history.
    
    Includes comprehensive information for viewing individual
    history entries with full product and user details.
    """
    
    product_name = serializers.CharField(
        source='product_id.name',
        read_only=True
    )
    product_id_value = serializers.CharField(
        source='product_id.product_id',
        read_only=True
    )
    category_name = serializers.CharField(
        source='product_id.category_id.name',
        read_only=True
    )
    
    performed_by_name = serializers.CharField(
        source='user_id.full_name',
        read_only=True,
        allow_null=True
    )
    performed_by_role = serializers.CharField(
        source='user_id.role',
        read_only=True,
        allow_null=True
    )
    
    class Meta:
        model = ProductStockHistory
        fields = [
            'id',
            'product_id',
            'product_name',
            'product_id_value',
            'category_name',
            'transaction_type',
            'qty_before',
            'qty_after',
            'change_amount',
            'sale_bill_number',
            'notes',
            'user_id',
            'performed_by_name',
            'performed_by_role',
            'created_at'
        ]
        read_only_fields = fields


class IngredientStockHistoryListSerializer(serializers.ModelSerializer):
    """
    List serializer for ingredient stock history.
    
    Includes nested ingredient and user information for context
    in the history list view.
    """
    
    ingredient_name = serializers.CharField(
        source='ingredient_id.name',
        read_only=True
    )
    ingredient_id_value = serializers.CharField(
        source='ingredient_id.ingredient_id',
        read_only=True
    )
    
    batch_id_value = serializers.CharField(
        source='batch_id.batch_id',
        read_only=True,
        allow_null=True
    )
    
    performed_by_name = serializers.CharField(
        source='performed_by.full_name',
        read_only=True,
        allow_null=True
    )
    
    class Meta:
        model = IngredientStockHistory
        fields = [
            'id',
            'ingredient_id',
            'ingredient_name',
            'ingredient_id_value',
            'batch_id',
            'batch_id_value',
            'transaction_type',
            'qty_before',
            'qty_after',
            'change_amount',
            'reference_id',
            'notes',
            'performed_by',
            'performed_by_name',
            'created_at'
        ]
        read_only_fields = fields


class IngredientStockHistoryDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for ingredient stock history.
    
    Includes comprehensive information for viewing individual
    history entries with full ingredient and user details.
    """
    
    ingredient_name = serializers.CharField(
        source='ingredient_id.name',
        read_only=True
    )
    ingredient_id_value = serializers.CharField(
        source='ingredient_id.ingredient_id',
        read_only=True
    )
    ingredient_category = serializers.CharField(
        source='ingredient_id.category_id.name',
        read_only=True
    )
    
    batch_id_value = serializers.CharField(
        source='batch_id.batch_id',
        read_only=True,
        allow_null=True
    )
    batch_supplier = serializers.CharField(
        source='batch_id.supplier',
        read_only=True,
        allow_null=True
    )
    
    performed_by_name = serializers.CharField(
        source='performed_by.full_name',
        read_only=True,
        allow_null=True
    )
    performed_by_role = serializers.CharField(
        source='performed_by.role',
        read_only=True,
        allow_null=True
    )
    
    class Meta:
        model = IngredientStockHistory
        fields = [
            'id',
            'ingredient_id',
            'ingredient_name',
            'ingredient_id_value',
            'ingredient_category',
            'batch_id',
            'batch_id_value',
            'batch_supplier',
            'transaction_type',
            'qty_before',
            'qty_after',
            'change_amount',
            'reference_id',
            'notes',
            'performed_by',
            'performed_by_name',
            'performed_by_role',
            'created_at'
        ]
        read_only_fields = fields
