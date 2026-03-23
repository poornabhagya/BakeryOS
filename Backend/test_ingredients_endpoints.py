import os
import django
import json
import urllib.request
import urllib.error

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import User, Ingredient, Category
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
print("TASK 3.2 - INGREDIENT API ENDPOINTS TEST")
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
    print(f'  ✓ Created test user: {user.username}')
else:
    print(f'  ✓ Using existing test user: {user.username}')

# Get or create token
token, created = Token.objects.get_or_create(user=user)
HEADERS['Authorization'] = f'Token {token.key}'
print(f'  ✓ Token obtained: {token.key[:20]}...')

# Get ingredients from DB
ingredients = Ingredient.objects.all()
print(f'  ✓ Database has {ingredients.count()} ingredients')

print("\n" + "=" * 70)
print("TEST 1: GET /api/ingredients/ (List all ingredients)")
print("=" * 70)
try:
    status_code, data = make_request(f'{BASE_URL}/ingredients/')
    print(f"  Status Code: {status_code}")
    if status_code == 200:
        results = data.get('results', data) if isinstance(data, dict) else data
        result_count = len(results) if isinstance(results, list) else 1
        print(f"  ✓ SUCCESS - Retrieved {result_count} ingredients")
    else:
        print(f"  ✗ FAILED - {data}")
except Exception as e:
    print(f"  ✗ ERROR: {str(e)}")

print("\n" + "=" * 70)
print("TEST 2: GET /api/ingredients/?category_id=X (Filter by category)")
print("=" * 70)
try:
    flour_cat = Category.objects.filter(name='Flour').first()
    if flour_cat:
        status_code, data = make_request(f'{BASE_URL}/ingredients/?category_id={flour_cat.id}')
        print(f"  Status Code: {status_code}")
        if status_code == 200:
            results = data.get('results', data) if isinstance(data, dict) else data
            print(f"  ✓ SUCCESS - Retrieved {len(results)} Flour ingredients")
            for item in results[:2]:
                print(f"    - {item.get('ingredient_id')}: {item.get('name')}")
        else:
            print(f"  ✗ FAILED - {data}")
    else:
        print(f"  ⚠ Flour category not found")
except Exception as e:
    print(f"  ✗ ERROR: {str(e)}")

print("\n" + "=" * 70)
print("TEST 3: GET /api/ingredients/low_stock/ (Get low-stock items)")
print("=" * 70)
try:
    status_code, data = make_request(f'{BASE_URL}/ingredients/low_stock/')
    print(f"  Status Code: {status_code}")
    if status_code == 200:
        results = data.get('results', [])
        # Most will be low-stock since we set quantity to 0
        print(f"  ✓ SUCCESS - Found {len(results)} low-stock ingredients")
        if results:
            print(f"    - {results[0].get('ingredient_id')}: {results[0].get('name')} ({results[0].get('total_quantity')})")
    else:
        print(f"  ✗ FAILED - {data}")
except Exception as e:
    print(f"  ✗ ERROR: {str(e)}")

print("\n" + "=" * 70)
print("TEST 4: GET /api/ingredients/by_category/ (Grouped by category)")
print("=" * 70)
try:
    status_code, data = make_request(f'{BASE_URL}/ingredients/by_category/')
    print(f"  Status Code: {status_code}")
    if status_code == 200:
        if isinstance(data, list):
            print(f"  ✓ SUCCESS - Retrieved {len(data)} categories")
            for cat in data[:2]:
                print(f"    - {cat.get('category_name')}: {cat.get('count')} ingredients")
        else:
            print(f"  ✓ SUCCESS - Retrieved data")
    else:
        print(f"  ✗ FAILED - {data}")
except Exception as e:
    print(f"  ✗ ERROR: {str(e)}")

print("\n" + "=" * 70)
print("TEST 5: GET /api/ingredients/out_of_stock/ (Get out-of-stock)")
print("=" * 70)
try:
    status_code, data = make_request(f'{BASE_URL}/ingredients/out_of_stock/')
    print(f"  Status Code: {status_code}")
    if status_code == 200:
        results = data.get('results', [])
        # All seeders have 0 quantity initially
        print(f"  ✓ SUCCESS - Found {len(results)} out-of-stock ingredients")
    else:
        print(f"  ✗ FAILED - {data}")
except Exception as e:
    print(f"  ✗ ERROR: {str(e)}")

