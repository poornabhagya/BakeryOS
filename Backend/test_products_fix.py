#!/usr/bin/env python
import os
import sys
import django
from django.test.utils import get_runner
from django.conf import settings

# Add the project to path
sys.path.insert(0, os.path.dirname(__file__))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Now test the API
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User


def test_product_api():
    """Test the Product API endpoints"""
    client = APIClient()
    
    # Get or create test user and token
    try:
        user = User.objects.get(username='testuser')
        token = Token.objects.get(user=user)
    except:
        user = User.objects.create_user(username='testuser', password='test123')
        user.role = 'Manager'
        user.save()
        token = Token.objects.create(user=user)
    
    # Set authentication
    client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
    
    # Test 1: GET /api/products/
    print("TEST 1: GET /api/products/ (List all products)")
    print("=" * 60)
    response = client.get('/api/products/')
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✓ SUCCESS - Retrieved {len(data) if isinstance(data, list) else data.get('count', 'N/A')} products")
        if isinstance(data, list):
            if data:
                print(f"Sample product: {data[0]}")
        else:
            if data.get('results'):
                print(f"Sample product: {data['results'][0]}")
    else:
        print(f"✗ FAILED - {response.json()}")
    
    print("\n")
    
    # Test 2: Filter by category
    print("TEST 2: GET /api/products/?category_id=1 (Filter by category)")
    print("=" * 60)
    response = client.get('/api/products/?category_id=1')
    print(f"Status Code: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        count = len(data) if isinstance(data, list) else data.get('count', 0)
        print(f"✓ SUCCESS - Found {count} products in category 1")
    else:
        print(f"✗ FAILED - {response.json()}")


if __name__ == '__main__':
    test_product_api()
