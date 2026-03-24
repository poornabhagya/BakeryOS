#!/usr/bin/env python
"""
Manual Testing Script for Task 4.3: ProductBatch Endpoints
Tests all endpoints with different roles and verifies functionality
"""

import requests
import json
from decimal import Decimal
from datetime import date, timedelta

BASE_URL = "http://localhost:8000/api"

# Color codes for console output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

class TestRunner:
    def __init__(self):
        self.baker_token = None
        self.manager_token = None
        self.storekeeper_token = None
        self.cashier_token = None
        self.product_id = None
        self.batch_id = None
        self.passed = 0
        self.failed = 0

    def print_section(self, title):
        print(f"\n{BLUE}{'='*60}")
        print(f"{title}")
        print(f"{'='*60}{RESET}\n")

    def print_success(self, message):
        print(f"{GREEN}✓ {message}{RESET}")
        self.passed += 1

    def print_error(self, message):
        print(f"{RED}✗ {message}{RESET}")
        self.failed += 1

    def print_warning(self, message):
        print(f"{YELLOW}⚠ {message}{RESET}")

    def login(self, username, password):
        """Login user and get token"""
        payload = {
            'username': username,
            'password': password
        }
        response = requests.post(f"{BASE_URL}/auth/login/", json=payload)
        if response.status_code == 200:
            token = response.json().get('token')
            return token
        return None

    def get_product(self):
        """Get or create a product for testing"""
        headers = {'Authorization': f'Token {self.baker_token}'}
        
        # Get first product
        response = requests.get(f"{BASE_URL}/products/", headers=headers)
        if response.status_code == 200 and response.json().get('results'):
            return response.json()['results'][0]['id']
        return None

    def test_1_authentication(self):
        """Test 1: User Authentication"""
        self.print_section("TEST 1: User Authentication")
        
        # Test Baker login
        token = self.login('baker1', 'baker123')
        if token:
            self.baker_token = token
            self.print_success("Baker login successful")
        else:
            self.print_error("Baker login failed")
            return False

        # Test Manager login
        token = self.login('manager1', 'manager123')
        if token:
            self.manager_token = token
            self.print_success("Manager login successful")
        else:
            self.print_error("Manager login failed")
            return False

        # Test Storekeeper login
        token = self.login('storekeeper1', 'storekeeper123')
        if token:
            self.storekeeper_token = token
            self.print_success("Storekeeper login successful")
        else:
            self.print_error("Storekeeper login failed")
            return False

        # Test Cashier login
        token = self.login('cashier1', 'cashier123')
        if token:
            self.cashier_token = token
            self.print_success("Cashier login successful")
        else:
            self.print_error("Cashier login failed")
            return False

        return True

    def test_2_get_product(self):
        """Test 2: Get Product for Testing"""
        self.print_section("TEST 2: Get Product for Testing")
        
        self.product_id = self.get_product()
        if self.product_id:
            self.print_success(f"Product retrieved: ID {self.product_id}")
            return True
        else:
            self.print_error("Failed to get product")
            return False

    def test_3_baker_create_batch(self):
        """Test 3: Baker can create batch"""
        self.print_section("TEST 3: Baker Create Batch")
        
        today = date.today().isoformat()
        payload = {
            'product_id': self.product_id,
            'quantity': '10.00',
            'made_date': today,
            'notes': 'Test batch created by baker'
        }
        
        headers = {
            'Authorization': f'Token {self.baker_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            f"{BASE_URL}/product-batches/",
            json=payload,
            headers=headers
        )
        
        if response.status_code == 201:
            data = response.json()
            self.batch_id = data.get('id')
            batch_id_val = data.get('batch_id')
            self.print_success(f"Batch created successfully - Batch ID: {batch_id_val}")
            return True
        else:
            self.print_error(f"Batch creation failed - Status: {response.status_code}")
            self.print_warning(f"Response: {response.text}")
            return False

    def test_4_manager_cannot_see(self):
        """Test 4: Other roles can view batches"""
        self.print_section("TEST 4: List Batches - Different Roles")
        
        headers_manager = {'Authorization': f'Token {self.manager_token}'}
        headers_storekeeper = {'Authorization': f'Token {self.storekeeper_token}'}
        
        # Manager list
        response = requests.get(
            f"{BASE_URL}/product-batches/",
            headers=headers_manager
        )
        if response.status_code == 200:
            self.print_success("Manager can list batches")
        else:
            self.print_error(f"Manager list failed: {response.status_code}")
        
        # Storekeeper list
        response = requests.get(
            f"{BASE_URL}/product-batches/",
            headers=headers_storekeeper
        )
        if response.status_code == 200:
            self.print_success("Storekeeper can list batches")
        else:
            self.print_error(f"Storekeeper list failed: {response.status_code}")

    def test_5_cashier_cannot_create(self):
        """Test 5: Cashier cannot create batch (permission check)"""
        self.print_section("TEST 5: Cashier Permission Check - Cannot Create")
        
        today = date.today().isoformat()
        payload = {
            'product_id': self.product_id,
            'quantity': '5.00',
            'made_date': today
        }
        
        headers = {
            'Authorization': f'Token {self.cashier_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            f"{BASE_URL}/product-batches/",
            json=payload,
            headers=headers
        )
        
        if response.status_code == 403:
            self.print_success("Cashier correctly denied access to create batch")
            return True
        else:
            self.print_error(f"Cashier permission check failed - Status: {response.status_code}")
            return False

    def test_6_retrieve_batch(self):
        """Test 6: Retrieve single batch details"""
        self.print_section("TEST 6: Retrieve Batch Details")
        
        if not self.batch_id:
            self.print_error("No batch ID available")
            return False
        
        headers = {'Authorization': f'Token {self.baker_token}'}
        
        response = requests.get(
            f"{BASE_URL}/product-batches/{self.batch_id}/",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            batch_id = data.get('batch_id')
            quantity = data.get('quantity')
            expire_date = data.get('expire_date')
            self.print_success(f"Batch retrieved - ID: {batch_id}, Qty: {quantity}, Expires: {expire_date}")
            return True
        else:
            self.print_error(f"Batch retrieval failed - Status: {response.status_code}")
            return False

    def test_7_update_batch(self):
        """Test 7: Baker can update batch"""
        self.print_section("TEST 7: Baker Update Batch")
        
        if not self.batch_id:
            self.print_error("No batch ID available")
            return False
        
        payload = {
            'quantity': '12.00',
            'notes': 'Updated by baker'
        }
        
        headers = {
            'Authorization': f'Token {self.baker_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.patch(
            f"{BASE_URL}/product-batches/{self.batch_id}/",
            json=payload,
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            quantity = data.get('quantity')
            self.print_success(f"Batch updated successfully - New Qty: {quantity}")
            return True
        else:
            self.print_error(f"Batch update failed - Status: {response.status_code}")
            self.print_warning(f"Response: {response.text}")
            return False

    def test_8_storekeeper_cannot_update(self):
        """Test 8: Storekeeper cannot update batch"""
        self.print_section("TEST 8: Storekeeper Permission Check - Cannot Update")
        
        if not self.batch_id:
            self.print_error("No batch ID available")
            return False
        
        payload = {'quantity': '15.00'}
        
        headers = {
            'Authorization': f'Token {self.storekeeper_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.patch(
            f"{BASE_URL}/product-batches/{self.batch_id}/",
            json=payload,
            headers=headers
        )
        
        if response.status_code == 403:
            self.print_success("Storekeeper correctly denied access to update batch")
            return True
        else:
            self.print_error(f"Storekeeper permission check failed - Status: {response.status_code}")
            return False

    def test_9_get_expiring_batches(self):
        """Test 9: Get expiring batches (within 2 days)"""
        self.print_section("TEST 9: Get Expiring Batches")
        
        headers = {'Authorization': f'Token {self.baker_token}'}
        
        response = requests.get(
            f"{BASE_URL}/product-batches/expiring/",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            count = len(data.get('results', []))
            self.print_success(f"Expiring batches retrieved - Count: {count}")
            return True
        else:
            self.print_error(f"Get expiring batches failed - Status: {response.status_code}")
            return False

    def test_10_use_batch(self):
        """Test 10: Use batch quantity"""
        self.print_section("TEST 10: Use Batch Quantity")
        
        if not self.batch_id:
            self.print_error("No batch ID available")
            return False
        
        payload = {
            'quantity_used': '2.00',
            'reason': 'Sold to customer'
        }
        
        headers = {
            'Authorization': f'Token {self.baker_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            f"{BASE_URL}/product-batches/{self.batch_id}/use_batch/",
            json=payload,
            headers=headers
        )
        
        if response.status_code == 200:
            self.print_success("Batch usage recorded successfully")
            return True
        else:
            self.print_error(f"Batch usage failed - Status: {response.status_code}")
            self.print_warning(f"Response: {response.text}")
            return False

    def test_11_get_product_batches(self):
        """Test 11: Get all batches for specific product"""
        self.print_section("TEST 11: Get Product Batches")
        
        headers = {'Authorization': f'Token {self.baker_token}'}
        
        response = requests.get(
            f"{BASE_URL}/product-batches/product/{self.product_id}/",
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            count = len(data.get('results', []) or data) if isinstance(data, (list, dict)) else 0
            self.print_success(f"Product batches retrieved - Count: {count}")
            return True
        else:
            self.print_error(f"Get product batches failed - Status: {response.status_code}")
            return False

    def test_12_batch_summary(self):
        """Test 12: Get batch summary statistics"""
        self.print_section("TEST 12: Batch Summary Statistics")
        
        headers = {'Authorization': f'Token {self.baker_token}'}
        
        response = requests.get(
            f"{BASE_URL}/product-batches/summary/",
            headers=headers
        )
        
        if response.status_code == 200:
            self.print_success("Batch summary retrieved successfully")
            return True
        else:
            self.print_error(f"Batch summary failed - Status: {response.status_code}")
            return False

    def test_13_manager_delete_batch(self):
        """Test 13: Manager can delete batch"""
        self.print_section("TEST 13: Manager Delete Batch")
        
        if not self.batch_id:
            self.print_error("No batch ID available")
            return False
        
        headers = {'Authorization': f'Token {self.manager_token}'}
        
        response = requests.delete(
            f"{BASE_URL}/product-batches/{self.batch_id}/",
            headers=headers
        )
        
        if response.status_code == 204:
            self.print_success("Batch deleted successfully by manager")
            self.batch_id = None  # Clear batch ID
            return True
        else:
            self.print_error(f"Batch deletion failed - Status: {response.status_code}")
            return False

    def test_14_baker_cannot_delete(self):
        """Test 14: Baker cannot delete batch (permission check)"""
        self.print_section("TEST 14: Baker Permission Check - Cannot Delete")
        
        # Create a batch first
        today = date.today().isoformat()
        payload = {
            'product_id': self.product_id,
            'quantity': '5.00',
            'made_date': today
        }
        
        headers = {
            'Authorization': f'Token {self.baker_token}',
            'Content-Type': 'application/json'
        }
        
        response = requests.post(
            f"{BASE_URL}/product-batches/",
            json=payload,
            headers=headers
        )
        
        if response.status_code != 201:
            self.print_error("Could not create test batch")
            return False
        
        batch_id = response.json().get('id')
        
        # Try to delete as baker
        headers = {'Authorization': f'Token {self.baker_token}'}
        response = requests.delete(
            f"{BASE_URL}/product-batches/{batch_id}/",
            headers=headers
        )
        
        if response.status_code == 403:
            self.print_success("Baker correctly denied access to delete batch")
            return True
        else:
            self.print_error(f"Baker permission check failed - Status: {response.status_code}")
            return False

    def run_all_tests(self):
        """Run all tests"""
        tests = [
            self.test_1_authentication,
            self.test_2_get_product,
            self.test_3_baker_create_batch,
            self.test_4_manager_cannot_see,
            self.test_5_cashier_cannot_create,
            self.test_6_retrieve_batch,
            self.test_7_update_batch,
            self.test_8_storekeeper_cannot_update,
            self.test_9_get_expiring_batches,
            self.test_10_use_batch,
            self.test_11_get_product_batches,
            self.test_12_batch_summary,
            self.test_13_manager_delete_batch,
            self.test_14_baker_cannot_delete,
        ]
        
        for test in tests:
            try:
                test()
            except Exception as e:
                self.print_error(f"Test failed with exception: {str(e)}")

        self.print_summary()

    def print_summary(self):
        """Print test summary"""
        self.print_section("TEST SUMMARY")
        total = self.passed + self.failed
        print(f"Total Tests: {total}")
        print(f"{GREEN}Passed: {self.passed}{RESET}")
        print(f"{RED}Failed: {self.failed}{RESET}")
        
        if self.failed == 0:
            print(f"\n{GREEN}All tests passed! ✓{RESET}")
        else:
            print(f"\n{YELLOW}Some tests failed. Review the errors above.{RESET}")


if __name__ == '__main__':
    runner = TestRunner()
    runner.run_all_tests()