print("\n" + "=" * 70)
print("TEST 6: GET /api/ingredients/{id}/ (Retrieve single ingredient)")
print("=" * 70)
try:
    first_ing = Ingredient.objects.first()
    if first_ing:
        status_code, data = make_request(f'{BASE_URL}/ingredients/{first_ing.id}/')
        print(f"  Status Code: {status_code}")
        if status_code == 200:
            print(f"  ✓ SUCCESS - Retrieved ingredient details")
            print(f"    - ID: {data.get('id')}")
            print(f"    - Ingredient ID: {data.get('ingredient_id')}")
            print(f"    - Name: {data.get('name')}")
            print(f"    - Category: {data.get('category_name')}")
            print(f"    - Base Unit: {data.get('base_unit')}")
            print(f"    - Stock Status: {data.get('stock_status')}")
        else:
            print(f"  ✗ FAILED - {data}")
    else:
        print(f"  ✗ No ingredients in database")
except Exception as e:
    print(f"  ✗ ERROR: {str(e)}")

print("\n" + "=" * 70)
print("TEST 7: POST /api/ingredients/ (Create new ingredient)")
print("=" * 70)
try:
    # Get a category for testing
    dairy_cat = Category.objects.filter(name='Dairy').first()
    if dairy_cat:
        import uuid
        unique_name = f'Test Cream {uuid.uuid4().hex[:8]}'
        new_ingredient_data = {
            'name': unique_name,
            'category_id': dairy_cat.id,
            'supplier': 'Test Supplier',
            'supplier_contact': '0712345678',
            'tracking_type': 'Volume',
            'base_unit': 'liters',
            'low_stock_threshold': 5,
            'shelf_life': 14,
            'shelf_unit': 'days'
        }
        status_code, data = make_request(
            f'{BASE_URL}/ingredients/',
            method='POST',
            data=new_ingredient_data
        )
        print(f"  Status Code: {status_code}")
        if status_code in [201, 200]:
            print(f"  ✓ SUCCESS - Ingredient created")
            print(f"    - Ingredient ID: {data.get('ingredient_id')}")
            print(f"    - Name: {data.get('name')}")
            created_ing_id = data.get('id')
            
            print("\n" + "=" * 70)
            print("TEST 8: PATCH /api/ingredients/{id}/ (Update ingredient)")
            print("=" * 70)
            try:
                update_data = {
                    'low_stock_threshold': 10,
                    'supplier': 'Updated Supplier'
                }
                status_code, data = make_request(
                    f'{BASE_URL}/ingredients/{created_ing_id}/',
                    method='PATCH',
                    data=update_data
                )
                print(f"  Status Code: {status_code}")
                if status_code == 200:
                    print(f"  ✓ SUCCESS - Ingredient updated")
                    print(f"    - New supplier: {data.get('supplier')}")
                    print(f"    - New threshold: {data.get('low_stock_threshold')}")
                else:
                    print(f"  ✗ FAILED - {data}")
            except Exception as e:
                print(f"  ✗ ERROR: {str(e)}")
            
            print("\n" + "=" * 70)
            print("TEST 9: DELETE /api/ingredients/{id}/ (Soft delete ingredient)")
            print("=" * 70)
            try:
                status_code, data = make_request(
                    f'{BASE_URL}/ingredients/{created_ing_id}/',
                    method='DELETE'
                )
                print(f"  Status Code: {status_code}")
                if status_code in [200]:
                    print(f"  ✓ SUCCESS - Ingredient soft deleted")
                    print(f"    - Message: {data.get('message')}")
                else:
                    print(f"  ✗ FAILED - {data}")
            except Exception as e:
                print(f"  ✗ ERROR: {str(e)}")
        else:
            print(f"  ✗ FAILED - {data}")
    else:
        print(f"  ⚠ Dairy category not found")
except Exception as e:
    print(f"  ✗ ERROR: {str(e)}")

print("\n" + "=" * 70)
print("TEST 10: Search functionality")
print("=" * 70)
try:
    status_code, data = make_request(f'{BASE_URL}/ingredients/?search=Flour')
    print(f"  Status Code: {status_code}")
    if status_code == 200:
        results = data.get('results', data) if isinstance(data, dict) else data
        print(f"  ✓ SUCCESS - Found {len(results)} ingredients matching 'Flour'")
        for item in results[:2]:
            print(f"    - {item.get('ingredient_id')}: {item.get('name')}")
    else:
        print(f"  ✗ FAILED - {data}")
except Exception as e:
    print(f"  ✗ ERROR: {str(e)}")

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
total_ings = Ingredient.objects.count()
by_category = Ingredient.objects.values('category_id__name').distinct().count()
low_stock = Ingredient.objects.filter(total_quantity__lt=django.db.models.F('low_stock_threshold')).count()

print(f"  Total Ingredients: {total_ings}")
print(f"  Categories: {by_category}")
print(f"  Low Stock Items: {low_stock}")
print(f"\n  Server: http://localhost:8000")
print(f"  API Base URL: {BASE_URL}")
print(f"  Test User: testuser")
print(f"  Token: {HEADERS['Authorization']}")
print("\n" + "=" * 70)
