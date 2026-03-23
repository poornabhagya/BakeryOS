from django.db import models
from django.core.validators import MinValueValidator
from decimal import Decimal
from .product import Product
from .ingredient import Ingredient


class RecipeItem(models.Model):
    """
    RecipeItem model - links products to their required ingredients.
    
    Represents what ingredient and how much is needed to make a product.
    
    Features:
    - Link product to required ingredients
    - Track quantity required for each ingredient
    - Prevent duplicate ingredients in same recipe
    - Auto-calculate product cost_price from recipe
    
    Example:
    - White Bread (#PROD-1002) requires:
      - All Purpose Flour (#I001): 2.5 kg
      - Yeast (#I008): 0.01 kg
      - Salt (#I005): 0.02 kg
    """
    
    product_id = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='recipe_items',
        help_text="Product this recipe belongs to"
    )
    
    ingredient_id = models.ForeignKey(
        Ingredient,
        on_delete=models.PROTECT,
        related_name='used_in_recipes',
        help_text="Ingredient required for product"
    )
    
    quantity_required = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text="Quantity of ingredient needed (in base unit)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        # Prevent same ingredient appearing twice in recipe
        unique_together = ['product_id', 'ingredient_id']
        ordering = ['product_id', 'created_at']
        indexes = [
            models.Index(fields=['product_id']),
            models.Index(fields=['ingredient_id']),
        ]
    
    def __str__(self):
        return f"{self.product_id.product_id} - {self.ingredient_id.ingredient_id}: {self.quantity_required}{self.ingredient_id.base_unit}"
    
    @property
    def ingredient_cost(self):
        """
        Calculate cost of this ingredient for this recipe.
        Formula: quantity_required * ingredient_cost_per_unit
        
        Note: This uses the current ingredient cost, which may vary
        based on which batch was used. For historical accuracy,
        cost_per_unit should be frozen at production time.
        """
        if not hasattr(self.ingredient_id, 'cost_per_unit'):
            return Decimal('0')
        return self.quantity_required * self.ingredient_id.cost_per_unit
    
    def save(self, *args, **kwargs):
        """Validate quantity_required before saving"""
        if self.quantity_required <= 0:
            raise ValueError("Quantity required must be greater than 0")
        
        super().save(*args, **kwargs)
        
        # After saving, update the product's cost_price
        self.product_id.update_cost_price_from_recipe()
