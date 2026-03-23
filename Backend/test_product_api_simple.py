#!/usr/bin/env python
"""Simple Product API test"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import Product, Category

# Test 1: Check if products table exists and has data
print("=" * 70)
print("PRODUCT API HEALTH CHECK".center(70))
print("=" * 70)

try:
    products = Product.objects.all()
    print(f"\n✓ Product table accessible")
    print(f"  Total products: {products.count()}")
    
    if products.exists():
        print(f"\n  First 5 products:")
        for p in products[:5]:
            print(f"    - {p.product_id}: {p.name} (Stock: {p.current_stock})")
    else:
        print(f"\n  No products found - creating test data...")
        
        # Get or create product category
        category, _ = Category.objects.get_or_create(
            name="Buns",
            type="Product",
            defaults={'description': 'Bakery buns and rolls'}
        )
        
        # Create test products
        test_products = [
            {'name': 'White Bun', 'cost_price': 0.50, 'selling_price': 1.00, 'current_stock': 50},
            {'name': 'Wheat Bun', 'cost_price': 0.60, 'selling_price': 1.20, 'current_stock': 30},
            {'name': 'Chocolate Bun', 'cost_price': 0.80, 'selling_price': 1.50, 'current_stock': 20},
        ]
        
        for p in test_products:
            product = Product.objects.create(
                category_id=category,
                name=p['name'],
                cost_price=p['cost_price'],
                selling_price=p['selling_price'],
                current_stock=p['current_stock']
            )
            print(f"    ✓ Created: {product.product_id} - {product.name}")
        
except Exception as e:
    print(f"✗ Error accessing Product table: {e}")
    sys.exit(1)

# Test 2: Check Product model methods
print("\n" + "=" * 70)
print("PRODUCT MODEL VALIDATION".center(70))
print("=" * 70 + "\n")

if products.exists():
    product = products.first()
    print(f"Testing product: {product.product_id} - {product.name}")
    print(f"  Cost Price: ${product.cost_price}")
    print(f"  Selling Price: ${product.selling_price}")
    print(f"  Profit Margin: {product.profit_margin:.2f}%")
    print(f"  Current Stock: {product.current_stock}")
    print(f"  Status: {product.status}")
    print(f"  Is Low Stock: {product.is_low_stock}")
    print(f"  Is Out of Stock: {product.is_out_of_stock}")

print("\n✓ Product API health check complete")
