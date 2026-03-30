#!/usr/bin/env python
"""Test script to verify full HTTP API flow with recipe items"""

import os
import sys
import django
import requests
import json
import uuid
from datetime import datetime

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from api.models import Category, Ingredient, User
from rest_framework.authtoken.models import Token

BASE_URL = "http://localhost:8000/api"

def get_or_create_auth_token():
    """Get or create token for admin user"""
    try:
        # Try to get existing admin user
        admin_user = User.objects.filter(username='admin').first()
        if admin_user:
            token, _ = Token.objects.get_or_create(user=admin_user)
            return token.key
    except Exception as e:
        print(f"Warning: Could not get token: {e}")
    return None

def test_api_flow():
    """Test creating product via API and retrieving it"""
    
    # Get token
    token = get_or_create_auth_token()
    if not token:
        print("ERROR: Could not get authentication token")
        return
    
    print(f"✅ Using auth token: {token[:20]}...")
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Token {token}"
    }
    
    # Get a product category
    categories = Category.objects.filter(type='Product').first()
    if not categories:
        print("ERROR: No product categories found.")
        return
    
    category_id = categories.id
    print(f"✅ Using category: {categories.name} (ID: {category_id})")
    
    # Get ingredients
    ingredients = Ingredient.objects.all()[:2]
    if len(ingredients) < 2:
        print("ERROR: Need at least 2 ingredients")
        return
    
    # Build recipe items
    recipe_items = [
        {"ingredient_id": ing.id, "quantity_required": "2.5"}
        for ing in ingredients
    ]
    
    # Create product payload with unique name
    unique_name = f"API Test Product {datetime.now().strftime('%Y%m%d%H%M%S%f')}"
    payload = {
        "name": unique_name,
        "category_id": category_id,
        "cost_price": 15.00,
        "selling_price": 29.99,
        "shelf_life": 5,
        "shelf_unit": "days",
        "preparation_instructions": "Mix and bake",
        "current_stock": 0,
        "recipe_items": recipe_items
    }
    
    print(f"\n[TEST] POST /api/products/")
    print(f"[TEST] Payload: {json.dumps(payload, indent=2)}")
    
    # Create product via API
    response = requests.post(
        f"{BASE_URL}/products/",
        json=payload,
        headers=headers
    )
    
    print(f"\n[TEST] Response status: {response.status_code}")
    
    if response.status_code == 201:
        print("✅ Product created successfully (201)")
        created_product = response.json()
        product_id = created_product.get('product_id')
        print(f"✅ Product ID: {product_id}")
        
        # Verify response includes recipe_items
        recipe_items_response = created_product.get('recipe_items', [])
        print(f"✅ Recipe items in response: {len(recipe_items_response)}")
        
        for item in recipe_items_response:
            print(f"   - {item.get('ingredient_name')}: {item.get('quantity_required')} {item.get('ingredient_unit')}")
        
        # Verify shelf_life returned
        print(f"✅ Shelf Life: {created_product.get('shelf_life')} {created_product.get('shelf_unit')}")
        
        # Now GET the product
        print(f"\n[TEST] GET /api/products/{product_id}/")
        detail_response = requests.get(
            f"{BASE_URL}/products/{product_id}/",
            headers=headers
        )
        
        print(f"[TEST] Response status: {detail_response.status_code}")
        
        if detail_response.status_code == 200:
            print("✅ Product retrieved successfully (200)")
            detail_data = detail_response.json()
            detail_recipe_items = detail_data.get('recipe_items', [])
            print(f"✅ Recipe items in detail: {len(detail_recipe_items)}")
            
            for item in detail_recipe_items:
                print(f"   - {item.get('ingredient_name')}: {item.get('quantity_required')} {item.get('ingredient_unit')}")
            
            print(f"✅ Shelf Life: {detail_data.get('shelf_life')} {detail_data.get('shelf_unit')}")
        else:
            print(f"❌ Error getting product: {detail_response.status_code}")
            print(detail_response.json())
    else:
        print(f"❌ Error creating product: {response.status_code}")
        print(json.dumps(response.json(), indent=2))

if __name__ == "__main__":
    test_api_flow()
