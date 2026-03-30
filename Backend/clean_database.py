#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import Sale, SaleItem, ProductWastage, IngredientWastage
from django.db.models import Sum

print("=" * 80)
print("CLEARING ALL SALES AND WASTAGE DATA".center(80))
print("=" * 80)

print("\nBefore cleanup:")
print(f"  Sales: {Sale.objects.count()} records")
print(f"  SaleItems: {SaleItem.objects.count()} records")
print(f"  ProductWastage: {ProductWastage.objects.count()} records")
print(f"  IngredientWastage: {IngredientWastage.objects.count()} records")

total_before = Sale.objects.count() + ProductWastage.objects.count() + IngredientWastage.objects.count()

# Delete all sales and wastage
Sale.objects.all().delete()
ProductWastage.objects.all().delete()
IngredientWastage.objects.all().delete()

print("\nAfter cleanup:")
print(f"  Sales: {Sale.objects.count()} records")
print(f"  SaleItems: {SaleItem.objects.count()} records")
print(f"  ProductWastage: {ProductWastage.objects.count()} records")
print(f"  IngredientWastage: {IngredientWastage.objects.count()} records")

print(f"\n✓ Deleted {total_before} records")
print("\n✓ Database is now CLEAN - Dashboard will show:")
print("  - Total Revenue: 0")
print("  - Total Orders: 0")  
print("  - Total Wastage Loss: 0")
print("  - Top Selling Items: (empty)")
print("  - Wastage Breakdown: (empty)")
print("  - Recent Transactions: (empty)")

print("\n" + "=" * 80)
