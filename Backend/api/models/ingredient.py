from django.db import models
from django.utils import timezone
from .category import Category


class Ingredient(models.Model):
    """
    Ingredient model for inventory management.
    
    Features:
    - Auto-generated ingredient_id (#I001, #I002, etc.)
    - Linked to Category (Flour, Sugar, Dairy, etc.)
    - Supplier tracking
    - Quantity tracking with low-stock threshold
    - Shelf-life management
    - total_quantity synced via signals from IngredientBatch
    
    Key Rules:
    - Only one #I sequence (not separate for each category)
    - total_quantity is READ-ONLY (calculated from batches)
    - Unique constraint: name per category
    - Soft delete if batches exist
    """
    
    TRACKING_TYPE_CHOICES = [
        ('Weight', 'Weight (kg, g)'),
        ('Volume', 'Volume (liters, ml)'),
        ('Count', 'Count (pieces, units)'),
    ]
    
    SHELF_UNIT_CHOICES = [
        ('days', 'Days'),
        ('weeks', 'Weeks'),
        ('months', 'Months'),
        ('years', 'Years'),
    ]
    
    # Auto-generated fields
    ingredient_id = models.CharField(
        max_length=50, 
        unique=True, 
        editable=False,
        db_index=True,
        help_text="Auto-generated: #I001, #I002, etc."
    )
    
    # Foreign keys
    category_id = models.ForeignKey(
        Category,
        on_delete=models.PROTECT,
        related_name='ingredients',
        limit_choices_to={'type': 'Ingredient'},
        help_text="Must be an Ingredient-type category"
    )
    
    # Basic info
    name = models.CharField(
        max_length=100,
        help_text="e.g., 'All Purpose Flour', 'Granulated Sugar'"
    )
    supplier = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Supplier company name"
    )
    supplier_contact = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Supplier phone/email"
    )
    
    # Quantity tracking
    tracking_type = models.CharField(
        max_length=20,
        choices=TRACKING_TYPE_CHOICES,
        default='Weight',
        help_text="How this ingredient is tracked (by weight, volume, or count)"
    )
    
    base_unit = models.CharField(
        max_length=20,
        help_text="e.g., 'kg', 'liters', 'pieces'"
    )
    
    total_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Total quantity from active batches (updated via signals, READ-ONLY)"
    )
    
    low_stock_threshold = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=10,
        help_text="Alert threshold for low stock"
    )
    
    # Shelf life
    shelf_life = models.IntegerField(
        default=30,
        help_text="Number of days/weeks/months before expiry"
    )
    
    shelf_unit = models.CharField(
        max_length=10,
        choices=SHELF_UNIT_CHOICES,
        default='days',
        help_text="Unit for shelf life (days, weeks, months)"
    )
    
    # Audit fields
    is_active = models.BooleanField(
        default=True,
        help_text="Soft delete support - set to False instead of deleting"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['category_id', 'name']
        unique_together = [['category_id', 'name']]
        indexes = [
            models.Index(fields=['ingredient_id']),
            models.Index(fields=['category_id']),
            models.Index(fields=['name']),
            models.Index(fields=['category_id', 'name']),
            models.Index(fields=['is_active', 'total_quantity']),
        ]
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'
    
    def __str__(self):
        return f"{self.ingredient_id} - {self.name}"
    
    def get_shelf_life_in_days(self):
        """Convert shelf_life to days based on shelf_unit"""
        multipliers = {
            'days': 1,
            'weeks': 7,
            'months': 30,
            'years': 365,
        }
        return self.shelf_life * multipliers.get(self.shelf_unit, 1)
    
    def is_low_stock(self):
        """Check if ingredient is below threshold"""
        return self.total_quantity < self.low_stock_threshold
    
    def is_out_of_stock(self):
        """Check if ingredient is out of stock"""
        return self.total_quantity <= 0
    
    @property
    def stock_status(self):
        """Get human-readable stock status"""
        if self.total_quantity == 0:
            return 'OUT_OF_STOCK'
        elif self.is_low_stock():
            return 'LOW_STOCK'
        else:
            return 'IN_STOCK'


# Signal handler for auto-ID generation
from django.db.models.signals import pre_save
from django.dispatch import receiver


@receiver(pre_save, sender=Ingredient)
def auto_generate_ingredient_id(sender, instance, **kwargs):
    """Auto-generate ingredient_id if not set"""
    if not instance.ingredient_id:
        # Get the next sequence number
        last_ingredient = Ingredient.objects.all().order_by('-id').first()
        next_number = (last_ingredient.id if last_ingredient else 0) + 1
        instance.ingredient_id = f"#I{next_number:03d}"
