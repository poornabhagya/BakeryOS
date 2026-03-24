from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from decimal import Decimal


class Sale(models.Model):
    """
    Sale Model - Represents a customer bill/transaction
    
    Features:
    - Auto-generated bill_number (BILL-1001, BILL-1002, etc.)
    - Links to cashier who processed the sale
    - Optional discount application
    - Multiple payment methods supported
    - Automatic calculation of totals
    - Timestamps for audit trail
    """
    
    PAYMENT_METHOD_CHOICES = [
        ('Cash', 'Cash'),
        ('Card', 'Debit/Credit Card'),
        ('Mobile', 'Mobile Money'),
        ('Cheque', 'Cheque'),
        ('Other', 'Other'),
    ]
    
    # Primary key
    id = models.AutoField(primary_key=True)
    
    # Auto-generated bill number
    bill_number = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        db_index=True
    )  # Format: BILL-1001, BILL-1002, etc.
    
    # Foreign keys
    cashier_id = models.ForeignKey(
        'User',
        on_delete=models.PROTECT,
        related_name='sales',
        help_text="Cashier who processed the sale"
    )
    
    # Optional discount
    discount_id = models.ForeignKey(
        'Discount',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='applied_sales',
        help_text="Discount applied to entire sale"
    )
    
    # Amounts
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Sum of all items before discount"
    )
    
    discount_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Discount amount applied"
    )
    
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Final amount after discount"
    )
    
    # Payment info
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        default='Cash'
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes about sale"
    )
    
    # Timestamps
    date_time = models.DateTimeField(
        default=timezone.now,
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date_time']
        indexes = [
            models.Index(fields=['bill_number']),
            models.Index(fields=['cashier_id']),
            models.Index(fields=['date_time']),
            models.Index(fields=['payment_method']),
        ]
    
    def __str__(self):
        return f"{self.bill_number} - {self.total_amount}"
    
    def save(self, *args, **kwargs):
        """Auto-generate bill_number and validate amounts"""
        
        # Generate bill_number if not set
        if not self.bill_number:
            last_sale = Sale.objects.order_by('-id').first()
            if last_sale and last_sale.bill_number:
                # Extract number: BILL-1001 → 1001
                last_num = int(last_sale.bill_number.split('-')[1])
                new_num = str(last_num + 1).zfill(4)
            else:
                new_num = '1001'
            self.bill_number = f'BILL-{new_num}'
        
        # Validate amounts
        if self.subtotal < 0:
            raise ValidationError("Subtotal cannot be negative")
        
        if self.discount_amount < 0:
            raise ValidationError("Discount amount cannot be negative")
        
        # Ensure discount doesn't exceed subtotal
        if self.discount_amount > self.subtotal:
            raise ValidationError(
                f"Discount amount ({self.discount_amount}) cannot exceed subtotal ({self.subtotal})"
            )
        
        # Auto-calculate total_amount if discount_amount was set
        if self.discount_amount and not self.discount_id:
            # Manual discount
            self.total_amount = self.subtotal - Decimal(str(self.discount_amount))
        elif self.discount_id:
            # Calculate discount using discount model
            discount_result = self.discount_id.calculate_discount_amount(self.subtotal)
            self.discount_amount = Decimal(str(discount_result))
            self.total_amount = self.subtotal - self.discount_amount
        else:
            # No discount
            self.discount_amount = Decimal('0')
            self.total_amount = self.subtotal
        
        # Ensure total_amount is never negative
        if self.total_amount < 0:
            self.total_amount = 0
        
        super().save(*args, **kwargs)


class SaleItem(models.Model):
    """
    SaleItem Model - Represents individual line items in a sale/bill
    
    Features:
    - Links to Sale (bill header)
    - Links to Product
    - Quantity and unit price at time of sale
    - Auto-calculated subtotal
    - Immutable after creation
    """
    
    # Foreign keys
    sale_id = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE,
        related_name='items',
        help_text="Sale this item belongs to"
    )
    
    product_id = models.ForeignKey(
        'Product',
        on_delete=models.PROTECT,
        related_name='sale_items',
        help_text="Product sold"
    )
    
    # Sale details
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Units sold"
    )
    
    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Price per unit at time of sale (frozen)"
    )
    
    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text="quantity * unit_price"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['sale_id']),
            models.Index(fields=['product_id']),
        ]
    
    def __str__(self):
        return f"{self.sale_id} - {self.product_id} x{self.quantity}"
    
    def save(self, *args, **kwargs):
        """Validate quantities and calculate subtotal"""
        
        # Validate quantity
        if self.quantity <= 0:
            raise ValidationError("Quantity must be greater than 0")
        
        # Validate unit price
        if self.unit_price <= 0:
            raise ValidationError("Unit price must be greater than 0")
        
        # Calculate subtotal
        self.subtotal = self.quantity * self.unit_price
        
        super().save(*args, **kwargs)
