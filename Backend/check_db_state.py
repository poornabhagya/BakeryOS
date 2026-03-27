#!/usr/bin/env python
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.models import Sale, Product, ProductWastage, SaleItem
from django.db.models import Sum
from decimal import Decimal

print("=" * 80)
print("DATABASE STATE CHECK".center(80))
print("=" * 80)

print(f"\nProducts count: {Product.objects.count()}")
print(f"Sales count: {Sale.objects.count()}")
print(f"Sale Items count: {SaleItem.objects.count()}")
print(f"Product Wastage count: {ProductWastage.objects.count()}")

if Sale.objects.count() > 0:
    total_sales = Sale.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or Decimal('0')
    print(f"\nTotal sales revenue: {float(total_sales)}")
    
    print("\nRecent sales:")
    for sale in Sale.objects.all()[:3]:
        print(f"  - Sale #{sale.id}: Rs. {sale.total_amount} ({sale.created_at})")
        for item in sale.items.all():
            print(f"    - {item.product_id.name}: {item.quantity} pcs @ Rs. {item.subtotal}")
else:
    print("\n✓ NO SALES IN DATABASE - Revenue should be 0")

if ProductWastage.objects.count() > 0:
    total_wastage = ProductWastage.objects.aggregate(Sum('total_loss'))['total_loss__sum'] or Decimal('0')
    print(f"\nTotal wastage loss: {float(total_wastage)}")
    
    print("\nRecent wastage:")
    for wastage in ProductWastage.objects.all()[:3]:
        print(f"  - {wastage.product_id.name}: {wastage.quantity} @ Rs. {wastage.total_loss}")
else:
    print("\n✓ NO WASTAGE IN DATABASE - Wastage should be 0")

print("\nProducts in database (first 10):")
for product in Product.objects.all()[:10]:
    print(f"  - {product.name}: {product.current_stock} units (cost: {product.cost_price}, sell: {product.selling_price})")

print("\n" + "=" * 80)
print("\nNow testing API endpoints...")
print("=" * 80)

# Import and test the ViewSet directly
from api.views.analytics_views import SalesStatsViewSet, ProductStatsViewSet, WastageStatsViewSet
from unittest.mock import Mock
from rest_framework.test import APIRequestFactory

factory = APIRequestFactory()
request = factory.get('/api/analytics/sales-stats/')
request.user = Mock()
request.user.is_authenticated = True

viewset = SalesStatsViewSet()
response = viewset.list(request)
print(f"\nSalesStatsViewSet response:")
import json
print(json.dumps(response.data, indent=2, default=str))

viewset = ProductStatsViewSet()
response = viewset.list(request)
print(f"\nProductStatsViewSet response:")
print(json.dumps(response.data, indent=2, default=str))

viewset = WastageStatsViewSet()
response = viewset.list(request)
print(f"\nWastageStatsViewSet response:")
print(json.dumps(response.data, indent=2, default=str))
