from django.db import models
from django.utils import timezone
from datetime import timedelta
from .ingredient import Ingredient


class IngredientBatch(models.Model):
    """
    IngredientBatch model for tracking batch-level inventory.
    
    Features:
    - Auto-generated batch_id (BATCH-1001, BATCH-1002, etc.)
    - Linked to Ingredient
    - Tracks received quantity and current remaining quantity
    - Cost per unit for financial tracking
    - Expiry date management with auto-expiry calculation
    - Status tracking: Active, Expired, Used
    - FIFO ordering for consumption
    
    Key Rules:
    - current_qty must be <= quantity
    - expire_date must be >= made_date
    - Batches are automatically ordered by expire_date (FIFO)
    - is_expired is calculated from expire_date < today
    - total_quantity in Ingredient is synced via signals
    """
    
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Expired', 'Expired'),
        ('Used', 'Used'),  # Fully consumed
    ]
    
    # Auto-generated fields
    batch_id = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        db_index=True,
        help_text="Auto-generated: BATCH-1001, BATCH-1002, etc."
    )
    
    # Foreign keys
    ingredient_id = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
        related_name='batches',
        help_text="Ingredient this batch belongs to"
    )
    
    # Quantity fields
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Total quantity received for this batch"
    )
    
    current_qty = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Current remaining quantity in this batch"
    )
    
    # Cost tracking
    cost_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Cost per unit (optional for financial tracking)"
    )
    
    # Date fields
    made_date = models.DateTimeField(
        default=timezone.now,
        help_text="Date batch was received/created"
    )
    
    expire_date = models.DateTimeField(
        help_text="Expiry date for this batch"
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Active',
        db_index=True,
        help_text="Current status of the batch"
    )
    
    # Audit fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['expire_date', 'made_date']  # FIFO ordering
        indexes = [
            models.Index(fields=['ingredient_id', 'status']),
            models.Index(fields=['expire_date']),
            models.Index(fields=['status']),
            models.Index(fields=['batch_id']),
        ]
        verbose_name = 'Ingredient Batch'
        verbose_name_plural = 'Ingredient Batches'
    
    def __str__(self):
        return f"{self.batch_id} - {self.ingredient_id.name} ({self.current_qty}/{self.quantity})"
    
    @property
    def is_expired(self):
        """Check if batch has expired"""
        return timezone.now() > self.expire_date
    
    @property
    def days_until_expiry(self):
        """Calculate days remaining until expiry"""
        days = (self.expire_date - timezone.now()).days
        return max(days, 0) if not self.is_expired else days
    
    @property
    def total_cost(self):
        """Calculate total cost for this batch"""
        if self.cost_price is None:
            return None
        return self.quantity * self.cost_price
    
    @property
    def expiry_progress(self):
        """Get expiry progress as percentage (0-100)"""
        from datetime import datetime
        now = timezone.now()
        if now >= self.expire_date:
            return 100
        days_from_creation = (self.expire_date - self.made_date).days
        days_passed = (now - self.made_date).days
        if days_from_creation <= 0:
            return 100
        return min(100, int((days_passed / days_from_creation) * 100))
    
    def consume(self, amount):
        """
        Consume (use) a quantity from this batch.
        
        Args:
            amount: Decimal quantity to consume
        
        Returns:
            dict: {'success': bool, 'message': str, 'remaining': decimal}
        """
        if amount <= 0:
            return {'success': False, 'message': 'Consume amount must be > 0'}
        
        if amount > self.current_qty:
            return {
                'success': False,
                'message': f'Not enough quantity. Available: {self.current_qty}, Requested: {amount}'
            }
        
        if self.is_expired:
            return {'success': False, 'message': 'Cannot consume from expired batch'}
        
        self.current_qty -= amount
        if self.current_qty == 0:
            self.status = 'Used'
        self.save()
        
        return {
            'success': True,
            'message': f'Consumed {amount} from batch',
            'remaining': self.current_qty
        }
    
    def mark_as_expired(self):
        """Manually mark batch as expired"""
        self.status = 'Expired'
        self.save()
        return True
    
    def can_consume(self):
        """Check if this batch can be consumed (for FIFO logic)"""
        return self.current_qty > 0 and not self.is_expired and self.status == 'Active'


# Signal handlers for auto-ID generation and quantity sync
from django.db.models.signals import pre_save, post_save, post_delete
from django.dispatch import receiver


@receiver(pre_save, sender=IngredientBatch)
def auto_generate_batch_id(sender, instance, **kwargs):
    """Auto-generate batch_id if not set"""
    if not instance.batch_id:
        last_batch = IngredientBatch.objects.all().order_by('-id').first()
        next_number = (last_batch.id if last_batch else 0) + 1
        instance.batch_id = f"BATCH-{1000 + next_number}"
    
    # Auto-mark as expired if expire_date has passed
    if instance.is_expired and instance.status == 'Active':
        instance.status = 'Expired'
    
    # Validate expire_date >= made_date
    if instance.expire_date < instance.made_date:
        raise ValueError("Expiry date must be on or after made date")
    
    # Validate current_qty <= quantity
    if instance.current_qty > instance.quantity:
        raise ValueError("Current quantity cannot exceed received quantity")


@receiver(post_save, sender=IngredientBatch)
def sync_ingredient_quantity_on_batch_save(sender, instance, created, **kwargs):
    """Update ingredient total_quantity when batch is created/updated"""
    sync_ingredient_total(instance.ingredient_id)


@receiver(post_delete, sender=IngredientBatch)
def sync_ingredient_quantity_on_batch_delete(sender, instance, **kwargs):
    """Update ingredient total_quantity when batch is deleted"""
    sync_ingredient_total(instance.ingredient_id)


def sync_ingredient_total(ingredient):
    """
    Sync the ingredient's total_quantity from all active batches.
    
    Args:
        ingredient: Ingredient instance to sync
    """
    active_batches = IngredientBatch.objects.filter(
        ingredient_id=ingredient,
        status='Active'
    )
    total = sum(batch.current_qty for batch in active_batches)
    ingredient.total_quantity = total
    ingredient.save(update_fields=['total_quantity'])
