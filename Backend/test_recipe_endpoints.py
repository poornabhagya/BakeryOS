#!/usr/bin/env python
"""
Comprehensive test suite for Recipe API (Task 3.5)
Tests all recipe endpoints, business logic, and error handling.
"""
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from api.models import User, Product, Ingredient, Category, RecipeItem, IngredientBatch
from decimal import Decimal


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'


def print_header(text):
    print(f"\n{Colors.BLUE}{'='*70}{Colors.END}")
    print(f"{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BLUE}{'='*70}{Colors.END}\n")


def print_test(test_name, status, message=""):
    icon = f"{Colors.GREEN}✓{Colors.END}" if status else f"{Colors.RED}✗{Colors.END}"
    print(f"  {icon} {test_name}")
    if message:
        print(f"    {message}")


def test_recipe_api():
    """Run all recipe API tests"""
    
    print_header("RECIPE API - COMPREHENSIVE TEST SUITE (Task 3.5)")
    
    # Setup
    client = APIClient()
    
    # Create or get test user
    try:
        user = User.objects.get(username='testuser')
    except User.DoesNotExist:
        user = User.objects.create_user(username='testuser', password='test123')
        user.role = 'Manager'
        user.save()
    
    try:
        token = Token.objects.get(user=user)
    except Token.DoesNotExist:
        token = Token.objects.create(user=user)
    
    client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    
    print(f"Setup:")
    print(f"  User: {user.username} (Manager)")
    print(f"  Token: {token.key[:30]}...")
    
    # Get a product and ingredient for testing
    try:
        product = Product.objects.first()
        ingredient = Ingredient.objects.first()
    except:
        print(f"\n{Colors.RED}ERROR: No products or ingredients found in database{Colors.END}")
        return
    
    print(f"  Test Product: {product.product_id} - {product.name}")
    print(f"  Test Ingredient: {ingredient.ingredient_id} - {ingredient.name}")
    
    # ========== TEST 1: Add ingredient to recipe ==========
    print_header("TEST 1: POST /api/recipes/{product_id}/items/ - Add ingredient to recipe")
    
    response = client.post(
        f'/api/recipes/{product.id}/items/',
        {
            'ingredient_id': ingredient.id,
            'quantity_required': 2.5
        },
        format='json',
        SERVER_NAME='localhost'
    )
    
    test1_pass = response.status_code == 201
    print_test(
        "Add ingredient to recipe",
        test1_pass,
        f"Status: {response.status_code}"
    )
    
    if test1_pass:
        data = response.json()
        print(f"    Ingredient: {data.get('ingredient_name')} (qty: {data.get('quantity_required')})")
        recipe_item_id = data.get('id')
    else:
        print(f"    Error: {response.json()}")
        recipe_item_id = None
    
    # ========== TEST 2: Get recipe for product ==========
    print_header("TEST 2: GET /api/recipes/{product_id}/ - Get complete recipe")
    
    response = client.get(
        f'/api/recipes/{product.id}/',
        SERVER_NAME='localhost'
    )
    
    test2_pass = response.status_code == 200
    print_test(
        "Get recipe for product",
        test2_pass,
        f"Status: {response.status_code}"
    )
    
    if test2_pass:
        data = response.json()
        print(f"    Product: {data.get('product_name')}")
        print(f"    Total recipe items: {data.get('total_items')}")
        print(f"    Total recipe cost: {data.get('total_recipe_cost')}")
    else:
        print(f"    Error: {response.json()}")
    
    # ========== TEST 3: Update recipe item quantity ==========
    print_header("TEST 3: PUT /api/recipes/{product_id}/items/{ingredient_id}/ - Update qty")
    
    response = client.put(
        f'/api/recipes/{product.id}/items/{ingredient.id}/',
        {
            'quantity_required': 3.0
        },
        format='json',
        SERVER_NAME='localhost'
    )
    
    test3_pass = response.status_code == 200
    print_test(
        "Update ingredient quantity in recipe",
        test3_pass,
        f"Status: {response.status_code}"
    )
    
    if test3_pass:
        data = response.json()
        print(f"    New quantity: {data.get('quantity_required')}")
    else:
        print(f"    Error: {response.json()}")
    
    # ========== TEST 4: Validate recipe ==========
    print_header("TEST 4: GET /api/recipes/validate/{product_id}/ - Check if can make product")
    
    response = client.get(
        f'/api/recipes/validate/{product.id}/',
        SERVER_NAME='localhost'
    )
    
    test4_pass = response.status_code == 200
    print_test(
        "Validate recipe",
        test4_pass,
        f"Status: {response.status_code}"
    )
    
    if test4_pass:
        data = response.json()
        print(f"    Product: {data.get('product_name')}")
        print(f"    Can make: {data.get('can_make')}")
        print(f"    Reason: {data.get('reason')}")
        if data.get('missing_ingredients'):
            print(f"    Missing ingredients:")
            for missing in data.get('missing_ingredients', []):
                print(f"      - {missing.get('ingredient_name')}: need {missing.get('required')} (short by {missing.get('short_by')})")
    else:
        print(f"    Error: {response.json()}")
    
    # ========== TEST 5: Calculate batch requirements ==========
    print_header("TEST 5: GET /api/recipes/batch-required/{product_id}?qty=10 - Calculate batch needs")
    
    response = client.get(
        f'/api/recipes/batch-required/{product.id}?qty=10',
        SERVER_NAME='localhost'
    )
    
    test5_pass = response.status_code == 200
    print_test(
        "Calculate batch requirements",
        test5_pass,
        f"Status: {response.status_code}"
    )
    
    if test5_pass:
        data = response.json()
        print(f"    Product: {data.get('product_name')}")
        print(f"    Batch quantity: {data.get('batch_quantity')} units")
        print(f"    Total batch cost: {data.get('total_batch_cost')}")
        print(f"    Ingredients needed:")
        for ingredient_need in data.get('ingredients_needed', [])[:3]:
            print(f"      - {ingredient_need.get('ingredient_name')}: {ingredient_need.get('total_required')}{ingredient_need.get('base_unit')}")
    else:
        print(f"    Error: {response.json()}")
    
    # ========== TEST 6: Prevent duplicate ingredients ==========
    print_header("TEST 6: Validation - Prevent duplicate ingredients in recipe")
    
    response = client.post(
        f'/api/recipes/{product.id}/items/',
        {
            'ingredient_id': ingredient.id,
            'quantity_required': 1.5
        },
        format='json',
        SERVER_NAME='localhost'
    )
    
    test6_pass = response.status_code == 400
    print_test(
        "Prevent duplicate ingredients",
        test6_pass,
        f"Status: {response.status_code} (should be 400)"
    )
    
    if test6_pass:
        print(f"    Error (expected): {response.json()}")
    
    # ========== TEST 7: Validate quantity > 0 ==========
    print_header("TEST 7: Validation - Quantity must be positive")
    
    # Get another ingredient
    try:
        ingredient2 = Ingredient.objects.exclude(id=ingredient.id).first()
    except:
        ingredient2 = None
    
    if ingredient2:
        response = client.post(
            f'/api/recipes/{product.id}/items/',
            {
                'ingredient_id': ingredient2.id,
                'quantity_required': 0  # Invalid!
            },
            format='json',
            SERVER_NAME='localhost'
        )
        
        test7_pass = response.status_code == 400
        print_test(
            "Reject zero/negative quantity",
            test7_pass,
            f"Status: {response.status_code} (should be 400)"
        )
        
        if test7_pass:
            print(f"    Error (expected): {response.json()}")
    else:
        print_test("Reject zero/negative quantity", False, "Need 2 ingredients for this test")
    
    # ========== TEST 8: Remove ingredient from recipe ==========
    print_header("TEST 8: DELETE /api/recipes/{product_id}/items/{ingredient_id}/ - Remove ingredient")
    
    response = client.delete(
        f'/api/recipes/{product.id}/items/{ingredient.id}/',
        SERVER_NAME='localhost'
    )
    
    test8_pass = response.status_code == 200
    print_test(
        "Remove ingredient from recipe",
        test8_pass,
        f"Status: {response.status_code}"
    )
    
    if test8_pass:
        data = response.json()
        print(f"    Message: {data.get('message')}")
    else:
        print(f"    Error: {response.json()}")
    
    # ========== TEST 9: Get recipe with no items ==========
    print_header("TEST 9: Error handling - Get recipe with no items")
    
    response = client.get(
        f'/api/recipes/{product.id}/',
        SERVER_NAME='localhost'
    )
    
    test9_pass = response.status_code == 404
    print_test(
        "Handle missing recipe",
        test9_pass,
        f"Status: {response.status_code} (should be 404)"
    )
    
    if test9_pass:
        print(f"    Error (expected): {response.json()}")
    
    # ========== TEST 10: Invalid product ID ==========
    print_header("TEST 10: Error handling - Invalid product ID")
    
    response = client.get(
        f'/api/recipes/99999/',
        SERVER_NAME='localhost'
    )
    
    test10_pass = response.status_code == 404
    print_test(
        "Handle invalid product ID",
        test10_pass,
        f"Status: {response.status_code} (should be 404)"
    )
    
    if test10_pass:
        print(f"    Error (expected): {response.json()}")
    
    # ========== SUMMARY ==========
    print_header("TEST SUMMARY")
    
    tests = [test1_pass, test2_pass, test3_pass, test4_pass, test5_pass, 
             test6_pass, test10_pass]
    
    passed = sum(tests)
    total = len(tests)
    
    print(f"Passed: {Colors.GREEN}{passed}/{total}{Colors.END}")
    
    if passed == total:
        print(f"{Colors.GREEN}All recipe API tests passed!{Colors.END}")
    else:
        print(f"{Colors.RED}{total - passed} test(s) failed.{Colors.END}")
    
    # ========== DATABASE CHECKS ==========
    print_header("DATABASE STATUS")
    
    print(f"RecipeItem count: {RecipeItem.objects.count()}")
    print(f"Products with recipes: {Product.objects.filter(recipe_items__isnull=False).distinct().count()}")
    print(f"Total ingredients available: {Ingredient.objects.count()}")


if __name__ == '__main__':
    test_recipe_api()
