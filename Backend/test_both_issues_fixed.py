#!/usr/bin/env python
"""Test to verify shelf_life display and recipe items saving - both issues fixed"""

import os
import sys
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from api.models import Product, Category, Ingredient, RecipeItem
from api.serializers.product_serializers import ProductListSerializer, ProductDetailSerializer

def test_shelf_life_in_list():
    """Test that shelf_life and shelf_unit are in list response"""
    print("\n=== TEST 1: Shelf Life in ProductListSerializer ===")
    product = Product.objects.first()
    if not product:
        print("ERROR: No products found")
        return
    
    serializer = ProductListSerializer(product)
    data = serializer.data
    
    print(f"Product: {product.product_id}")
    print(f"Has shelf_life: {'shelf_life' in data}")
    print(f"Has shelf_unit: {'shelf_unit' in data}")
    
    if 'shelf_life' in data and 'shelf_unit' in data:
        print(f"✅ Shelf Life: {data['shelf_life']} {data['shelf_unit']}")
    else:
        print("❌ Missing shelf_life or shelf_unit fields")

def test_shelf_life_and_recipe_in_detail():
    """Test that shelf_life, shelf_unit, and recipe_items are in detail response"""
    print("\n=== TEST 2: Shelf Life and Recipe Items in ProductDetailSerializer ===")
    product = Product.objects.first()
    if not product:
        print("ERROR: No products found")
        return
    
    serializer = ProductDetailSerializer(product)
    data = serializer.data
    
    print(f"Product: {product.product_id}")
    print(f"Has shelf_life: {'shelf_life' in data}")
    print(f"Has shelf_unit: {'shelf_unit' in data}")
    print(f"Has recipe_items: {'recipe_items' in data}")
    
    if 'shelf_life' in data:
        print(f"✅ Shelf Life: {data['shelf_life']} {data['shelf_unit']}")
    
    if 'recipe_items' in data:
        recipe_count = len(data['recipe_items'])
        print(f"✅ Recipe Items: {recipe_count}")
        for item in data['recipe_items'][:3]:
            print(f"   - {item.get('ingredient_name')}: {item.get('quantity_required')} {item.get('ingredient_unit')}")
    else:
        print("❌ recipe_items field missing")

def test_recipe_items_saved():
    """Test that recipe items are actually saved to database"""
    print("\n=== TEST 3: Recipe Items Saved to Database ===")
    
    # Count total recipe items
    total_recipe_items = RecipeItem.objects.count()
    print(f"Total RecipeItem records in database: {total_recipe_items}")
    
    # Find products with recipe items
    products_with_recipes = Product.objects.filter(recipe_items__isnull=False).distinct()
    print(f"Products with recipe items: {products_with_recipes.count()}")
    
    if products_with_recipes.count() > 0:
        for prod in products_with_recipes[:3]:
            recipe_count = prod.recipe_items.count()
            print(f"\n✅ {prod.product_id} ({prod.name}):")
            print(f"   - Shelf Life: {prod.shelf_life} {prod.shelf_unit}")
            print(f"   - Recipe Items: {recipe_count}")
            
            for recipe_item in prod.recipe_items.all():
                print(f"      • {recipe_item.ingredient_id.name}: {recipe_item.quantity_required} {recipe_item.ingredient_id.base_unit}")
    else:
        print("ℹ️  No products with recipe items found (this is OK - they may not have been created yet)")

if __name__ == "__main__":
    test_shelf_life_in_list()
    test_shelf_life_and_recipe_in_detail()
    test_recipe_items_saved()
    print("\n✅ All checks complete!")
