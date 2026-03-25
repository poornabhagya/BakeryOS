from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class IngredientStockHistory(models.Model):
    """
    Track all ingredient stock transactions for audit trail.
    
    Automatically created by signals when:
    - IngredientBatch created (AddStock)
    - IngredientBatch usage (UseStock)
    - IngredientWastage created (Wastage)
    - Manual adjustments (Adjustment)
    """
    
    TRANSACTION_TYPES = [
        ('AddStock', 'Add Stock'),
        ('UseStock', 'Use Stock'),
        ('Wastage', 'Wastage'),
        ('Adjustment', 'Adjustment'),
    ]
    
    id = models.AutoField(primary_key=True)
    
    # References
    ingredient_id = models.ForeignKey(
        'Ingredient',
        on_delete=models.CASCADE,
        related_name='stock_history',
        help_text="Ingredient whose stock changed"
    )
    
    batch_id = models.ForeignKey(
        'IngredientBatch',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='stock_history',
        help_text="Specific batch involved (if applicable)"
    )
    
    performed_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='ingredient_stock_changes',
        help_text="User who performed the transaction"
    )
    
    # Transaction details
    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPES,
        help_text="Type of transaction"
    )
    
    # Stock tracking
    qty_before = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Quantity before transaction"
    )
    
    qty_after = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Quantity after transaction"
    )
    
    change_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Change in quantity (positive or negative)"
    )
    
    # Additional info
    reference_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="ID of related transaction (IngredientBatch, IngredientWastage, etc.)"
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional details about the transaction"
    )
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'api_ingredient_stock_history'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['ingredient_id']),
            models.Index(fields=['batch_id']),
            models.Index(fields=['transaction_type']),
            models.Index(fields=['-created_at']),
            models.Index(fields=['ingredient_id', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.ingredient_id} - {self.transaction_type} ({self.change_amount})"
