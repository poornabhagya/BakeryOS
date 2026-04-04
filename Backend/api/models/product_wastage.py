from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, DecimalValidator
from decimal import Decimal


class ProductWastage(models.Model):
    """
    Model to track product wastage events.
    
    Automatically generates wastage_id (PW-001, PW-002, etc.)
    Tracks which product was wasted, why, by whom, and the financial impact.
    """
    
    wastage_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False,
        help_text="Auto-generated ID: PW-001, PW-002, etc."
    )
    
    product_id = models.ForeignKey(
        'Product',
        on_delete=models.CASCADE,
        related_name='wastage_records',
        help_text="The product that was wasted"
    )
    
    batch = models.ForeignKey(
        'ProductBatch',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='wastage_records',
        help_text="The product batch this wastage came from (optional)"
    )
    
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Quantity of product wasted"
    )
    
    unit_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0'))],
        help_text="Cost per unit at time of wastage"
    )
    
    total_loss = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        editable=False,
        help_text="Calculated as quantity * unit_cost"
    )
    
    reason_id = models.ForeignKey(
        'WastageReason',
        on_delete=models.PROTECT,
        related_name='product_wastages',
        help_text="Reason for wastage"
    )
    
    reported_by = models.ForeignKey(
        'User',
        on_delete=models.SET_NULL,
        null=True,
        related_name='reported_wastages',
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
        db_table = 'api_product_wastage'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['wastage_id']),
            models.Index(fields=['product_id']),
            models.Index(fields=['reason_id']),
            models.Index(fields=['reported_by']),
            models.Index(fields=['-created_at']),
        ]
        verbose_name = 'Product Wastage'
        verbose_name_plural = 'Product Wastages'
    
    def save(self, *args, **kwargs):
        """
        Auto-generate wastage_id and calculate total_loss before saving.
        Deduct quantity from the batch's current_qty if batch is linked.
        """
        # Generate wastage_id if not exists
        if not self.wastage_id:
            # Get the highest number from existing records
            latest_wastage = ProductWastage.objects.all().order_by('-id').first()
            if latest_wastage and latest_wastage.wastage_id:
                try:
                    # Extract number from PW-### format
                    number = int(latest_wastage.wastage_id.split('-')[1])
                    new_number = number + 1
                except (ValueError, IndexError):
                    new_number = 1
            else:
                new_number = 1
            
            self.wastage_id = f"PW-{new_number:03d}"
        
        # Calculate total_loss
        self.total_loss = (self.quantity or Decimal('0')) * (self.unit_cost or Decimal('0'))
        
        # Deduct from batch's current_qty if batch is linked
        if self.batch and self.quantity:
            self.batch.current_qty -= self.quantity
            self.batch.save()
        
        # Deduct from product's current_stock
        if self.product_id and self.quantity:
            self.product_id.current_stock -= self.quantity
            self.product_id.save()
        
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.wastage_id} - {self.product_id.name if hasattr(self.product_id, 'name') else 'Unknown'} ({self.quantity})"
    
    @property
    def product_name(self):
        """Get product name for serialization."""
        try:
            return self.product_id.name
        except:
            return "Unknown Product"
    
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
