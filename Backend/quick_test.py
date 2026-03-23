#!/usr/bin/env python
import urllib.request
import json

# Test the Product API endpoint
token = "bd616d5e8bd9e45e61e40721c043b7f0edeb6b6d"
headers = {"Authorization": f"Token {token}"}

url = "http://localhost:8000/api/products/"

try:
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req) as response:
        status = response.getcode()
        data = response.read().decode()
        print(f"✓ SUCCESS - Status Code: {status}")
        print(f"Response preview: {data[:200]}...")
except Exception as e:
    print(f"✗ ERROR - {type(e).__name__}: {str(e)}")
