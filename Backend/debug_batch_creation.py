import os
import django
import requests
from decimal import Decimal
from datetime import date

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import User, Category, Product
from rest_framework.authtoken.models import Token

# Get baker user
baker = User.objects.get(username='baker1')
print(f"Baker user: {baker.username}, Role: {baker.role}")

# Get or create token
token, created = Token.objects.get_or_create(user=baker)
print(f"Token: {token.key}")
print(f"Token created: {created}")

# Get a product
products = Product.objects.all()
if products:
    product = products.first()
    print(f"\nProduct: {product.id} - {product.name}")
else:
    print("\nNo products available!")
    exit(1)

# Test API endpoint
print("\n" + "="*60)
print("Testing Product Batch Creation")
print("="*60)

BASE_URL = "http://localhost:8000/api"

headers = {
    'Authorization': f'Token {token.key}',
    'Content-Type': 'application/json'
}

payload = {
    'product_id': product.id,
    'quantity': '10.00',
    'made_date': date.today().isoformat(),
    'notes': 'Test batch'
}

print(f"\nRequest URL: POST {BASE_URL}/product-batches/")
print(f"Headers: {headers}")
print(f"Payload: {payload}")

response = requests.post(
    f"{BASE_URL}/product-batches/",
    json=payload,
    headers=headers
)

print(f"\nResponse Status: {response.status_code}")
print(f"Response Body: {response.text}")

if response.status_code == 201:
    print("\n✓ Batch created successfully!")
    print(f"Response JSON: {response.json()}")
else:
    print(f"\n✗ Failed to create batch")
