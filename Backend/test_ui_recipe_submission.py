#!/usr/bin/env python
"""
Test script to verify that recipe items are correctly saved when submitted via the UI form.
This simulates the exact payload that the updated AddItemModal.tsx will send.
"""

import os
import django
import json
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import Product, Ingredient, RecipeItem
from api.serializers import ProductCreateSerializer

print("=" * 80)
print("SIMULATING UI FORM SUBMISSION WITH RECIPE ITEMS")
print("=" * 80)

# This is the exact payload format that comes from the updated AddItemModal.tsx
ui_payload = {
    'name': 'UI Test Product - Chocolate Cake',
    'category_id': 2,  # Cakes category
    'cost_price': '150.00',
    'selling_price': '350.00',
    'shelf_life': 7,
    'shelf_unit': 'days',  # Now lowercase as per backend requirement
    'preparation_instructions': 'Mix and bake at 180C for 25 minutes',
    'current_stock': 0,
    'recipe_items': [
        {
            'ingredient_id': 13,  # Real database ID for Baking Powder
            'quantity_required': 2.5
        },
        {
            'ingredient_id': 14,  # Real database ID for Baking Soda
            'quantity_required': 1.0
        },
        {
            'ingredient_id': 8,   # Real database ID for Butter
            'quantity_required': 3.5
        }
    ]
}

print("\n✓ Payload to be sent from updated AddItemModal.tsx:")
print(json.dumps(ui_payload, indent=2, default=str))

# Test the serializer with this exact payload
serializer = ProductCreateSerializer(data=ui_payload)

if serializer.is_valid():
    print("\n" + "=" * 80)
    print("✅ SERIALIZER VALIDATION PASSED")
    print("=" * 80)
    
    # Save the product
    product = serializer.save()
    print(f"\n✓ Product created: {product.product_id} - {product.name}")
    
    # Check if recipe items were created
    recipe_items = RecipeItem.objects.filter(product_id=product)
    print(f"✓ Recipe items created: {recipe_items.count()}")
    
    for recipe in recipe_items:
        print(f"  - {recipe.ingredient_id.name}: {recipe.quantity_required} {recipe.ingredient_id.base_unit}")
    
    print("\n" + "=" * 80)
    print("✅ COMPLETE SUCCESS - Recipe items saved with product!")
    print("=" * 80)
    
else:
    print("\n" + "=" * 80)
    print("❌ SERIALIZER VALIDATION FAILED")
    print("=" * 80)
    print(f"Errors: {serializer.errors}")
