from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from decimal import Decimal
from .category import Category


class Product(models.Model):
    """
    Product model for bakery items management.
    
    Features:
    - Auto-generated product_id (#PROD-1001, #PROD-1002, etc.)
    - Linked to Category (Buns, Bread, Cakes, Drinks, Pastries)
    - Pricing with dynamic profit_margin calculation
    - Current stock tracking
    - Shelf-life management (how long product can be stored)
    - Image URL for frontend display
    - Recipe LinkageVia RecipeItem
    
    Key Rules:
    - Only one #PROD sequence (global)
    - profit_margin = (selling_price - cost_price) / cost_price * 100
    - Unique constraint: name per category
    - Soft delete if recipes or batches exist
    - current_stock is updated by ProductBatch creation/deletion
    """
    
    SHELF_UNIT_CHOICES = [
        ('hours', 'Hours'),
        ('days', 'Days'),
        ('weeks', 'Weeks'),
    ]
    
    # Auto-generated fields
    product_id = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        db_index=True,
        help_text="Auto-generated: #PROD-1001, #PROD-1002, etc."
    )
    
    # Foreign keys
    category_id = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='products',
        limit_choices_to={'type': 'Product'},
        help_text="Must be a Product-type category"
    )
    
    # Basic info
    name = models.CharField(
        max_length=100,
        help_text="e.g., 'White Bread Loaf', 'Chocolate Cake'"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Product description for display"
    )
    image_url = models.URLField(
        blank=True,
        null=True,
        help_text="URL to product image"
    )
    
    # Pricing
    cost_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Cost to produce per unit"
    )
    selling_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Selling price per unit"
    )
    
    # Stock tracking
    current_stock = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Current quantity in stock (pieces/units)"
    )
    
    # Shelf-life
    shelf_life = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="How long product lasts after production"
    )
    shelf_unit = models.CharField(
        max_length=20,
        choices=SHELF_UNIT_CHOICES,
        default='days',
        help_text="Time unit for shelf_life"
    )
    
    # Metadata
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )
    
    # Unique constraint: name per category
    class Meta:
        unique_together = ['category_id', 'name']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product_id']),
            models.Index(fields=['category_id', 'name']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.product_id} - {self.name}"
    
    @property
    def profit_margin(self):
        """
        Calculate profit margin percentage.
        Formula: (selling_price - cost_price) / cost_price * 100
        """
        if self.cost_price == 0:
            return 0
        return ((self.selling_price - self.cost_price) / self.cost_price) * 100
    
    @property
    def is_low_stock(self):
        """Check if product is low on stock (less than 10 pieces)"""
        return self.current_stock < 10
    
    @property
    def is_out_of_stock(self):
        """Check if product is completely out of stock"""
        return self.current_stock <= 0
    
    @property
    def status(self):
        """Return stock status: available, low_stock, or out_of_stock"""
        if self.is_out_of_stock:
            return 'out_of_stock'
        elif self.is_low_stock:
            return 'low_stock'
        return 'available'
    
    def save(self, *args, **kwargs):
        """Auto-generate product_id if not already set"""
        if not self.product_id:
            # Find the highest product number
            last_product = Product.objects.all().order_by('id').last()
            if last_product:
                # Extract the number from existing product_id (e.g., '#PROD-1001' -> 1001)
                try:
                    last_num = int(last_product.product_id.split('-')[-1])
                    next_num = last_num + 1
                except:
                    next_num = 1001
            else:
                next_num = 1001
            
            self.product_id = f"#PROD-{next_num}"
        
        super().save(*args, **kwargs)
    
    def update_cost_price_from_recipe(self):
        """
        Calculate and update product cost_price from recipe items.
        
        Formula: total_cost = sum(ingredient_qty * ingredient_cost_per_unit)
        
        This is called automatically when recipe items are added/updated.
        """
        from .recipe import RecipeItem
        
        recipe_items = RecipeItem.objects.filter(product_id=self)
        
        if not recipe_items.exists():
            # No recipe defined, keep original cost_price
            return
        
        total_cost = Decimal('0')
        
        for item in recipe_items:
            # Get the total cost from the last batch of this ingredient
            # This represents the actual cost per unit
            batches = self.get_active_batches_for_ingredient(item.ingredient_id)
            
            if batches.exists():
                # Use cost from most recent batch
                cost_per_unit = batches.first().cost_price / batches.first().quantity
                item_cost = item.quantity_required * cost_per_unit
            else:
                # If no batch exists, estimate from ingredient's initial pricing
                # This is a fallback - ideally we track ingredient unit cost
                item_cost = Decimal('0')
            
            total_cost += item_cost
        
        # Update product cost_price only if recipe provides a valid cost
        if total_cost > 0:
            self.cost_price = total_cost
            self.save(update_fields=['cost_price', 'updated_at'])
    
    def get_active_batches_for_ingredient(self, ingredient):
        """Get active batches for an ingredient for cost calculation"""
        from .batch import IngredientBatch
        return IngredientBatch.objects.filter(
            ingredient_id=ingredient,
            status='Active'
        ).order_by('-created_at')


class ProductStockHistory(models.Model):
    """
    Audit trail for product stock changes.
    
    Tracks all stock modifications including:
    - Sales (UseStock)
    - Returns (ReturnStock)
    - Adjustments (StockAdjustment)
    - Waste (WasteStock)
    
    Features:
    - Links to Product and User (cashier/storekeeper who made the change)
    - Records before/after quantities
    - Optional reference to Sale or other transactions
    - Timestamp for audit trail
    """
    
    TRANSACTION_TYPES = [
        ('AddStock', 'Add Stock (Production/Batch)'),
        ('UseStock', 'Use Stock (Sale)'),
        ('ReturnStock', 'Return Stock (Product Return)'),
        ('WasteStock', 'Waste Stock (Spoilage/Damage)'),
        ('StockAdjustment', 'Stock Adjustment (Inventory Correction)'),
    ]
    
    product_id = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='stock_history',
        db_index=True
    )
    
    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPES,
        db_index=True,
        help_text="Type of stock change"
    )
    
    qty_before = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Stock quantity before transaction"
    )
    
    qty_after = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Stock quantity after transaction"
    )
    
    change_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Change in quantity (positive for additions, negative for removals)"
    )
    
    # Reference fields for traceability
    user_id = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stock_history',
        help_text="User who made the change (cashier, storekeeper, etc.)"
    )
    
    # Optional reference to sales transaction
    sale_bill_number = models.CharField(
        max_length=50,
        null=True,
        blank=True,
        db_index=True,
        help_text="Bill number if this is from a sale"
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional details about the transaction"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['product_id', '-created_at']),
            models.Index(fields=['transaction_type', '-created_at']),
            models.Index(fields=['sale_bill_number']),
        ]
        verbose_name = 'Product Stock History'
        verbose_name_plural = 'Product Stock Histories'
    
    def __str__(self):
        return f"{self.product_id.name} - {self.transaction_type} ({self.change_amount}) at {self.created_at}"
