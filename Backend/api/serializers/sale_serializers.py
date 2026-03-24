from rest_framework import serializers
from api.models import Sale, SaleItem, Product, Discount


class SaleItemSerializer(serializers.ModelSerializer):
    """Serializer for SaleItem"""
    
    product_name = serializers.CharField(source='product_id.name', read_only=True)
    product_id_val = serializers.IntegerField(source='product_id.id', read_only=True)
    
    class Meta:
        model = SaleItem
        fields = [
            'id',
            'product_id',
            'product_id_val',
            'product_name',
            'quantity',
            'unit_price',
            'subtotal',
            'created_at'
        ]
        read_only_fields = ['id', 'subtotal', 'created_at']


class SaleListSerializer(serializers.ModelSerializer):
    """Serializer for listing sales"""
    
    cashier_name = serializers.CharField(source='cashier_id.full_name', read_only=True)
    discount_name = serializers.CharField(source='discount_id.name', read_only=True, allow_null=True)
    item_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Sale
        fields = [
            'id',
            'bill_number',
            'cashier_id',
            'cashier_name',
            'subtotal',
            'discount_id',
            'discount_name',
            'discount_amount',
            'total_amount',
            'payment_method',
            'item_count',
            'date_time',
            'created_at'
        ]
        read_only_fields = fields
    
    def get_item_count(self, obj):
        """Get count of items in sale"""
        return obj.items.count()


class SaleDetailSerializer(serializers.ModelSerializer):
    """Serializer for sale details with items"""
    
    cashier_name = serializers.CharField(source='cashier_id.full_name', read_only=True)
    discount_name = serializers.CharField(source='discount_id.name', read_only=True, allow_null=True)
    discount_type = serializers.CharField(source='discount_id.discount_type', read_only=True, allow_null=True)
    discount_value = serializers.DecimalField(
        source='discount_id.value',
        max_digits=10,
        decimal_places=2,
        read_only=True,
        allow_null=True
    )
    item_count = serializers.SerializerMethodField()
    items = SaleItemSerializer(many=True, read_only=True)
    
    class Meta:
        model = Sale
        fields = [
            'id',
            'bill_number',
            'cashier_id',
            'cashier_name',
            'subtotal',
            'discount_id',
            'discount_name',
            'discount_type',
            'discount_value',
            'discount_amount',
            'total_amount',
            'payment_method',
            'notes',
            'item_count',
            'items',
            'date_time',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'bill_number',
            'cashier_id',
            'cashier_name',
            'subtotal',
            'discount_amount',
            'total_amount',
            'item_count',
            'created_at',
            'updated_at'
        ]
    
    def get_item_count(self, obj):
        """Get count of items in sale"""
        return obj.items.count()


class SaleItemCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating sale items"""
    
    class Meta:
        model = SaleItem
        fields = [
            'product_id',
            'quantity',
            'unit_price'
        ]
    
    def validate_quantity(self, value):
        """Validate quantity is positive"""
        if value <= 0:
            raise serializers.ValidationError("Quantity must be greater than 0")
        return value
    
    def validate_unit_price(self, value):
        """Validate unit price is positive"""
        if value <= 0:
            raise serializers.ValidationError("Unit price must be greater than 0")
        return value
    
    def validate_product_id(self, value):
        """Validate product exists and has stock"""
        if not value:
            raise serializers.ValidationError("Product is required")
        
        if not Product.objects.filter(id=value.id).exists():
            raise serializers.ValidationError("Product not found")
        
        return value


class SaleCreateSerializer(serializers.Serializer):
    """Serializer for creating a new sale with items"""
    
    cashier_id = serializers.IntegerField(required=False)  # Will use current user
    discount_id = serializers.IntegerField(allow_null=True, required=False)
    items = SaleItemCreateSerializer(many=True)
    payment_method = serializers.ChoiceField(choices=Sale.PAYMENT_METHOD_CHOICES)
    notes = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        fields = [
            'cashier_id',
            'discount_id',
            'items',
            'payment_method',
            'notes'
        ]
    
    def validate_items(self, value):
        """Validate items list"""
        if not value:
            raise serializers.ValidationError("Sale must have at least one item")
        
        if len(value) > 100:
            raise serializers.ValidationError("Sale cannot have more than 100 items")
        
        return value
    
    def validate_discount_id(self, value):
        """Validate discount exists and is active if provided"""
        if value:
            try:
                discount = Discount.objects.get(id=value)
                if not discount.is_active:
                    raise serializers.ValidationError("Selected discount is not active")
            except Discount.DoesNotExist:
                raise serializers.ValidationError("Discount not found")
        
        return value
    
    def create(self, validated_data):
        """Create sale with items and handle stock deduction"""
        from api.models import Sale, SaleItem
        
        # Get cashier from request or validated data
        request = self.context.get('request')
        if not validated_data.get('cashier_id'):
            validated_data['cashier_id'] = request.user
        else:
            from api.models import User
            cashier = User.objects.get(id=validated_data['cashier_id'])
            validated_data['cashier_id'] = cashier
        
        items_data = validated_data.pop('items')
        
        # Calculate subtotal
        subtotal = sum(
            item['quantity'] * item['unit_price']
            for item in items_data
        )
        
        # Handle discount
        discount_id = validated_data.get('discount_id')
        discount_obj = None
        discount_amount = 0
        
        if discount_id:
            discount_obj = Discount.objects.get(id=discount_id)
            discount_amount = discount_obj.calculate_discount_amount(subtotal)
        
        # Create sale
        sale = Sale.objects.create(
            cashier_id=validated_data['cashier_id'],
            subtotal=subtotal,
            discount_id=discount_obj,
            discount_amount=discount_amount,
            payment_method=validated_data['payment_method'],
            notes=validated_data.get('notes', ''),
        )
        
        sale.total_amount = subtotal - discount_amount
        sale.save()
        
        # Create sale items and deduct stock
        for item_data in items_data:
            product = item_data['product_id']
            quantity = item_data['quantity']
            unit_price = item_data['unit_price']
            
            # Create sale item
            SaleItem.objects.create(
                sale_id=sale,
                product_id=product,
                quantity=quantity,
                unit_price=unit_price,
                subtotal=quantity * unit_price
            )
            
            # Deduct from product stock
            product.current_stock -= quantity
            product.save()
            
            # Create stock history entry
            from api.models import ProductStockHistory
            ProductStockHistory.objects.create(
                product_id=product,
                transaction_type='UseStock',
                qty_before=product.current_stock + quantity,
                qty_after=product.current_stock,
                change_amount=-quantity,
                user_id=validated_data['cashier_id'],
                sale_bill_number=sale.bill_number,
                notes=f'Sale {sale.bill_number}'
            )
        
        return sale


class SaleAnalyticsSerializer(serializers.Serializer):
    """Serializer for sales analytics data"""
    
    date = serializers.DateField()
    total_sales = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    average_sale = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_discount = serializers.DecimalField(max_digits=12, decimal_places=2)


class CashierSalesSerializer(serializers.Serializer):
    """Serializer for cashier sales summary"""
    
    cashier_id = serializers.IntegerField()
    cashier_name = serializers.CharField()
    total_sales = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    average_sale = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_discount = serializers.DecimalField(max_digits=12, decimal_places=2)


class PaymentMethodSalesSerializer(serializers.Serializer):
    """Serializer for payment method breakdown"""
    
    payment_method = serializers.CharField()
    count = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=12, decimal_places=2)
