from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator
from datetime import timedelta
from decimal import Decimal
from .product import Product


class ProductBatch(models.Model):
    """
    Product Batch model for production tracking.
    
    A batch represents a production run of a product.
    Used to track:
    - When products were made (made_date)
    - When they expire (expire_date)
    - How many produced (quantity)
    - Current status
    
    Features:
    - Auto-generated batch_id (PROD-BATCH-1001, PROD-BATCH-1002, etc.)
    - Links to Product
    - Auto-calculate expire_date from product.shelf_life
    - Track when batch is used/consumed
    - Audit trail via ProductStockHistory
    
    Business Logic:
    - When created: Add quantity to product.current_stock
    - When deleted: Deduct quantity from product.current_stock
    - When used: Reduce quantity for production usage
    - Auto-expire: Mark as expired if expire_date has passed
    """
    
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Expired', 'Expired'),
        ('Used', 'Used'),
    ]
    
    # Auto-generated fields
    batch_id = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        db_index=True,
        help_text="Auto-generated: PROD-BATCH-1001, PROD-BATCH-1002, etc."
    )
    
    # Foreign keys
    product_id = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='batches',
        db_index=True,
        help_text="Product this batch is made of"
    )
    
    # Batch info
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Total quantity produced in this batch"
    )
    
    current_qty = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        default=Decimal('0'),
        help_text="Current quantity remaining in batch (tracks consumption/usage)"
    )
    
    made_date = models.DateField(
        help_text="Date when batch was produced"
    )
    
    expire_date = models.DateField(
        help_text="Date when batch expires (auto-calculated: made_date + product.shelf_life)"
    )
    
    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='Active',
        db_index=True,
        help_text="Active, Expired, or Used"
    )
    
    # Additional info
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Notes about production e.g., 'Oven #2', 'Made by Baker1'"
    )
    
    # Metadata
    created_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )
    updated_at = models.DateTimeField(
        auto_now=True
    )
    
    class Meta:
        ordering = ['-made_date', '-created_at']
        indexes = [
            models.Index(fields=['batch_id']),
            models.Index(fields=['product_id', '-made_date']),
            models.Index(fields=['expire_date']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.batch_id} - {self.product_id.name} ({self.quantity} units)"
    
    @property
    def is_expired(self):
        """Check if batch is past expiry date"""
        return timezone.now().date() > self.expire_date
    
    @property
    def days_until_expiry(self):
        """Calculate days remaining until expiry"""
        from datetime import date
        today = date.today()
        if self.is_expired:
            return -(today - self.expire_date).days
        return (self.expire_date - today).days
    
    @property
    def expiring_soon(self):
        """Check if batch expires within 2 days"""
        return 0 <= self.days_until_expiry <= 2
    
    def save(self, *args, **kwargs):
        """
        Auto-generate batch_id and calculate expire_date if not already set.
        
        When creating a new batch:
        1. Initialize current_qty = quantity (for stock tracking) - FIRST PRIORITY
        2. Generate batch_id (PROD-BATCH-1001, etc.)
        3. Calculate expire_date from product.shelf_life
        4. Add quantity to product.current_stock
        5. Create ProductStockHistory entry
        """
        # CRITICAL: Initialize current_qty at the VERY BEGINNING before any other logic
        # This must happen before super().save() is called
        is_new = not self.pk
        if is_new and not self.current_qty:
            self.current_qty = self.quantity
        
        # Auto-generate batch_id
        if not self.batch_id:
            last_batch = ProductBatch.objects.all().order_by('id').last()
            if last_batch:
                try:
                    last_num = int(last_batch.batch_id.split('-')[-1])
                    next_num = last_num + 1
                except:
                    next_num = 1001
            else:
                next_num = 1001
            
            self.batch_id = f"PROD-BATCH-{next_num}"
        
        # Auto-calculate expire_date from product.shelf_life
        if not self.expire_date:
            from datetime import timedelta
            shelf_days = self._calculate_shelf_days()
            self.expire_date = self.made_date + timedelta(days=shelf_days)
        
        # Store old quantity for comparison (if updating)
        old_quantity = None
        if not is_new:
            try:
                old_batch = ProductBatch.objects.get(pk=self.pk)
                old_quantity = old_batch.quantity
            except ProductBatch.DoesNotExist:
                pass
        
        super().save(*args, **kwargs)
        
        # Update product stock and create audit trail
        if is_new:
            # New batch: add to product stock
            self._add_to_product_stock()
        elif old_quantity and old_quantity != self.quantity:
            # Updated batch quantity: adjust difference
            qty_diff = self.quantity - old_quantity
            self._adjust_product_stock(qty_diff, 'Update')
    
    def delete(self, *args, **kwargs):
        """
        Delete batch and deduct quantity from product stock.
        Create ProductStockHistory entry for audit trail.
        """
        # Deduct from product stock before deleting
        self._deduct_from_product_stock()
        
        super().delete(*args, **kwargs)
    
    def _calculate_shelf_days(self):
        """
        Convert product.shelf_life (with unit) to days.
        
        Returns:
            int: Number of days
        """
        shelf_life = self.product_id.shelf_life
        shelf_unit = self.product_id.shelf_unit
        
        if shelf_unit == 'hours':
            # Convert hours to days
            return max(1, shelf_life // 24)
        elif shelf_unit == 'weeks':
            # Convert weeks to days
            return shelf_life * 7
        else:  # days
            return shelf_life
    
    def _add_to_product_stock(self):
        """
        Add batch quantity to product.current_stock and create audit trail.
        Called when batch is created.
        """
        from .product import ProductStockHistory
        from django.contrib.auth import get_user_model
        
        product = self.product_id
        
        # Update product stock
        qty_before = product.current_stock
        product.current_stock += self.quantity
        product.save(update_fields=['current_stock', 'updated_at'])
        
        # Create audit trail entry
        ProductStockHistory.objects.create(
            product_id=product,
            transaction_type='AddStock',
            qty_before=qty_before,
            qty_after=product.current_stock,
            change_amount=self.quantity,
            user_id=None,  # No user context in batch creation
            notes=f"New production batch {self.batch_id} created"
        )
    
    def _deduct_from_product_stock(self):
        """
        Deduct batch quantity from product.current_stock and create audit trail.
        Called when batch is deleted.
        """
        from .product import ProductStockHistory
        
        product = self.product_id
        
        # Update product stock
        qty_before = product.current_stock
        product.current_stock = max(Decimal('0'), product.current_stock - self.quantity)
        product.save(update_fields=['current_stock', 'updated_at'])
        
        # Create audit trail entry
        ProductStockHistory.objects.create(
            product_id=product,
            transaction_type='WasteStock',
            qty_before=qty_before,
            qty_after=product.current_stock,
            change_amount=-self.quantity,
            user_id=None,
            notes=f"Production batch {self.batch_id} deleted/voided"
        )
    
    def _adjust_product_stock(self, qty_diff, reason='StockAdjustment'):
        """
        Adjust product stock by quantity difference (for updates).
        
        Args:
            qty_diff (Decimal): Positive to add, negative to deduct
            reason (str): Reason for adjustment
        """
        from .product import ProductStockHistory
        
        product = self.product_id
        
        # Update product stock
        qty_before = product.current_stock
        product.current_stock = max(Decimal('0'), product.current_stock + qty_diff)
        product.save(update_fields=['current_stock', 'updated_at'])
        
        # Create audit trail entry
        ProductStockHistory.objects.create(
            product_id=product,
            transaction_type='StockAdjustment',
            qty_before=qty_before,
            qty_after=product.current_stock,
            change_amount=qty_diff,
            user_id=None,
            notes=f"Batch {self.batch_id} quantity updated: {reason}"
        )
    
    def mark_expired(self):
        """Mark batch as expired and deduct from product stock if still marked active"""
        if self.status == 'Active':
            self.status = 'Expired'
            self._deduct_from_product_stock()
            self.save(update_fields=['status', 'updated_at'])
    
    def use_batch(self, quantity_used):
        """
        Use quantity from batch (for production/consumption).
        Deducts used quantity from product stock.
        
        Args:
            quantity_used (Decimal): Amount being used
            
        Returns:
            bool: True if successful, False if not enough quantity
        """
        if quantity_used > self.quantity:
            return False  # Not enough quantity
        
        from .product import ProductStockHistory
        
        product = self.product_id
        
        # Update product stock
        qty_before = product.current_stock
        product.current_stock = max(Decimal('0'), product.current_stock - quantity_used)
        product.save(update_fields=['current_stock', 'updated_at'])
        
        # Create audit trail entry
        ProductStockHistory.objects.create(
            product_id=product,
            transaction_type='UseStock',
            qty_before=qty_before,
            qty_after=product.current_stock,
            change_amount=-quantity_used,
            user_id=None,
            notes=f"Production batch {self.batch_id} used: {quantity_used} units"
        )
        
        return True
