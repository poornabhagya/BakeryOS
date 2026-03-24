from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime


class Discount(models.Model):
    """
    Discount Model - Represents discounts applicable to products/categories
    
    Features:
    - Auto-generated discount_id (DISC-001, DISC-002, etc.)
    - Type: Percentage or FixedAmount
    - Applicable to: All products, Category, or Specific Product
    - Date and time range validation
    - Active/Inactive toggle
    - Automatic applicability checking
    """
    
    DISCOUNT_TYPE_CHOICES = [
        ('Percentage', 'Percentage (%)'),
        ('FixedAmount', 'Fixed Amount (Rs)'),
    ]
    
    APPLICABLE_TO_CHOICES = [
        ('All', 'All Products'),
        ('Category', 'Specific Category'),
        ('Product', 'Specific Product'),
    ]
    
    # Primary key
    id = models.AutoField(primary_key=True)
    
    # Auto-generated identifier
    discount_id = models.CharField(
        max_length=20,
        unique=True,
        editable=False
    )  # Format: DISC-001, DISC-002, etc.
    
    # Basic info
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    
    # Discount type and value
    discount_type = models.CharField(
        max_length=20,
        choices=DISCOUNT_TYPE_CHOICES,
        default='Percentage'
    )
    value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text='For Percentage: 0-100, For FixedAmount: any positive number'
    )
    
    # Applicability
    applicable_to = models.CharField(
        max_length=20,
        choices=APPLICABLE_TO_CHOICES,
        default='All'
    )
    
    # Foreign keys (nullable based on applicable_to)
    target_category_id = models.ForeignKey(
        'Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='discounts'
    )
    target_product_id = models.ForeignKey(
        'Product',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='discounts'
    )
    
    # Date range
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    
    # Time range (optional for daily time-based discounts)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['discount_id']),
            models.Index(fields=['is_active']),
            models.Index(fields=['applicable_to']),
            models.Index(fields=['start_date', 'end_date']),
        ]
    
    def __str__(self):
        return f"{self.discount_id} - {self.name}"
    
    def save(self, *args, **kwargs):
        """Auto-generate discount_id and validate constraints"""
        
        # Generate discount_id if not set
        if not self.discount_id:
            last_discount = Discount.objects.order_by('-id').first()
            if last_discount and last_discount.discount_id:
                # Extract number: DISC-001 → 001 → 001
                last_num = int(last_discount.discount_id.split('-')[1])
                new_num = str(last_num + 1).zfill(3)
            else:
                new_num = '001'
            self.discount_id = f'DISC-{new_num}'
        
        # Validate discount value
        if self.discount_type == 'Percentage':
            if not (0 < self.value <= 100):
                raise ValidationError(
                    "Percentage discount must be between 0 and 100"
                )
        elif self.discount_type == 'FixedAmount':
            if self.value <= 0:
                raise ValidationError(
                    "Fixed amount discount must be greater than 0"
                )
        
        # Validate date range
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                raise ValidationError(
                    "Start date cannot be after end date"
                )
        
        # Validate time range
        if self.start_time and self.end_time:
            if self.start_time >= self.end_time:
                raise ValidationError(
                    "Start time must be before end time"
                )
        
        # Validate applicable_to constraints
        if self.applicable_to == 'Category':
            if not self.target_category_id:
                raise ValidationError(
                    "Category must be selected when applicable_to is 'Category'"
                )
            if self.target_product_id:
                raise ValidationError(
                    "Product should not be set when applicable_to is 'Category'"
                )
        elif self.applicable_to == 'Product':
            if not self.target_product_id:
                raise ValidationError(
                    "Product must be selected when applicable_to is 'Product'"
                )
            if self.target_category_id:
                raise ValidationError(
                    "Category should not be set when applicable_to is 'Product'"
                )
        elif self.applicable_to == 'All':
            if self.target_category_id or self.target_product_id:
                raise ValidationError(
                    "No targets should be set when applicable_to is 'All'"
                )
        
        super().save(*args, **kwargs)
    
    def is_applicable_now(self):
        """Check if discount is applicable at current date/time"""
        return self.is_applicable_at(timezone.now())
    
    def is_applicable_at(self, check_datetime):
        """
        Check if discount is applicable at a specific date/time
        
        Args:
            check_datetime: datetime object to check against
            
        Returns:
            bool: True if discount is applicable
        """
        if not self.is_active:
            return False
        
        # Check date range
        check_date = check_datetime.date() if isinstance(check_datetime, datetime) else check_datetime
        
        if self.start_date and check_date < self.start_date:
            return False
        if self.end_date and check_date > self.end_date:
            return False
        
        # Check time range
        check_time = check_datetime.time() if isinstance(check_datetime, datetime) else None
        
        if check_time:
            if self.start_time and check_time < self.start_time:
                return False
            if self.end_time and check_time > self.end_time:
                return False
        
        return True
    
    def is_applicable_to_product(self, product):
        """
        Check if discount applies to specific product
        
        Args:
            product: Product instance
            
        Returns:
            bool: True if discount applies to product
        """
        if self.applicable_to == 'All':
            return True
        elif self.applicable_to == 'Category':
            return product.category_id == self.target_category_id
        elif self.applicable_to == 'Product':
            return product.id == self.target_product_id.id
        
        return False
    
    def calculate_discount_amount(self, amount):
        """
        Calculate discount amount based on type
        
        Args:
            amount: Original amount (price, total, etc.)
            
        Returns:
            float: Discount amount in Rs
        """
        if self.discount_type == 'Percentage':
            return float(amount) * (float(self.value) / 100)
        elif self.discount_type == 'FixedAmount':
            return float(self.value)
        return 0
