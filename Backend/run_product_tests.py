#!/usr/bin/env python
"""Task 3.4 - Product API Comprehensive Tests"""

import subprocess
import time
import requests
import json
from decimal import Decimal

# Configuration
BASE_URL = "http://localhost:8000/api"
OTHER_TOKEN = "bd616d5e8bd9e45e61e40721c043b7f0edeb6b6d"  # testuser token

print("\n" + "=" * 80)
print("TASK 3.4 - PRODUCT API ENDPOINTS TEST".center(80))
print("=" * 80 + "\n")

# First, check if server is running
print("Checking server status...")
for i in range(5):
    try:
        response = requests.get(f"{BASE_URL}/categories/", headers={'Authorization': f'Token {OTHER_TOKEN}'}, timeout=2)
        if response.status_code in [200, 401, 403]:
            print("✓ Server is running\n")
            break
    except:
        if i < 4:
            print(f"  Waiting for server... ({i+1}/5)")
            time.sleep(2)
        else:
            print("✗ Server is not responding!")
            exit(1)

# Get or create test category
print("Setting up test data...")
categories_response = requests.get(
    f"{BASE_URL}/categories/?type=Product",
    headers={'Authorization': f'Token {OTHER_TOKEN}'}
)

test_category_id = None
if categories_response.status_code == 200:
    categories = categories_response.json()
    if isinstance(categories, dict) and 'results' in categories:
        if categories['results']:
            test_category_id = categories['results'][0]['id']
            print(f"✓ Using category: {categories['results'][0]['name']} (ID: {test_category_id})")

if not test_category_id:
    print("✗ No Product categories found!")
    exit(1)

# Test counters
tests_passed = 0
tests_failed = 0

def test_endpoint(name, method, endpoint, data=None, expected_status=200, method_name=""):
    """Generic test function"""
    global tests_passed, tests_failed
    
    url = f"{BASE_URL}{endpoint}"
    headers = {'Authorization': f'Token {OTHER_TOKEN}', 'Content-Type': 'application/json'}
    
    try:
        if method == 'GET':
            response = requests.get(url, headers=headers, timeout=5)
        elif method == 'POST':
            response = requests.post(url, headers=headers, json=data, timeout=5)
        elif method == 'PATCH':
            response = requests.patch(url, headers=headers, json=data, timeout=5)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers, timeout=5)
        else:
            response = None
        
        if response and response.status_code == expected_status:
            print(f"✓ {name}")
            print(f"  {method} {endpoint} -> {response.status_code}")
            tests_passed += 1
            return response
        else:
            print(f"✗ {name}")
            print(f"  {method} {endpoint} -> {response.status_code if response else 'No response'}")
            if response:
                try:
                    print(f"  Response: {response.json()}")
                except:
                    print(f"  Response: {response.text[:200]}")
            tests_failed += 1
            return None
    except Exception as e:
        print(f"✗ {name}")
        print(f"  Error: {str(e)}")
        tests_failed += 1
        return None

# ==================== TESTS ====================

print("\n" + "-" * 80)
print("TEST GROUP 1: List & Filter Products")
print("-" * 80)

test_endpoint(
    "GET /api/products/ - List all products",
    "GET", "/products/", expected_status=200
)

test_endpoint(
    f"GET /api/products/?category_id={test_category_id} - Filter by category",
    "GET", f"/products/?category_id={test_category_id}", expected_status=200
)

print("\n" + "-" * 80)
print("TEST GROUP 2: Create Products")
print("-" * 80)

product_data = {
    "category_id": test_category_id,
    "name": "Test Product " + str(int(time.time())),
    "description": "A test product for API validation",
    "cost_price": "2.50",
    "selling_price": "5.00",
    "current_stock": "100",
    "shelf_life": 2,
    "shelf_unit": "days"
}

create_response = test_endpoint(
    "POST /api/products/ - Create new product",
    "POST", "/products/", data=product_data, expected_status=201
)

product_id = None
if create_response:
    try:
        product_id = create_response.json()['id']
        product_obj = create_response.json()
        print(f"  Product ID: {product_obj.get('product_id', '?')}")
        print(f"  Profit Margin: {product_obj.get('profit_margin', '?')}%")
    except:
        pass

print("\n" + "-" * 80)
print("TEST GROUP 3: Get Product Details")
print("-" * 80)

if product_id:
    response = test_endpoint(
        f"GET /api/products/{product_id}/ - Get product details",
        "GET", f"/products/{product_id}/", expected_status=200
    )
    
    if response:
        try:
            data = response.json()
            print(f"  Status: {data.get('status', '?')}")
            print(f"  Low Stock: {data.get('is_low_stock', '?')}")
            print(f"  Out of Stock: {data.get('is_out_of_stock', '?')}")
        except:
            pass

print("\n" + "-" * 80)
print("TEST GROUP 4: Update Product")
print("-" * 80)

if product_id:
    update_data = {
        "current_stock": "50",
        "selling_price": "6.00"
    }
    
    test_endpoint(
        f"PATCH /api/products/{product_id}/ - Update product",
        "PATCH", f"/products/{product_id}/", data=update_data, expected_status=200
    )

print("\n" + "-" * 80)
print("TEST GROUP 5: Custom Endpoints")
print("-" * 80)

test_endpoint(
    "GET /api/products/low-stock/ - Get low-stock products",
    "GET", "/products/low_stock/", expected_status=200
)

test_endpoint(
    "GET /api/products/out-of-stock/ - Get out-of-stock products",
    "GET", "/products/out_of_stock/", expected_status=200
)

test_endpoint(
    f"GET /api/products/by-category/{test_category_id}/ - Get products by category",
    "GET", f"/products/by_category/{test_category_id}/", expected_status=200
)

print("\n" + "-" * 80)
print("TEST GROUP 6: Search & Filter")
print("-" * 80)

test_endpoint(
    "GET /api/products/?search=test - Search products",
    "GET", "/products/?search=test", expected_status=200
)

print("\n" + "-" * 80)
print("TEST GROUP 7: Validation")
print("-" * 80)

# Test: selling_price <= cost_price
invalid_data = {
    "category_id": test_category_id,
    "name": "Invalid Product " + str(int(time.time())),
    "cost_price": "5.00",
    "selling_price": "3.00",  # Lower than cost
    "current_stock": "10"
}

test_endpoint(
    "POST /api/products/ - Reject selling_price <= cost_price",
    "POST", "/products/", data=invalid_data, expected_status=400
)

# Test: Duplicate name in category
if product_id:
    duplicate_data = {
        "category_id": test_category_id,
        "name": product_data["name"],  # Same name as created product
        "cost_price": "2.50",
        "selling_price": "5.00",
        "current_stock": "10"
    }
    
    test_endpoint(
        "POST /api/products/ - Reject duplicate name in category",
        "POST", "/products/", data=duplicate_data, expected_status=400
    )

print("\n" + "-" * 80)
print("TEST GROUP 8: Delete Product")
print("-" * 80)

if product_id:
    test_endpoint(
        f"DELETE /api/products/{product_id}/ - Delete product",
        "DELETE", f"/products/{product_id}/", expected_status=204
    )

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

if tests_failed == 0:
    print("\n✓ All tests passed! Product API is working correctly.")
else:
    print(f"\n⚠ {tests_failed} test(s) failed. Please review the implementation.")

print("\n" + "=" * 80)
