#!/usr/bin/env python
"""Detailed test to diagnose the 500 error"""

import os
import sys
import django
import traceback

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from api.models import Product, Category, Ingredient, RecipeItem
from api.serializers.product_serializers import ProductCreateSerializer
from decimal import Decimal

def test_serializer_response():
    """Test if to_representation works correctly"""
    
    # Get a product category
    categories = Category.objects.filter(type='Product').first()
    if not categories:
        print("ERROR: No product categories found.")
        return
    
    # Get ingredients
    ingredients = Ingredient.objects.all()[:2]
    if len(ingredients) < 2:
        print("ERROR: Need at least 2 ingredients")
        return
    
    # Build payload
    payload = {
        "name": f"Serializer Test {Product.objects.count() + 1}",
        "category_id": categories.id,
        "cost_price": 15.00,
        "selling_price": 29.99,
        "shelf_life": 5,
        "shelf_unit": "days",
        "preparation_instructions": "Mix and bake",
        "current_stock": 0,
        "recipe_items": [
            {"ingredient_id": str(ing.id), "quantity_required": "2.5"}
            for ing in ingredients
        ]
    }
    
    print("[TEST] Creating serializer with payload...")
    serializer = ProductCreateSerializer(data=payload)
    
    if not serializer.is_valid():
        print(f"❌ Validation failed: {serializer.errors}")
        return
    
    print("✅ Serializer validation passed")
    
    try:
        print("[TEST] Calling serializer.save()...")
        product = serializer.save()
        print(f"✅ Product created: {product.product_id}")
        
        print("[TEST] Calling serializer.data (which calls to_representation)...")
        response_data = serializer.data
        print(f"✅ Serializer.data returned successfully")
        print(f"Response contains recipe_items: {('recipe_items' in response_data)}")
        if 'recipe_items' in response_data:
            print(f"Recipe items count: {len(response_data['recipe_items'])}")
        
    except Exception as e:
        print(f"\n❌ EXCEPTION during serialization:")
        print(traceback.format_exc())

if __name__ == "__main__":
    test_serializer_response()
