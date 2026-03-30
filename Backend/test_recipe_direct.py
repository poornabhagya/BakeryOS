#!/usr/bin/env python
"""Test script to verify recipe item creation using Django directly"""

import os
import sys
import django
import json

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from api.models import Product, Ingredient, RecipeItem, Category
from api.serializers.product_serializers import ProductCreateSerializer

def test_product_with_recipe():
    """Test creating a product with recipe items using serializer"""
    
    # Get a product category
    categories = Category.objects.filter(type='Product').first()
    if not categories:
        print("ERROR: No product categories found.")
        return
    
    category_id = categories.id
    print(f"Using category: {categories.name} (ID: {category_id})")
    
    # Get some ingredients
    ingredients = Ingredient.objects.all()[:3]
    print(f"Available ingredients count: {Ingredient.objects.count()}")
    
    if len(ingredients) < 2:
        print("ERROR: Not enough ingredients in database. Need at least 2.")
        return
    
    # Build recipe items
    recipe_items = []
    for ing in ingredients[:2]:  # Use first 2 ingredients
        recipe_items.append({
            "ingredient_id": ing.id,  # Use the database ID directly
            "quantity_required": "2.5"
        })
    
    # Create product payload - exactly what the frontend would send
    payload = {
        "name": f"Test Product {Product.objects.count() + 1}",
        "category_id": category_id,
        "cost_price": 10.50,
        "selling_price": 19.99,
        "shelf_life": 7,
        "shelf_unit": "days",
        "preparation_instructions": "Mix well and bake",
        "current_stock": 0,
        "recipe_items": recipe_items
    }
    
    print(f"\n[TEST] Creating product with payload:")
    print(json.dumps(payload, indent=2))
    
    # Test the serializer directly
    serializer = ProductCreateSerializer(data=payload)
    
    if serializer.is_valid():
        print("\n✅ Serializer validation passed")
        product = serializer.save()
        print(f"✅ Product created: {product.product_id}")
        
        # Verify recipe items in database
        recipe_count = RecipeItem.objects.filter(product_id=product).count()
        print(f"✅ Recipe items saved in database: {recipe_count}")
        
        # Detail the recipe items
        recipe_items_saved = RecipeItem.objects.filter(product_id=product).values(
            'id', 'ingredient_id', 'quantity_required', 'created_at'
        )
        for item in recipe_items_saved:
            print(f"   - Ingredient ID: {item['ingredient_id']}, Quantity: {item['quantity_required']}")
            
    else:
        print(f"\n❌ Serializer validation failed:")
        for field, errors in serializer.errors.items():
            print(f"   {field}: {errors}")

if __name__ == "__main__":
    test_product_with_recipe()
