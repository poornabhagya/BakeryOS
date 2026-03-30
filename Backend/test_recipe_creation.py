#!/usr/bin/env python
"""Test script to verify recipe item creation in product POST request"""

import os
import sys
import django
import requests
import json

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from api.models import Product, Ingredient, RecipeItem, Category

BASE_URL = "http://localhost:8000/api"

def get_auth_token():
    """Get token for authentication"""
    try:
        # Try to get admin user - credentials might be set, we'll handle auth later
        response = requests.post(f"{BASE_URL}/token/", json={
            "username": "admin",
            "password": "admin123"
        })
        if response.status_code == 200:
            return response.json().get("access")
    except Exception as e:
        print(f"Error getting token: {e}")
    return None

def test_product_with_recipe():
    """Test creating a product with recipe items"""
    
    # Get token
    token = get_auth_token()
    print(f"Token: {token}")
    
    headers = {
        "Content-Type": "application/json",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    
    # Get a product category
    all_categories = Category.objects.all().values('id', 'name', 'type')
    print(f"All categories in database: {list(all_categories)}")
    
    categories = Category.objects.filter(type='product').first()
    if not categories:
        # Try to get any category
        categories = Category.objects.first()
        if not categories:
            print("ERROR: No categories found at all.")
            return
        print(f"WARNING: No product-type categories found, using: {categories.name}")
    
    category_id = categories.id
    print(f"Using category: {categories.name} (ID: {category_id}, Type: {categories.type})")
    
    # Get some ingredients
    ingredients = Ingredient.objects.all()[:3]
    print(f"Available ingredients: {list(ingredients.values_list('ingredient_id', 'name'))}")
    
    if len(ingredients) < 1:
        print("ERROR: Not enough ingredients in database. Create some first.")
        return
    
    # Build recipe items
    recipe_items = []
    for ing in ingredients[:2]:  # Use first 2 ingredients
        recipe_items.append({
            "ingredient_id": ing.id,  # Use the database ID directly
            "quantity_required": "2.5"
        })
    
    # Create product payload
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
    
    print(f"\n[TEST] Sending payload:")
    print(json.dumps(payload, indent=2))
    
    # Make request
    try:
        response = requests.post(
            f"{BASE_URL}/products/",
            json=payload,
            headers=headers
        )
        
        print(f"\n[TEST] Response status: {response.status_code}")
        print(f"[TEST] Response body: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code in [200, 201]:
            created_product = response.json()
            product_id = created_product.get('product_id')
            print(f"\n✅ Product created successfully: {product_id}")
            
            # Verify recipe items in database
            db_product = Product.objects.get(product_id=product_id)
            recipe_count = RecipeItem.objects.filter(product_id=db_product).count()
            print(f"✅ Recipe items in database: {recipe_count}")
            
            # Get product detail to see if recipe_items are returned
            detail_response = requests.get(
                f"{BASE_URL}/products/{product_id}/",
                headers=headers
            )
            if detail_response.status_code == 200:
                detail_data = detail_response.json()
                returned_recipe_items = detail_data.get('recipe_items', [])
                print(f"✅ Recipe items returned in detail: {len(returned_recipe_items)}")
                print(f"   Detail: {json.dumps(returned_recipe_items, indent=2)}")
            
        else:
            print(f"❌ Error creating product")
            
    except Exception as e:
        print(f"❌ Exception: {e}")

if __name__ == "__main__":
    test_product_with_recipe()
