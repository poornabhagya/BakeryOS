from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver


class Category(models.Model):
    """
    Unified Category model for both Products and Ingredients.
    
    Types:
    - Product: Used for bakery products (Buns, Bread, Cakes, etc.)
    - Ingredient: Used for raw materials (Flour, Sugar, Dairy, etc.)
    """
    
    TYPE_CHOICES = [
        ('Product', 'Product'),
        ('Ingredient', 'Ingredient'),
    ]
    
    category_id = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        editable=False,
        help_text="Auto-generated ID: CAT-P001, CAT-I001, etc."
    )
    
    name = models.CharField(
        max_length=100,
        help_text="Category name (e.g., 'Bread', 'Flour')"
    )
    
    type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        help_text="Category type: Product or Ingredient"
    )
    
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Detailed description of category"
    )
    
    low_stock_alert = models.IntegerField(
        blank=True,
        null=True,
        default=None,
        help_text="Quantity threshold for low stock alerts (for Product categories)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'api_category'
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'
        
        # Unique constraint on (type, name)
        unique_together = [('type', 'name')]
        
        # Indexes for fast querying
        indexes = [
            models.Index(fields=['category_id']),
            models.Index(fields=['type']),
            models.Index(fields=['name']),
            models.Index(fields=['type', 'name']),
        ]
        
        ordering = ['type', 'name']
    
    def __str__(self):
        return f"{self.category_id} - {self.name} ({self.type})"
    
    def save(self, *args, **kwargs):
        """Auto-generate category_id before saving"""
        if not self.category_id:
            # Get the prefix based on type
            if self.type == 'Product':
                prefix = 'CAT-P'
            else:  # Ingredient
                prefix = 'CAT-I'
            
            # Count existing categories with same type
            count = Category.objects.filter(type=self.type).count()
            
            # Generate ID: CAT-P001, CAT-I001, etc.
            self.category_id = f"{prefix}{count + 1:03d}"
        
        super().save(*args, **kwargs)


# Signal for auto-ID generation
@receiver(pre_save, sender=Category)
def generate_category_id(sender, instance, **kwargs):
    """Signal to auto-generate category_id if not provided"""
    if not instance.category_id:
        if instance.type == 'Product':
            prefix = 'CAT-P'
        else:
            prefix = 'CAT-I'
        
        # Count existing to get next number
        count = Category.objects.filter(type=instance.type).count()
        instance.category_id = f"{prefix}{count + 1:03d}"
