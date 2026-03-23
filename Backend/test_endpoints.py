import os
import django
import json
import urllib.request
import urllib.error

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import User, Category
from rest_framework.authtoken.models import Token

BASE_URL = 'http://localhost:8000/api'
HEADERS = {
    'Content-Type': 'application/json',
}

def make_request(url, method='GET', data=None, headers=None):
    """Helper function to make HTTP requests"""
    if headers is None:
        headers = HEADERS.copy()
    else:
        headers = {**HEADERS, **headers}
    
    if data:
        data = json.dumps(data).encode('utf-8')
    
    try:
        req = urllib.request.Request(url, data=data, headers=headers, method=method)
        with urllib.request.urlopen(req) as response:
            body = response.read().decode('utf-8')
            return response.status, json.loads(body) if body else None
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8')
        try:
            return e.code, json.loads(body)
        except:
            return e.code, body

print("=" * 70)
print("TASK 3.1 - CATEGORY API ENDPOINTS TEST")
print("=" * 70)

# Create or get test user
print("\n[SETUP] Creating test user...")
user, created = User.objects.get_or_create(
    username='testuser',
    defaults={
        'email': 'test@example.com',
        'full_name': 'Test User',
        'role': 'Manager',
        'is_staff': True,
        'is_superuser': True,
    }
)
if created:
    user.set_password('testpass123')
    user.save()
    print(f'  ✓ Created test user: {user.username} (Role: {user.role})')
else:
    print(f'  ✓ Using existing test user: {user.username} (Role: {user.role})')

# Get or create token
token, created = Token.objects.get_or_create(user=user)
HEADERS['Authorization'] = f'Token {token.key}'
print(f'  ✓ Token obtained: {token.key[:20]}...')

# Get categories from DB
categories = Category.objects.all()
print(f'  ✓ Database has {categories.count()} categories')

print("\n" + "=" * 70)
print("TEST 1: GET /api/categories/ (List all categories)")
print("=" * 70)
try:
    status_code, data = make_request(f'{BASE_URL}/categories/')
    print(f"  Status Code: {status_code}")
    if status_code == 200:
        results = data.get('results', data) if isinstance(data, dict) else data
        result_count = len(results) if isinstance(results, list) else 1
        print(f"  ✓ SUCCESS - Retrieved {result_count} categories")
    else:
        print(f"  ✗ FAILED - {data}")
except Exception as e:
    print(f"  ✗ ERROR: {str(e)}")

print("\n" + "=" * 70)
print("TEST 2: GET /api/categories/?type=Product (Filter by type)")
print("=" * 70)
try:
    status_code, data = make_request(f'{BASE_URL}/categories/?type=Product')
    print(f"  Status Code: {status_code}")
    if status_code == 200:
        products = data.get('results', data) if isinstance(data, dict) else data
        print(f"  ✓ SUCCESS - Retrieved {len(products)} product categories")
        for item in products[:3]:
            print(f"    - {item.get('category_id')}: {item.get('name')}")
    else:
        print(f"  ✗ FAILED - {data}")
except Exception as e:
    print(f"  ✗ ERROR: {str(e)}")

print("\n" + "=" * 70)
print("TEST 3: GET /api/categories/?type=Ingredient (Filter by type)")
print("=" * 70)
try:
    status_code, data = make_request(f'{BASE_URL}/categories/?type=Ingredient')
    print(f"  Status Code: {status_code}")
    if status_code == 200:
        ingredients = data.get('results', data) if isinstance(data, dict) else data
        print(f"  ✓ SUCCESS - Retrieved {len(ingredients)} ingredient categories")
        for item in ingredients[:3]:
            print(f"    - {item.get('category_id')}: {item.get('name')}")
    else:
        print(f"  ✗ FAILED - {data}")
except Exception as e:
    print(f"  ✗ ERROR: {str(e)}")

print("\n" + "=" * 70)
print("TEST 4: GET /api/categories/products/ (Custom action - products)")
print("=" * 70)
try:
    status_code, data = make_request(f'{BASE_URL}/categories/products/')
    print(f"  Status Code: {status_code}")
    if status_code == 200:
        products = data if isinstance(data, list) else data.get('results', data)
        print(f"  ✓ SUCCESS - Retrieved {len(products)} product categories")
        for item in products:
            print(f"    - {item.get('category_id')}: {item.get('name')}")
    else:
        print(f"  ✗ FAILED - {data}")
except Exception as e:
    print(f"  ✗ ERROR: {str(e)}")

