#!/usr/bin/env python
"""Test script to verify ingredients and recipe items are properly set up for UI testing"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import Ingredient, RecipeItem, Product

print("=" * 70)
print("INGREDIENTS IN DATABASE (showing real IDs)")
print("=" * 70)
ingredients = Ingredient.objects.all()[:10]
for ing in ingredients:
    print(f"  ID: {ing.id:3d} | Name: {ing.name:25s} | Unit: {ing.base_unit:6s}")

total_ing = Ingredient.objects.count()
print(f"\nTotal ingredients in database: {total_ing}")

print("\n" + "=" * 70)
print("EXISTING RECIPE ITEMS (Sample)")
print("=" * 70)
recipe_count = RecipeItem.objects.count()
print(f"Total recipe items: {recipe_count}")

if recipe_count > 0:
    recent = RecipeItem.objects.all()[:5]
    for item in recent:
        print(f"  Product: {item.product_id.product_id} | Ingredient: {item.ingredient_id.name:20s} | Qty: {item.quantity_required}")

print("\n" + "=" * 70)
print("NEXT STEPS FOR UI TEST")
print("=" * 70)
print("✓ Open UI Add Product Modal")
print("✓ Select an ingredient from the list (use one of the IDs shown above)")
print("✓ Enter a quantity (e.g., 2.50)")
print("✓ Submit the form")
print("✓ Check Django admin to verify recipe_items saved")
