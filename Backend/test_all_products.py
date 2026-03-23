#!/usr/bin/env python
"""
Task 3.4 - Product API Comprehensive Test Suite
Tests all endpoints after migration and seed data
"""
import os
import sys
import django
import time
import requests
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.core.management import call_command
from django.db import connection
from api.models import Product, Category, User

print("=" * 80)
print("TASK 3.4 - PRODUCT API COMPREHENSIVE TEST SUITE".center(80))
print("=" * 80)

# ==================== STEP 1: CHECK & APPLY MIGRATIONS ====================
print("\n[STEP 1] Checking database schema...")
with connection.cursor() as cursor:
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='api_product'
    """)
    table_exists = cursor.fetchone() is not None

if not table_exists:
    print("  ⚠ Product table not found - applying migrations...")
    call_command('migrate', verbosity=0)
    print("  ✓ Migrations applied")
else:
    print("  ✓ Product table exists")

# ==================== STEP 2: LOAD SEED DATA ====================
print("\n[STEP 2] Loading seed data...")
product_count = Product.objects.count()

if product_count == 0:
    print("  ⚠ No products found - loading seed data...")
    try:
        call_command('seed_products', verbosity=0)
        product_count = Product.objects.count()
        print(f"  ✓ Loaded {product_count} products")
    except Exception as e:
        print(f"  Note: seed_products command not available ({str(e)[:50]}...)")
        print("  Creating test products manually...")
        
        # Create categories
        categories = {
            'Buns': Category.objects.get_or_create(name='Buns', type='Product', defaults={'description': 'Bakery buns'})[0],
            'Bread': Category.objects.get_or_create(name='Bread', type='Product', defaults={'description': 'Bread items'})[0],
        }
        
        # Create test products
        products_data = [
            ('Burger Bun', 'Buns', 15.00, 25.00, 50),
            ('Hot Dog Bun', 'Buns', 12.00, 20.00, 45),
            ('White Bread', 'Bread', 75.00, 120.00, 30),
            ('Brown Bread', 'Bread', 80.00, 130.00, 25),
        ]
        
        for name, cat_name, cost, selling, stock in products_data:
            Product.objects.create(
                category_id=categories[cat_name],
                name=name,
                cost_price=Decimal(str(cost)),
                selling_price=Decimal(str(selling)),
                current_stock=Decimal(str(stock)),
                shelf_life=2,
                shelf_unit='days'
            )
        
        product_count = Product.objects.count()
        print(f"  ✓ Created {product_count} test products")
else:
    print(f"  ✓ {product_count} products already loaded")

# ==================== STEP 3: GET TEST TOKEN ====================
print("\n[STEP 3] Getting test authentication token...")
test_user = User.objects.filter(username='testuser').first()
if not test_user:
    print("  ⚠ testuser not found")
    test_token = "NO_TOKEN"
else:
    from rest_framework.authtoken.models import Token
    token, _ = Token.objects.get_or_create(user=test_user)
    test_token = str(token)
    print(f"  ✓ Token: {test_token[:20]}...")

# ==================== STEP 4: TEST ENDPOINTS ====================
print("\n[STEP 4] Testing all endpoints...")
print("  Waiting for server to be ready...")
time.sleep(3)

BASE_URL = "http://localhost:8000/api"
HEADERS = {'Authorization': f'Token {test_token}'}

tests_passed = 0
tests_failed = 0

def test_endpoint(name, method, endpoint, data=None, expected_status=200):
    """Generic endpoint test"""
    global tests_passed, tests_failed
    
    url = f"{BASE_URL}{endpoint}"
    try:
        if method == 'GET':
            response = requests.get(url, headers=HEADERS, timeout=5)
        elif method == 'POST':
            response = requests.post(url, headers=HEADERS, json=data, timeout=5)
        elif method == 'PATCH':
            response = requests.patch(url, headers=HEADERS, json=data, timeout=5)
        elif method == 'DELETE':
            response = requests.delete(url, headers=HEADERS, timeout=5)
        
        if response.status_code == expected_status:
            print(f"  ✓ {name}")
            print(f"    {method} {endpoint} → {response.status_code}")
            tests_passed += 1
            return response
        else:
            print(f"  ✗ {name}")
            print(f"    {method} {endpoint} → {response.status_code} (expected {expected_status})")
            try:
                print(f"    Response: {response.json()}")
            except:
                print(f"    Response: {response.text[:100]}")
            tests_failed += 1
            return None
    except Exception as e:
        print(f"  ✗ {name}")
        print(f"    Error: {str(e)[:60]}")
        tests_failed += 1
        return None

# Test Group 1: List Endpoints
print("\n  [GROUP 1] List & Filter")
test_endpoint("List all products", "GET", "/products/", expected_status=200)
test_endpoint("Filter by category", "GET", "/products/?category_id=1", expected_status=200)
test_endpoint("Filter by status", "GET", "/products/?status=available", expected_status=200)
test_endpoint("Search products", "GET", "/products/?search=Bread", expected_status=200)
test_endpoint("Low-stock products", "GET", "/products/low_stock/", expected_status=200)
test_endpoint("Out-of-stock products", "GET", "/products/out_of_stock/", expected_status=200)

# Test Group 2: Detail Endpoint
print("\n  [GROUP 2] Product Details")
if product_count > 0:
    test_endpoint("Get product detail (ID=1)", "GET", "/products/1/", expected_status=200)

# Test Group 3: Create
print("\n  [GROUP 3] Create Product")
new_product = {
    "category_id": 1,
    "name": f"Test Product {int(time.time())}",
    "cost_price": "20.00",
    "selling_price": "40.00",
    "current_stock": "25",
    "shelf_life": 2,
    "shelf_unit": "days"
}
create_response = test_endpoint("Create product", "POST", "/products/", data=new_product, expected_status=201)

# Get product ID for update/delete tests
product_id_for_testing = None
if create_response:
    try:
        product_id_for_testing = create_response.json().get('id')
    except:
        pass

# Test Group 4: Update
print("\n  [GROUP 4] Update Product")
if product_id_for_testing:
    update_data = {"current_stock": "35"}
    test_endpoint(f"Update product (ID={product_id_for_testing})", "PATCH", 
                 f"/products/{product_id_for_testing}/", data=update_data, expected_status=200)

# Test Group 5: Delete
print("\n  [GROUP 5] Delete Product")
if product_id_for_testing:
    test_endpoint(f"Delete product (ID={product_id_for_testing})", "DELETE", 
                 f"/products/{product_id_for_testing}/", expected_status=204)

# Test Group 6: By Category
print("\n  [GROUP 6] By Category")
if product_count > 0:
    test_endpoint("Products by category (ID=1)", "GET", "/products/by_category/1/", expected_status=200)

# ==================== STEP 5: VALIDATION TESTS ====================
print("\n[STEP 5] Validation tests...")

# Test invalid price
print("\n  [VALIDATION] Invalid selling_price")
invalid_data = {
    "category_id": 1,
    "name": f"Invalid Product {int(time.time())}",
    "cost_price": "50.00",
    "selling_price": "30.00",  # Less than cost
    "shelf_life": 2,
    "shelf_unit": "days"
}
response = test_endpoint("Reject selling_price < cost_price", "POST", "/products/", 
                        data=invalid_data, expected_status=400)

# ==================== SUMMARY ====================
print("\n" + "=" * 80)
print("TEST SUMMARY".center(80))
print("=" * 80)

total_tests = tests_passed + tests_failed
success_rate = (tests_passed / total_tests * 100) if total_tests > 0 else 0

print(f"\nTotal Tests: {total_tests}")
print(f"Passed: {tests_passed} ✓")
print(f"Failed: {tests_failed} ✗")
print(f"Success Rate: {success_rate:.1f}%")

# Database Summary
print(f"\nDatabase Summary:")
print(f"  Total Products: {Product.objects.count()}")
print(f"  Total Categories: {Category.objects.filter(type='Product').count()}")

# Product List
print(f"\nProducts in Database:")
for p in Product.objects.all()[:5]:
    print(f"  - {p.product_id}: {p.name} (Rs. {p.selling_price}, Status: {p.status})")
if Product.objects.count() > 5:
    print(f"  ... and {Product.objects.count() - 5} more")

print("\n" + "=" * 80)
if tests_failed == 0:
    print("✅ ALL TESTS PASSED - Product API is fully functional!".center(80))
else:
    print(f"⚠️  {tests_failed} test(s) failed - please review errors above".center(80))
print("=" * 80 + "\n")
