#!/usr/bin/env python
"""Test Product API after fix"""
import json
import subprocess
import time
import sys

# Wait for server to start
time.sleep(2)

# Test using curl command
print("Testing Product API Endpoint...")
print("=" * 60)

cmd = [
    "powershell",
    "-Command",
    """
    $headers = @{
        'Authorization' = 'Token bd616d5e8bd9e45e61e40721c043b7f0edeb6b6d'
    }
    
    try {
        $response = Invoke-WebRequest -Uri 'http://localhost:8000/api/products/' -Headers $headers -UseBasicParsing
        Write-Host "✓ SUCCESS - Status Code: $($response.StatusCode)"
        $data = $response.Content | ConvertFrom-Json
        if ($data -is [array]) {
            Write-Host "Products count: $($data.Length)"
            if ($data.Length -gt 0) {
                Write-Host "Sample product: $($data[0])"
            }
        } else {
            Write-Host "Products count: $($data.count)"
            Write-Host "Sample product: $($data.results[0])"
        }
    } catch {
        Write-Host "✗ ERROR: $($_)"
    }
    """
]

result = subprocess.run(cmd, capture_output=True, text=True)
print(result.stdout)
if result.stderr:
    print("STDERR:", result.stderr)
