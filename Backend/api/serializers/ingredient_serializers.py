from rest_framework import serializers
from api.models import Ingredient, Category
from decimal import Decimal


TRACKING_BASE_UNIT_MAP = {
    'Weight': 'g',
    'Volume': 'ml',
    'Count': 'nos',
}

TRACKING_THRESHOLD_UNITS = {
    'Weight': {'g', 'kg'},
    'Volume': {'ml', 'L'},
    'Count': {'nos'},
}

UNIT_TO_BASE_FACTOR = {
    'g': Decimal('1'),
    'kg': Decimal('1000'),
    'ml': Decimal('1'),
    'L': Decimal('1000'),
    'nos': Decimal('1'),
}


def get_base_unit_for_tracking(tracking_type):
    return TRACKING_BASE_UNIT_MAP.get(tracking_type, 'g')


def get_default_threshold_unit_for_tracking(tracking_type):
    return get_base_unit_for_tracking(tracking_type)


def convert_threshold_to_base(raw_value, threshold_unit):
    return raw_value * UNIT_TO_BASE_FACTOR.get(threshold_unit, Decimal('1'))


def convert_threshold_from_base(base_value, threshold_unit):
    factor = UNIT_TO_BASE_FACTOR.get(threshold_unit, Decimal('1'))
    if factor == 0:
        return base_value
    return base_value / factor


class IngredientListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for ingredient list views.
    
    Includes: id, ingredient_id, name, category info, quantity status
    """
    category_name = serializers.CharField(source='category_id.name', read_only=True)
    stock_status = serializers.CharField(read_only=True)
    threshold_unit = serializers.SerializerMethodField()
    low_stock_threshold_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Ingredient
        fields = [
            'id',
            'ingredient_id',
            'name',
            'category_id',
            'category_name',
            'tracking_type',
            'base_unit',
            'total_quantity',
            'low_stock_threshold',
            'threshold_unit',
            'low_stock_threshold_display',
            'stock_status',
            'is_active',
            'created_at',
        ]
        read_only_fields = [
            'id',
            'ingredient_id',
            'total_quantity',
            'stock_status',
            'created_at',
        ]

    def get_threshold_unit(self, obj):
        return obj.effective_threshold_unit

    def get_low_stock_threshold_display(self, obj):
        threshold_unit = obj.effective_threshold_unit
        return convert_threshold_from_base(obj.low_stock_threshold, threshold_unit)


class IngredientDetailSerializer(serializers.ModelSerializer):
    """
    Complete serializer for ingredient detail view.
    
    Includes: All fields + batch count, recipe count, supplier info
    """
    category_name = serializers.CharField(source='category_id.name', read_only=True)
    stock_status = serializers.CharField(read_only=True)
    batch_count = serializers.SerializerMethodField()
    is_low_stock = serializers.SerializerMethodField()
    is_out_of_stock = serializers.SerializerMethodField()
    shelf_life_display = serializers.SerializerMethodField()
    threshold_unit = serializers.SerializerMethodField()
    low_stock_threshold_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Ingredient
        fields = [
            'id',
            'ingredient_id',
            'name',
            'category_id',
            'category_name',
            'supplier',
            'supplier_contact',
            'tracking_type',
            'base_unit',
            'total_quantity',
            'low_stock_threshold',
            'threshold_unit',
            'low_stock_threshold_display',
            'shelf_life',
            'shelf_unit',
            'shelf_life_display',
            'stock_status',
            'is_low_stock',
            'is_out_of_stock',
            'batch_count',
            'is_active',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'ingredient_id',
            'total_quantity',
            'stock_status',
            'is_low_stock',
            'is_out_of_stock',
            'batch_count',
            'shelf_life_display',
            'threshold_unit',
            'low_stock_threshold_display',
            'created_at',
            'updated_at',
        ]
    
    def get_batch_count(self, obj):
        """Get count of active batches for this ingredient"""
        # Will be implemented after IngredientBatch model is created
        return 0
    
    def get_is_low_stock(self, obj):
        """Get low stock status"""
        return obj.is_low_stock()
    
    def get_is_out_of_stock(self, obj):
        """Get out of stock status"""
        return obj.is_out_of_stock()
    
    def get_shelf_life_display(self, obj):
        """Get formatted shelf life display"""
        return f"{obj.shelf_life} {obj.get_shelf_unit_display().lower()}"

    def get_threshold_unit(self, obj):
        return obj.effective_threshold_unit

    def get_low_stock_threshold_display(self, obj):
        threshold_unit = obj.effective_threshold_unit
        return convert_threshold_from_base(obj.low_stock_threshold, threshold_unit)


class IngredientCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new ingredients.
    
    Includes comprehensive validation.
    """
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.filter(type='Ingredient'))
    threshold_unit = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = Ingredient
        fields = [
            'name',
            'category_id',
            'supplier',
            'supplier_contact',
            'tracking_type',
            'base_unit',
            'low_stock_threshold',
            'threshold_unit',
            'shelf_life',
            'shelf_unit',
        ]
    
    def validate_category_id(self, value):
        """Ensure category is Ingredient type"""
        if value.type != 'Ingredient':
            raise serializers.ValidationError(
                f"Category '{value.name}' is a {value.type} category. "
                "Please select an Ingredient-type category."
            )
        return value
    
    def validate_name(self, value):
        """Validate ingredient name"""
        if not value or not value.strip():
            raise serializers.ValidationError("Name cannot be empty.")
        if len(value) < 2:
            raise serializers.ValidationError("Name must be at least 2 characters.")
        if len(value) > 100:
            raise serializers.ValidationError("Name must be at most 100 characters.")
        return value.strip()
    
    def validate_base_unit(self, value):
        """Validate base unit"""
        if not value or not value.strip():
            raise serializers.ValidationError("Base unit cannot be empty.")
        if len(value) > 20:
            raise serializers.ValidationError("Base unit must be at most 20 characters.")
        return value.strip()
    
    def validate_low_stock_threshold(self, value):
        """Validate low stock threshold"""
        if value < 0:
            raise serializers.ValidationError("Low stock threshold cannot be negative.")
        return value
    
    def validate_shelf_life(self, value):
        """Validate shelf life"""
        if value <= 0:
            raise serializers.ValidationError("Shelf life must be greater than 0.")
        return value
    
    def validate(self, data):
        """Validate combined fields"""
        # Check for duplicate name in same category
        category = data.get('category_id')
        name = data.get('name')
        
        if category and name:
            existing = Ingredient.objects.filter(
                category_id=category,
                name__iexact=name
            ).exists()
            
            if existing:
                raise serializers.ValidationError(
                    f"An ingredient named '{name}' already exists in category '{category.name}'."
                )

        tracking_type = data.get('tracking_type', 'Weight')
        data['base_unit'] = get_base_unit_for_tracking(tracking_type)

        threshold_unit = data.get('threshold_unit') or get_default_threshold_unit_for_tracking(tracking_type)
        allowed_units = TRACKING_THRESHOLD_UNITS.get(tracking_type, {'g'})

        if threshold_unit not in allowed_units:
            raise serializers.ValidationError({
                'threshold_unit': f"Invalid threshold unit '{threshold_unit}' for tracking type '{tracking_type}'."
            })

        data['threshold_unit'] = threshold_unit
        
        return data
    
    def create(self, validated_data):
        """Create ingredient instance with threshold stored in base units."""
        tracking_type = validated_data.get('tracking_type', 'Weight')
        threshold_unit = validated_data.get('threshold_unit') or get_default_threshold_unit_for_tracking(tracking_type)

        raw_threshold = validated_data.get('low_stock_threshold')
        if raw_threshold is not None:
            validated_data['low_stock_threshold'] = convert_threshold_to_base(raw_threshold, threshold_unit)

        return Ingredient.objects.create(**validated_data)


class IngredientUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating existing ingredients.
    
    Allows updating core ingredient details: name, category, tracking type, quantity,
    and supplier information.
    """
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.filter(type='Ingredient'))
    threshold_unit = serializers.CharField(required=False, allow_blank=True)
    
    class Meta:
        model = Ingredient
        fields = [
            'name',
            'category_id',
            'tracking_type',
            'total_quantity',
            'supplier',
            'supplier_contact',
            'base_unit',
            'low_stock_threshold',
            'threshold_unit',
            'shelf_life',
            'shelf_unit',
            'is_active',
        ]
    
    def validate_name(self, value):
        """Validate ingredient name"""
        if not value or not value.strip():
            raise serializers.ValidationError("Name cannot be empty.")
        if len(value) < 2:
            raise serializers.ValidationError("Name must be at least 2 characters.")
        if len(value) > 100:
            raise serializers.ValidationError("Name must be at most 100 characters.")
        return value.strip()
    
    def validate_category_id(self, value):
        """Ensure category is Ingredient type"""
        if value.type != 'Ingredient':
            raise serializers.ValidationError(
                f"Category '{value.name}' is a {value.type} category. "
                "Please select an Ingredient-type category."
            )
        return value
    
    def validate_base_unit(self, value):
        """Validate base unit"""
        if not value or not value.strip():
            raise serializers.ValidationError("Base unit cannot be empty.")
        return value.strip()
    
    def validate_total_quantity(self, value):
        """Validate total quantity"""
        if value < 0:
            raise serializers.ValidationError("Total quantity cannot be negative.")
        return value
    
    def validate_low_stock_threshold(self, value):
        """Validate low stock threshold"""
        if value < 0:
            raise serializers.ValidationError("Low stock threshold cannot be negative.")
        return value
    
    def validate_shelf_life(self, value):
        """Validate shelf life"""
        if value <= 0:
            raise serializers.ValidationError("Shelf life must be greater than 0.")
        return value
    
    def validate(self, data):
        """Validate combined fields"""
        # Check for duplicate name in same category (only if name or category is being updated)
        if 'name' in data or 'category_id' in data:
            instance = self.instance
            name = data.get('name', instance.name)
            category = data.get('category_id', instance.category_id)
            
            # Check for duplicate but exclude current instance
            existing = Ingredient.objects.filter(
                category_id=category,
                name__iexact=name
            ).exclude(id=instance.id).exists()
            
            if existing:
                raise serializers.ValidationError(
                    f"An ingredient named '{name}' already exists in category '{category.name}'."
                )

        instance = self.instance
        tracking_type = data.get('tracking_type', instance.tracking_type)
        data['base_unit'] = get_base_unit_for_tracking(tracking_type)

        if 'threshold_unit' in data:
            threshold_unit = data.get('threshold_unit') or get_default_threshold_unit_for_tracking(tracking_type)
        else:
            threshold_unit = instance.threshold_unit or get_default_threshold_unit_for_tracking(tracking_type)

        allowed_units = TRACKING_THRESHOLD_UNITS.get(tracking_type, {'g'})
        if threshold_unit not in allowed_units:
            raise serializers.ValidationError({
                'threshold_unit': f"Invalid threshold unit '{threshold_unit}' for tracking type '{tracking_type}'."
            })

        data['threshold_unit'] = threshold_unit
        
        return data

    def update(self, instance, validated_data):
        """
        Persist threshold in base units.

        Backward compatibility:
        - If client sends low_stock_threshold without threshold_unit, treat value as already in base unit.
        - If client sends both low_stock_threshold and threshold_unit, convert to base unit before save.
        """
        threshold_unit_was_sent = 'threshold_unit' in self.initial_data
        threshold_value_was_sent = 'low_stock_threshold' in validated_data

        if threshold_value_was_sent and threshold_unit_was_sent:
            tracking_type = validated_data.get('tracking_type', instance.tracking_type)
            threshold_unit = validated_data.get('threshold_unit') or get_default_threshold_unit_for_tracking(tracking_type)
            validated_data['low_stock_threshold'] = convert_threshold_to_base(
                validated_data['low_stock_threshold'],
                threshold_unit,
            )

        return super().update(instance, validated_data)


class IngredientMinimalSerializer(serializers.ModelSerializer):
    """
    Minimal serializer for embedding in other responses.
    
    Useful when showing ingredient info in batches, recipes, etc.
    """
    
    class Meta:
        model = Ingredient
        fields = [
            'id',
            'ingredient_id',
            'name',
            'base_unit',
            'total_quantity',
            'stock_status',
        ]
        read_only_fields = fields
