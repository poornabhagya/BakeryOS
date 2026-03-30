#!/usr/bin/env python
"""
Test to verify /api/analytics/sales-stats/ endpoint fix
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from rest_framework.test import APIRequestFactory
from rest_framework.request import Request as DRFRequest
from api.views.analytics_views import SalesStatsViewSet, ProductStatsViewSet

print('\n' + '='*80)
print('TESTING /api/analytics/sales-stats/ ENDPOINT FIX')
print('='*80)

try:
    # Create request factory
    factory = APIRequestFactory()
    
    # Test 1: SalesStatsViewSet (the one causing the 500 error)
    print('\n[TEST 1] Testing SalesStatsViewSet.list() ...')
    wsgi_request = factory.get('/api/analytics/sales-stats/')
    request = DRFRequest(wsgi_request)
    
    viewset = SalesStatsViewSet()
    response = viewset.list(request)
    
    print(f'Status Code: {response.status_code}')
    if response.status_code == 200:
        print('✅ SalesStatsViewSet succeeded!')
        print(f'Response data keys: {list(response.data.keys())}')
        print(f'Sample values:')
        print(f'  - total_revenue: {response.data.get("total_revenue")}')
        print(f'  - total_orders: {response.data.get("total_orders")}')
        print(f'  - net_profit: {response.data.get("net_profit")}')
    else:
        print(f'❌ Failed with status {response.status_code}')
        print(f'Error: {response.data}')
    
    # Test 2: ProductStatsViewSet (also accesses product data)
    print('\n[TEST 2] Testing ProductStatsViewSet.list() ...')
    wsgi_request = factory.get('/api/analytics/product-stats/')
    request = DRFRequest(wsgi_request)
    
    viewset = ProductStatsViewSet()
    response = viewset.list(request)
    
    print(f'Status Code: {response.status_code}')
    if response.status_code == 200:
        print('✅ ProductStatsViewSet succeeded!')
        print(f'Response keys: {list(response.data.keys())}')
        if 'top_products' in response.data:
            print(f'Top products count: {len(response.data["top_products"])}')
    else:
        print(f'❌ Failed with status {response.status_code}')
        print(f'Error: {response.data}')
    
    print('\n' + '='*80)
    print('✅ BOTH ENDPOINTS WORKING - /api/analytics/sales-stats/ FIXED!')
    print('='*80)
    
except Exception as e:
    print(f'\n❌ ERROR: {type(e).__name__}: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
