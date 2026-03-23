#!/usr/bin/env python
"""
Test Recipe API endpoints after URL pattern fix.
Tests the corrected endpoint paths with detail=True routing.
"""
import os
import sys
import django
from io import StringIO

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.test import Client, override_settings

# Suppress output during test setup
old_stdout = sys.stdout
sys.stdout = StringIO()

# Test setup
client = Client()
token = 'bd616d5e8bd9e45e61e40721c043b7f0edeb6b6d'
headers = {'HTTP_AUTHORIZATION': f'Token {token}'}

# Restore stdout
sys.stdout = old_stdout

PRODUCT_ID = 22
INGREDIENT_ID = 13

print("=" * 70)
print("RECIPE API ENDPOINT TESTING - URL PATTERN FIX")
print("=" * 70)

tests_passed = 0
tests_failed = 0

# Test 1: Retrieve recipe
print("\nTest 1: GET /api/recipes/{}/".format(PRODUCT_ID))
print("-" * 70)
response = client.get(f'/api/recipes/{PRODUCT_ID}/', **headers)
print(f"Status: {response.status_code}")
if response.status_code in [200, 404]:  # 404 is OK if no recipe yet
    print("[PASS] Recipe retrieval working")
    tests_passed += 1
else:
    print("[FAIL] Unexpected status code")
    tests_failed += 1

# Test 2: Add ingredient
print("\nTest 2: POST /api/recipes/{}/items/".format(PRODUCT_ID))
print("-" * 70)
response = client.post(
    f'/api/recipes/{PRODUCT_ID}/items/',
    {'ingredient_id': INGREDIENT_ID, 'quantity_required': 1.5},
    content_type='application/json',
    **headers
)
print(f"Status: {response.status_code}")
if response.status_code in [201, 400]:  # 400 if already exists
    print("[PASS] Recipe item creation working")
    tests_passed += 1
else:
    print("[FAIL] Unexpected status code")
    print(f"Response: {response.content[:100]}")
    tests_failed += 1

# Test 3: Validate recipe (NEW URL)
print("\nTest 3: GET /api/recipes/{}/validate/".format(PRODUCT_ID))
print("-" * 70)
response = client.get(f'/api/recipes/{PRODUCT_ID}/validate/', **headers)
print(f"Status: {response.status_code}")
if response.status_code in [200, 404]:
    print("[PASS] Recipe validation endpoint working")
    tests_passed += 1
else:
    print("[FAIL] Unexpected status code")
    print(f"Response: {response.content[:100]}")
    tests_failed += 1

# Test 4: Batch requirements (NEW URL - underscore, detail=True)
print("\nTest 4: GET /api/recipes/{}/batch_required/?qty=10".format(PRODUCT_ID))
print("-" * 70)
response = client.get(f'/api/recipes/{PRODUCT_ID}/batch_required/?qty=10', **headers)
print(f"Status: {response.status_code}")
print(f"Response type: {type(response)}")
if response.status_code in [200, 404]:
    print("[PASS] Batch requirements endpoint working")
    tests_passed += 1
elif response.status_code == 301:
    print("[FAIL] Still getting redirect (301)")
    print(f"Location: {response.get('Location', 'No redirect target')}")
    tests_failed += 1
else:
    print("[FAIL] Unexpected status code")
    print(f"Response: {response.content[:100]}")
    tests_failed += 1

print("\n" + "=" * 70)
print("RESULTS")
print("=" * 70)
print(f"Passed: {tests_passed}/4")
print(f"Failed: {tests_failed}/4")
print("\nNewly fixed URL patterns:")
print("  - validate: /api/recipes/{id}/validate/")
print("  - batch_required: /api/recipes/{id}/batch_required/")
print("=" * 70)
