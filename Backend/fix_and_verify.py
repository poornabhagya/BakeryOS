#!/usr/bin/env python
"""Direct migration and testing without HTTP requests"""
import os
import sys
import django
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from django.core.management import call_command
from django.db import connection
from api.models import Product, Category, User

print("\n" + "=" * 80)
print("PRODUCT API - FIX & TEST".center(80))
print("=" * 80)

# Step 1: Apply migrations
print("\n[STEP 1] Applying migrations...")
try:
    call_command('migrate', verbosity=1)
    print("✓ Migrations applied")
except Exception as e:
    print(f"✗ Migration error: {e}")
    sys.exit(1)

# Step 2: Verify Product table
print("\n[STEP 2] Verifying Product table...")
with connection.cursor() as cursor:
    cursor.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' AND name='api_product'
    """)
    if cursor.fetchone():
        print("✓ Product table exists")
    else:
        print("✗ Product table NOT found!")
        sys.exit(1)

# Step 3: Check existing data
print("\n[STEP 3] Checking existing products...")
product_count = Product.objects.count()
print(f"✓ Current products in database: {product_count}")

# Step 4: Create test data
if product_count == 0:
    print("\n[STEP 4] Creating test products...")
    cat, _ = Category.objects.get_or_create(
        name='Buns', 
        type='Product',
        defaults={'description': 'Test buns'}
    )
    
    product = Product.objects.create(
        category_id=cat,
        name='Test Burger Bun',
        cost_price=Decimal('15.00'),
        selling_price=Decimal('25.00'),
        current_stock=Decimal('50.00'),
        shelf_life=2,
        shelf_unit='days'
    )
    print(f"✓ Created test product: {product.product_id}")
    product_count = 1
else:
    print("\n[STEP 4] Skipping - products already exist")

# Step 5: Validate model
print("\n[STEP 5] Validating Product model...")
p = Product.objects.first()
if p:
    print(f"  Product: {p.product_id}")
    print(f"  Name: {p.name}")
    print(f"  Cost: Rs. {p.cost_price}")
    print(f"  Selling: Rs. {p.selling_price}")
    print(f"  Profit Margin: {p.profit_margin:.2f}%")
    print(f"  Stock Status: {p.status}")
    print("✓ Model working correctly")
else:
    print("✗ No products found")

# Step 6: List all
print(f"\n[STEP 6] Products summary:")
print(f"  Total: {Product.objects.count()}")
print(f"  Available:  {Product.objects.filter(current_stock__gte=10).count()}")
print(f"  Low Stock:  {Product.objects.filter(current_stock__lt=10, current_stock__gt=0).count()}")
print(f"  Out Stock:  {Product.objects.filter(current_stock__lte=0).count()}")

print("\n" + "=" * 80)
print("✅ DATABASE AND MODELS VERIFIED - Ready to test API endpoints!".center(80))
print("\nNext: Start server with 'python manage.py runserver 8000'".center(80))
print("Then test: 'curl -H \"Authorization: Token TOKEN\" http://localhost:8000/api/products/'".center(80))
print("=" * 80 + "\n")
