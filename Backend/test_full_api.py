#!/usr/bin/env python
import os
import sys
import django

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from api.models import Product

print("=" * 70)
print("PRODUCT API TEST - After Fixes")  
print("=" * 70)

# Create test client
client = APIClient()

# Get or create test user
try:
    user = User.objects.get(username='testuser')
    token = Token.objects.get(user=user)
    print(f"✓ Using existing test user: {user.username}")
except:
    user = User.objects.create_user(username='testuser', password='test123')
    user.role = 'Manager'
    user.save()
    token = Token.objects.create(user=user)
    print(f"✓ Created test user: {user.username}")

print(f"✓ Token: {token.key[:20]}...")

# Set authentication
client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

# Test 1: GET /api/products/
print("\n[TEST 1] GET /api/products/ - List all products")
print("-" * 70)
response = client.get('/api/products/')
print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    if isinstance(data, list):
        count = len(data)
        print(f"✓ SUCCESS - Retrieved {count} products")
        if count > 0:
            print(f"  Sample product: {data[0]}")
    else:
        count = data.get('count', len(data.get('results', [])))
        print(f"✓ SUCCESS - Retrieved {count} products")
        if data.get('results'):
            print(f"  Sample product: {data['results'][0]}")
else:
    print(f"✗ FAILED - {response.json()}")

# Test 2: Product count in database
print("\n[TEST 2] Database Product Count")
print("-" * 70)
count_in_db = Product.objects.count()
print(f"Total products in database: {count_in_db}")

# Test 3: Filter by category
print("\n[TEST 3] GET /api/products/?category_id=1 - Filter by category")
print("-" * 70)
response = client.get('/api/products/?category_id=1')
print(f"Status Code: {response.status_code}")
if response.status_code == 200:
    data = response.json()
    if isinstance(data, list):
        count = len(data)
    else:
        count = data.get('count', 0)
    print(f"✓ SUCCESS - Found {count} products in category 1")
else:
    print(f"✗ FAILED - {response.json()}")

# Test 4: Check for any obvious errors
print("\n[TEST 4] Check Database and API Configuration")
print("-" * 70)
print(f"Products in DB: {Product.objects.count()}")
print(f"First product: {Product.objects.first()}")
print(f"Sample query: {list(Product.objects.values_list('product_id', 'name')[:3])}")

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
