#!/usr/bin/env python
"""Test script to verify product detail endpoint returns recipe items"""

import os
import sys
import django
import json

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from api.models import Product, Ingredient, RecipeItem, Category
from api.serializers.product_serializers import ProductCreateSerializer, ProductDetailSerializer

def test_product_detail_with_recipe():
    """Test that ProductDetailSerializer includes recipe items"""
    
    # Get the last created product (from our test)
    product = Product.objects.last()
    if not product:
        print("ERROR: No products in database.")
        return
    
    print(f"Testing product: {product.product_id}")
    
    # Use ProductDetailSerializer to serialize the product
    serializer = ProductDetailSerializer(product)
    data = serializer.data
    
    print(f"\n✅ Product serialized with ProductDetailSerializer:")
    print(json.dumps(data, indent=2, default=str))
    
    # Check recipe items in response
    recipe_items = data.get('recipe_items', [])
    print(f"\n✅ Recipe items in response: {len(recipe_items)}")
    
    if recipe_items:
        print("Recipe items details:")
        for item in recipe_items:
            print(f"  - Ingredient: {item.get('ingredient_name')} ({item.get('ingredient_id')}), "
                  f"Quantity: {item.get('quantity_required')} {item.get('ingredient_unit')}")
    else:
        print("(No recipe items in response)")
    
    # Check shelf_life and shelf_unit
    print(f"\n✅ Shelf Life: {data.get('shelf_life')} {data.get('shelf_unit')}")

if __name__ == "__main__":
    test_product_detail_with_recipe()
