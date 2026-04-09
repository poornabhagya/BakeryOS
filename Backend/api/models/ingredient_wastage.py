from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal


class IngredientWastage(models.Model):
    """
    Model to track ingredient wastage events.
    
    Automatically generates wastage_id (IW-001, IW-002, etc.)
    Tracks which ingredient was wasted, which batch (if applicable), why, by whom, and the financial impact.
    """
    
    wastage_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        help_text="Auto-generated ID: IW-001, IW-002, etc."
    )
    
    ingredient_id = models.ForeignKey(
        'Ingredient',
        on_delete=models.CASCADE,
        related_name='wastage_records',
        help_text="The ingredient that was wasted"
    )
    
    batch_id = models.ForeignKey(
        'IngredientBatch',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='wastage_records',
        help_text="The batch from which wastage occurred (optional)"
    )
    
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Quantity of ingredient wasted"
    )
    
    unit_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Cost per unit at time of wastage"
    )
    
    total_loss = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        editable=False,
        help_text="Calculated as quantity * unit_cost"
    )
    
    reason_id = models.ForeignKey(
        'WastageReason',
        on_delete=models.PROTECT,
        related_name='ingredient_wastages',
        help_text="Reason for wastage"
    )
    
    reported_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='reported_ingredient_wastages',
        help_text="User who reported the wastage"
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes about the wastage"
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when wastage was recorded"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp of last update"
    )
    
    class Meta:
        db_table = 'api_ingredient_wastage'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['wastage_id']),
            models.Index(fields=['ingredient_id']),
            models.Index(fields=['batch_id']),
            models.Index(fields=['reason_id']),
            models.Index(fields=['reported_by']),
            models.Index(fields=['-created_at']),
        ]
        verbose_name = 'Ingredient Wastage'
        verbose_name_plural = 'Ingredient Wastages'
    
    def save(self, *args, **kwargs):
        """
        Auto-generate wastage_id and calculate total_loss before saving.
        """
        # Generate wastage_id if not exists
        if not self.wastage_id:
            # Get the highest number from existing records
            latest_wastage = IngredientWastage.objects.all().order_by('-id').first()
            if latest_wastage and latest_wastage.wastage_id:
                try:
                    # Extract number from IW-### format
                    number = int(latest_wastage.wastage_id.split('-')[1])
                    new_number = number + 1
                except (ValueError, IndexError):
                    new_number = 1
            else:
                new_number = 1
            
            self.wastage_id = f"IW-{new_number:03d}"
        
        # Calculate total_loss
        self.total_loss = (self.quantity or Decimal('0')) * (self.unit_cost or Decimal('0'))
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        batch_info = f" (Batch: {self.batch_id.batch_id})" if self.batch_id else ""
        return f"{self.wastage_id} - {self.ingredient_id.name if hasattr(self.ingredient_id, 'name') else 'Unknown'} ({self.quantity}){batch_info}"
    
    @property
    def ingredient_name(self):
        """Get ingredient name for serialization."""
        try:
            return self.ingredient_id.name
        except:
            return "Unknown Ingredient"
    
    @property
    def reason_text(self):
        """Get reason text for serialization."""
        try:
            return self.reason_id.reason
        except:
            return "Unknown Reason"
    
    @property
    def reported_by_name(self):
        """Get reporter name for serialization."""
        try:
            if self.reported_by:
                return self.reported_by.get_full_name() or self.reported_by.username
            return "System"
        except:
            return "Unknown User"