print("\n" + "=" * 70)
print("TEST 5: GET /api/categories/ingredients/ (Custom action - ingredients)")
print("=" * 70)
try:
    status_code, data = make_request(f'{BASE_URL}/categories/ingredients/')
    print(f"  Status Code: {status_code}")
    if status_code == 200:
        ingredients = data if isinstance(data, list) else data.get('results', data)
        print(f"  ✓ SUCCESS - Retrieved {len(ingredients)} ingredient categories")
        for item in ingredients:
            print(f"    - {item.get('category_id')}: {item.get('name')}")
    else:
        print(f"  ✗ FAILED - {data}")
except Exception as e:
    print(f"  ✗ ERROR: {str(e)}")

print("\n" + "=" * 70)
print("TEST 6: GET /api/categories/{id}/ (Retrieve single category)")
print("=" * 70)
try:
    first_cat = Category.objects.first()
    if first_cat:
        status_code, data = make_request(f'{BASE_URL}/categories/{first_cat.id}/')
        print(f"  Status Code: {status_code}")
        if status_code == 200:
            print(f"  ✓ SUCCESS - Retrieved category details")
            print(f"    - ID: {data.get('id')}")
            print(f"    - Category ID: {data.get('category_id')}")
            print(f"    - Name: {data.get('name')}")
            print(f"    - Type: {data.get('type')}")
        else:
            print(f"  ✗ FAILED - {data}")
    else:
        print(f"  ✗ No categories in database to test retrieve")
except Exception as e:
    print(f"  ✗ ERROR: {str(e)}")

print("\n" + "=" * 70)
print("TEST 7: POST /api/categories/ (Create new category)")
print("=" * 70)
created_cat_id = None
try:
    new_category_data = {
        'name': 'Test Category',
        'type': 'Product',
        'description': 'This is a test category'
    }
    status_code, data = make_request(
        f'{BASE_URL}/categories/',
        method='POST',
        data=new_category_data
    )
    print(f"  Status Code: {status_code}")
    if status_code in [201, 200]:
        print(f"  ✓ SUCCESS - Category created")
        print(f"    - Category ID: {data.get('category_id')}")
        print(f"    - Name: {data.get('name')}")
        created_cat_id = data.get('id')
    else:
        print(f"  ✗ FAILED - {data}")
except Exception as e:
    print(f"  ✗ ERROR: {str(e)}")

if created_cat_id:
    print("\n" + "=" * 70)
    print("TEST 8: PATCH /api/categories/{id}/ (Update category)")
    print("=" * 70)
    try:
        update_data = {
            'description': 'Updated description for test category'
        }
        status_code, data = make_request(
            f'{BASE_URL}/categories/{created_cat_id}/',
            method='PATCH',
            data=update_data
        )
        print(f"  Status Code: {status_code}")
        if status_code == 200:
            print(f"  ✓ SUCCESS - Category updated")
            print(f"    - New description: {data.get('description')}")
        else:
            print(f"  ✗ FAILED - {data}")
    except Exception as e:
        print(f"  ✗ ERROR: {str(e)}")

    print("\n" + "=" * 70)
    print("TEST 9: DELETE /api/categories/{id}/ (Delete category)")
    print("=" * 70)
    try:
        status_code, data = make_request(
            f'{BASE_URL}/categories/{created_cat_id}/',
            method='DELETE'
        )
        print(f"  Status Code: {status_code}")
        if status_code in [204, 200]:
            print(f"  ✓ SUCCESS - Category deleted")
        else:
            print(f"  ✗ FAILED - {data}")
    except Exception as e:
        print(f"  ✗ ERROR: {str(e)}")

print("\n" + "=" * 70)
print("TEST 10: Search functionality")
print("=" * 70)
try:
    status_code, data = make_request(f'{BASE_URL}/categories/?search=Bread')
    print(f"  Status Code: {status_code}")
    if status_code == 200:
        results = data.get('results', data) if isinstance(data, dict) else data
        print(f"  ✓ SUCCESS - Found {len(results)} categories matching 'Bread'")
        for item in results:
            print(f"    - {item.get('category_id')}: {item.get('name')}")
    else:
        print(f"  ✗ FAILED - {data}")
except Exception as e:
    print(f"  ✗ ERROR: {str(e)}")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
total_cats = Category.objects.count()
product_cats = Category.objects.filter(type='Product').count()
ingredient_cats = Category.objects.filter(type='Ingredient').count()
print(f"  Total Categories in Database: {total_cats}")
print(f"  Product Categories: {product_cats}")
print(f"  Ingredient Categories: {ingredient_cats}")
print(f"\n  Server: http://localhost:8000")
print(f"  API Base URL: {BASE_URL}")
print(f"  Test User: testuser")
print(f"  Token: {HEADERS['Authorization']}")
print("\n" + "=" * 70)
