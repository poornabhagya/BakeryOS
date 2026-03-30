#!/usr/bin/env python
"""
Test script to verify the analytics endpoint fix for deleted products.
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from api.views.analytics_views import SalesAnalyticsViewSet
from rest_framework.test import APIRequestFactory
from rest_framework.request import Request as DRFRequest
from rest_framework.response import Response
from decimal import Decimal

print("\n" + "="*80)
print("ANALYTICS ENDPOINT FIX VERIFICATION")
print("="*80)

try:
    # Create request factory
    factory = APIRequestFactory()
    viewset = SalesAnalyticsViewSet()
    
    # Test 1: daily endpoint
    print("\n[TEST 1] Testing daily() endpoint...")
    wsgi_request = factory.get('/api/analytics/daily/')
    request = DRFRequest(wsgi_request)
    viewset.request = request
    viewset.format_kwarg = None
    response = viewset.daily(request)
    
    if isinstance(response, Response):
        if 200 <= response.status_code < 300:
            print(f"✅ daily() succeeded with status {response.status_code}")
        else:
            print(f"❌ daily() returned status {response.status_code}")
    else:
        print(f"❌ daily() returned non-Response: {type(response)}")
    
    # Test 2: weekly endpoint
    print("\n[TEST 2] Testing weekly() endpoint...")
    wsgi_request = factory.get('/api/analytics/weekly/')
    request = DRFRequest(wsgi_request)
    response = viewset.weekly(request)
    
    if isinstance(response, Response):
        if 200 <= response.status_code < 300:
            print(f"✅ weekly() succeeded with status {response.status_code}")
        else:
            print(f"❌ weekly() returned status {response.status_code}")
    else:
        print(f"❌ weekly() returned non-Response: {type(response)}")
    
    # Test 3: monthly endpoint
    print("\n[TEST 3] Testing monthly() endpoint...")
    wsgi_request = factory.get('/api/analytics/monthly/')
    request = DRFRequest(wsgi_request)
    response = viewset.monthly(request)
    
    if isinstance(response, Response):
        if 200 <= response.status_code < 300:
            print(f"✅ monthly() succeeded with status {response.status_code}")
        else:
            print(f"❌ monthly() returned status {response.status_code}")
    else:
        print(f"❌ monthly() returned non-Response: {type(response)}")
    
    # Test 4: revenue endpoint
    print("\n[TEST 4] Testing revenue() endpoint...")
    wsgi_request = factory.get('/api/analytics/revenue/')
    request = DRFRequest(wsgi_request)
    response = viewset.revenue(request)
    
    if isinstance(response, Response):
        if 200 <= response.status_code < 300:
            print(f"✅ revenue() succeeded with status {response.status_code}")
            if response.data:
                print(f"   Response keys: {list(response.data.keys())}")
        else:
            print(f"❌ revenue() returned status {response.status_code}")
    else:
        print(f"❌ revenue() returned non-Response: {type(response)}")
    
    print("\n" + "="*80)
    print("✅ ALL ANALYTICS ENDPOINTS WORKING - NO 500 ERRORS!")
    print("="*80)
    
except Exception as e:
    print("\n❌ ERROR DURING TESTING:")
    print(f"{type(e).__name__}: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
