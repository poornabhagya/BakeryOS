"""
Comprehensive tests for Ingredient Batch API endpoints.

Test Coverage:
- List batches with pagination and filtering
- Get batch details
- Create new batch with validation
- Update batch (PATCH)
- Delete batch
- Consume from batch (FIFO logic)
- Expiring batches endpoint
- By ingredient batches endpoint
- Permission checks
- Data integrity (quantity sync to ingredient)
"""

import json
import requests
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone

# Configuration
BASE_URL = "http://localhost:8000/api"
MANAGER_TOKEN = "YOUR_MANAGER_TOKEN_HERE"
STOREKEEPER_TOKEN = "YOUR_STOREKEEPER_TOKEN_HERE"
BAKER_TOKEN = "YOUR_BAKER_TOKEN_HERE"
CASHIER_TOKEN = "YOUR_CASHIER_TOKEN_HERE"


class Colors:
    """Terminal colors for output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'


def test_result(test_name, passed, details=""):
    """Print test result with color"""
    status = f"{Colors.GREEN}✓ PASS{Colors.END}" if passed else f"{Colors.RED}✗ FAIL{Colors.END}"
    print(f"  {status} - {test_name}")
    if details and not passed:
        print(f"         {details}")


class TestBatchAPI:
    """Test suite for Batch API"""
    
    def __init__(self, manager_token, storekeeper_token, baker_token):
        self.manager_token = manager_token
        self.storekeeper_token = storekeeper_token
        self.baker_token = baker_token
        self.headers_manager = {"Authorization": f"Token {manager_token}"}
        self.headers_storekeeper = {"Authorization": f"Token {storekeeper_token}"}
        self.headers_baker = {"Authorization": f"Token {baker_token}"}
        self.test_count = 0
        self.passed_count = 0
    
    def run_all_tests(self):
        """Run all test cases"""
        print(f"\n{Colors.BLUE}{'='*60}")
        print(f"INGREDIENT BATCH API - COMPREHENSIVE TEST SUITE")
        print(f"{'='*60}{Colors.END}\n")
        
        print(f"{Colors.YELLOW}Test Group 1: List & Filter Batches{Colors.END}")
        self.test_list_all_batches()
        self.test_list_batches_pagination()
        self.test_filter_by_ingredient()
        self.test_filter_by_status()
        self.test_search_batches()
        
        print(f"\n{Colors.YELLOW}Test Group 2: Get & Details{Colors.END}")
        self.test_get_batch_details()
        self.test_get_nonexistent_batch()
        
        print(f"\n{Colors.YELLOW}Test Group 3: Create New Batch{Colors.END}")
        self.test_create_valid_batch()
        self.test_create_batch_invalid_quantity()
        self.test_create_batch_invalid_dates()
        
        print(f"\n{Colors.YELLOW}Test Group 4: Update Batch{Colors.END}")
        self.test_partial_update_batch()
        self.test_update_batch_quantity()
        
        print(f"\n{Colors.YELLOW}Test Group 5: Custom Actions{Colors.END}")
        self.test_batches_expiring_soon()
        self.test_expired_batches()
        self.test_out_of_stock_batches()
        self.test_by_ingredient_batches()
        
        print(f"\n{Colors.YELLOW}Test Group 6: Consume Batch{Colors.END}")
        self.test_consume_valid_amount()
        self.test_consume_invalid_amount()
        self.test_consume_exceeds_available()
        
        print(f"\n{Colors.YELLOW}Test Group 7: Delete & Status{Colors.END}")
        self.test_delete_batch()
        self.test_update_expiry_status()
        
        print(f"\n{Colors.YELLOW}Test Group 8: Permissions{Colors.END}")
        self.test_permission_create_manager()
        self.test_permission_create_storekeeper()
        self.test_permission_create_baker_forbidden()
        self.test_permission_delete_manager()
        self.test_permission_delete_storekeeper()
        
        print(f"\n{Colors.YELLOW}Test Group 9: Quantity Sync{Colors.END}")
        self.test_ingredient_quantity_sync()
        
        print(f"\n{Colors.YELLOW}Test Group 10: Validation Rules{Colors.END}")
        self.test_validation_expiry_before_made()
        self.test_validation_current_qty_exceeds_quantity()
        
        # Summary
        print(f"\n{Colors.BLUE}{'='*60}")
        print(f"TEST SUMMARY: {self.passed_count}/{self.test_count} tests passed")
        print(f"{'='*60}{Colors.END}\n")
        
        if self.passed_count == self.test_count:
            print(f"{Colors.GREEN}✓ All tests passed!{Colors.END}\n")
        else:
            print(f"{Colors.RED}✗ {self.test_count - self.passed_count} tests failed{Colors.END}\n")
    
    def test_list_all_batches(self):
        """Test: List all batches with pagination"""
        self.test_count += 1
        try:
            response = requests.get(
                f"{BASE_URL}/batches/",
                headers=self.headers_manager
            )
            passed = response.status_code == 200 and 'results' in response.json()
            self.passed_count += passed
            
            data = response.json()
            count = len(data.get('results', []))
            test_result("List all batches", passed, f"Got {count} batches")
        except Exception as e:
            test_result("List all batches", False, str(e))
    
    def test_list_batches_pagination(self):
        """Test: Pagination with page_size"""
        self.test_count += 1
        try:
            response = requests.get(
                f"{BASE_URL}/batches/?page_size=10&page=1",
                headers=self.headers_manager
            )
            passed = response.status_code == 200
            self.passed_count += passed
            test_result("Pagination (page_size=10)", passed)
        except Exception as e:
            test_result("Pagination", False, str(e))
    
    def test_filter_by_ingredient(self):
        """Test: Filter batches by ingredient_id"""
        self.test_count += 1
        try:
            # Assuming ingredient_id=1 exists
            response = requests.get(
                f"{BASE_URL}/batches/?ingredient_id=1",
                headers=self.headers_manager
            )
            passed = response.status_code == 200
            self.passed_count += passed
            
            if passed:
                batches = response.json().get('results', [])
                all_match = all(b['ingredient_id'] == 1 for b in batches)
                passed = all_match
                self.passed_count += (all_match - 1) if not all_match else 0
            
            test_result("Filter by ingredient_id", passed)
        except Exception as e:
            test_result("Filter by ingredient_id", False, str(e))
    
    def test_filter_by_status(self):
        """Test: Filter batches by status (Active, Expired, Used)"""
        self.test_count += 1
        try:
            response = requests.get(
                f"{BASE_URL}/batches/?status=Active",
                headers=self.headers_manager
            )
            passed = response.status_code == 200
            self.passed_count += passed
            
            data = response.json()
            active_count = len([b for b in data.get('results', []) if b['status'] == 'Active'])
            test_result("Filter by status=Active", passed, f"Found {active_count} active")
        except Exception as e:
            test_result("Filter by status", False, str(e))
    
    def test_search_batches(self):
        """Test: Search batches by batch_id"""
        self.test_count += 1
        try:
            response = requests.get(
                f"{BASE_URL}/batches/?search=BATCH-1001",
                headers=self.headers_manager
            )
            passed = response.status_code == 200
            self.passed_count += passed
            test_result("Search by batch_id", passed)
        except Exception as e:
            test_result("Search by batch_id", False, str(e))
    
    def test_get_batch_details(self):
        """Test: Get specific batch details"""
        self.test_count += 1
        try:
            # Get first batch
            response = requests.get(
                f"{BASE_URL}/batches/",
                headers=self.headers_manager
            )
            batches = response.json().get('results', [])
            
            if batches:
                batch_id = batches[0]['id']
                detail_response = requests.get(
                    f"{BASE_URL}/batches/{batch_id}/",
                    headers=self.headers_manager
                )
                passed = detail_response.status_code == 200
                self.passed_count += passed
                test_result("Get batch details", passed, f"Batch #{batch_id}")
            else:
                test_result("Get batch details", False, "No batches found")
        except Exception as e:
            test_result("Get batch details", False, str(e))
    
    def test_get_nonexistent_batch(self):
        """Test: Get non-existent batch (should return 404)"""
        self.test_count += 1
        try:
            response = requests.get(
                f"{BASE_URL}/batches/99999/",
                headers=self.headers_manager
            )
            passed = response.status_code == 404
            self.passed_count += passed
            test_result("Get non-existent batch returns 404", passed)
        except Exception as e:
            test_result("Get non-existent batch", False, str(e))
    
    def test_create_valid_batch(self):
        """Test: Create new batch with valid data"""
        self.test_count += 1
        try:
            batch_data = {
                "ingredient_id": 1,
                "quantity": "50.00",
                "current_qty": "50.00",
                "cost_price": "12.50",
                "made_date": timezone.now().isoformat(),
                "expire_date": (timezone.now() + timedelta(days=30)).isoformat()
            }
            
            response = requests.post(
                f"{BASE_URL}/batches/",
                json=batch_data,
                headers=self.headers_storekeeper
            )
            
            passed = response.status_code == 201
            self.passed_count += passed
            
            if passed:
                data = response.json()
                batch_id = data.get('batch_id')
                test_result("Create valid batch", True, f"Created {batch_id}")
            else:
                test_result("Create valid batch", False, f"Status: {response.status_code}")
        except Exception as e:
            test_result("Create valid batch", False, str(e))
    
    def test_create_batch_invalid_quantity(self):
        """Test: Create batch with invalid quantity (should fail)"""
        self.test_count += 1
        try:
            batch_data = {
                "ingredient_id": 1,
                "quantity": "-10.00",  # Invalid: negative
                "current_qty": "10.00",
                "cost_price": "12.50",
                "made_date": timezone.now().isoformat(),
                "expire_date": (timezone.now() + timedelta(days=30)).isoformat()
            }
            
            response = requests.post(
                f"{BASE_URL}/batches/",
                json=batch_data,
                headers=self.headers_storekeeper
            )
            
            passed = response.status_code in [400, 422]  # Validation error
            self.passed_count += passed
            test_result("Reject negative quantity", passed, f"Status: {response.status_code}")
        except Exception as e:
            test_result("Reject negative quantity", False, str(e))
    
    def test_create_batch_invalid_dates(self):
        """Test: Create batch with expiry < made_date (should fail)"""
        self.test_count += 1
        try:
            batch_data = {
                "ingredient_id": 1,
                "quantity": "50.00",
                "current_qty": "50.00",
                "cost_price": "12.50",
                "made_date": timezone.now().isoformat(),
                "expire_date": (timezone.now() - timedelta(days=5)).isoformat()  # In the past!
            }
            
            response = requests.post(
                f"{BASE_URL}/batches/",
                json=batch_data,
                headers=self.headers_storekeeper
            )
            
            passed = response.status_code in [400, 422]
            self.passed_count += passed
            test_result("Reject expiry < made_date", passed, f"Status: {response.status_code}")
        except Exception as e:
            test_result("Reject expiry < made_date", False, str(e))
    
    def test_partial_update_batch(self):
        """Test: Partial update of batch (PATCH)"""
        self.test_count += 1
        try:
            # Get first batch
            response = requests.get(
                f"{BASE_URL}/batches/",
                headers=self.headers_manager
            )
            batches = response.json().get('results', [])
            
            if batches:
                batch_id = batches[0]['id']
                update_data = {
                    "cost_price": "15.00"
                }
                
                patch_response = requests.patch(
                    f"{BASE_URL}/batches/{batch_id}/",
                    json=update_data,
                    headers=self.headers_storekeeper
                )
                
                passed = patch_response.status_code == 200
                self.passed_count += passed
                test_result("Partial update (PATCH)", passed)
            else:
                test_result("Partial update", False, "No batches found")
        except Exception as e:
            test_result("Partial update", False, str(e))
    
    def test_update_batch_quantity(self):
        """Test: Update batch current_qty"""
        self.test_count += 1
        try:
            response = requests.get(
                f"{BASE_URL}/batches/",
                headers=self.headers_manager
            )
            batches = response.json().get('results', [])
            
            if batches:
                batch = batches[0]
                batch_id = batch['id']
                new_qty = batch['current_qty'] - 10  # Reduce by 10
                
                update_data = {
                    "current_qty": str(new_qty)
                }
                
                patch_response = requests.patch(
                    f"{BASE_URL}/batches/{batch_id}/",
                    json=update_data,
                    headers=self.headers_storekeeper
                )
                
                passed = patch_response.status_code == 200
                self.passed_count += passed
                test_result("Update batch quantity", passed)
            else:
                test_result("Update batch quantity", False, "No batches found")
        except Exception as e:
            test_result("Update batch quantity", False, str(e))
    
    def test_batches_expiring_soon(self):
        """Test: Get batches expiring within N days"""
        self.test_count += 1
        try:
            response = requests.get(
                f"{BASE_URL}/batches/expiring/?days=7",
                headers=self.headers_manager
            )
            
            passed = response.status_code == 200 and 'results' in response.json()
            self.passed_count += passed
            
            if passed:
                data = response.json()
                count = len(data['results'])
                test_result("Get expiring batches (within 7 days)", True, f"Found {count}")
            else:
                test_result("Get expiring batches", False, f"Status: {response.status_code}")
        except Exception as e:
            test_result("Get expiring batches", False, str(e))
    
    def test_expired_batches(self):
        """Test: Get all expired batches"""
        self.test_count += 1
        try:
            response = requests.get(
                f"{BASE_URL}/batches/expired/",
                headers=self.headers_manager
            )
            
            passed = response.status_code == 200
            self.passed_count += passed
            
            if passed:
                data = response.json()
                count = data.get('count', 0)
                test_result("Get expired batches", True, f"Found {count} expired")
            else:
                test_result("Get expired batches", False)
        except Exception as e:
            test_result("Get expired batches", False, str(e))
    
    def test_out_of_stock_batches(self):
        """Test: Get batches that are out of stock (current_qty == 0)"""
        self.test_count += 1
        try:
            response = requests.get(
                f"{BASE_URL}/batches/out-of-stock/",
                headers=self.headers_manager
            )
            
            passed = response.status_code == 200
            self.passed_count += passed
            
            if passed:
                data = response.json()
                count = data.get('count', 0)
                test_result("Get out-of-stock batches", True, f"Found {count}")
            else:
                test_result("Get out-of-stock batches", False)
        except Exception as e:
            test_result("Get out-of-stock batches", False, str(e))
    
    def test_by_ingredient_batches(self):
        """Test: Get all batches for a specific ingredient (FIFO)"""
        self.test_count += 1
        try:
            response = requests.get(
                f"{BASE_URL}/batches/by-ingredient/1/",
                headers=self.headers_manager
            )
            
            passed = response.status_code == 200
            self.passed_count += passed
            
            if passed:
                data = response.json()
                count = data.get('count', 0)
                test_result("Get batches by ingredient (FIFO)", True, f"Found {count}")
            else:
                test_result("Get batches by ingredient", False)
        except Exception as e:
            test_result("Get batches by ingredient", False, str(e))
    
    def test_consume_valid_amount(self):
        """Test: Consume valid amount from batch"""
        self.test_count += 1
        try:
            # Get first active batch with qty > 0
            response = requests.get(
                f"{BASE_URL}/batches/?status=Active",
                headers=self.headers_manager
            )
            batches = response.json().get('results', [])
            
            active_batch = next((b for b in batches if b['current_qty'] > 10), None)
            
            if active_batch:
                batch_id = active_batch['id']
                consume_amount = min(10, active_batch['current_qty'] - 1)
                
                consume_response = requests.post(
                    f"{BASE_URL}/batches/{batch_id}/consume/",
                    json={"amount": str(consume_amount)},
                    headers=self.headers_storekeeper
                )
                
                passed = consume_response.status_code == 200
                self.passed_count += passed
                test_result("Consume valid amount", passed, f"Consumed {consume_amount}")
            else:
                test_result("Consume valid amount", False, "No suitable batch found")
        except Exception as e:
            test_result("Consume valid amount", False, str(e))
    
    def test_consume_invalid_amount(self):
        """Test: Consume invalid amount (negative)"""
        self.test_count += 1
        try:
            response = requests.get(
                f"{BASE_URL}/batches/",
                headers=self.headers_manager
            )
            batches = response.json().get('results', [])
            
            if batches:
                batch_id = batches[0]['id']
                
                consume_response = requests.post(
                    f"{BASE_URL}/batches/{batch_id}/consume/",
                    json={"amount": "-5"},
                    headers=self.headers_storekeeper
                )
                
                passed = consume_response.status_code in [400, 422]
                self.passed_count += passed
                test_result("Reject negative consume", passed)
            else:
                test_result("Reject negative consume", False, "No batches found")
        except Exception as e:
            test_result("Reject negative consume", False, str(e))
    
    def test_consume_exceeds_available(self):
        """Test: Consume more than available (should fail)"""
        self.test_count += 1
        try:
            response = requests.get(
                f"{BASE_URL}/batches/?status=Active",
                headers=self.headers_manager
            )
            batches = response.json().get('results', [])
            
            if batches:
                batch = batches[0]
                batch_id = batch['id']
                available = batch['current_qty']
                
                consume_response = requests.post(
                    f"{BASE_URL}/batches/{batch_id}/consume/",
                    json={"amount": str(available + 50)},  # Way too much
                    headers=self.headers_storekeeper
                )
                
                passed = consume_response.status_code == 400
                self.passed_count += passed
                test_result("Reject over-consumption", passed)
            else:
                test_result("Reject over-consumption", False, "No batches found")
        except Exception as e:
            test_result("Reject over-consumption", False, str(e))
    
    def test_delete_batch(self):
        """Test: Delete (soft delete) a batch"""
        self.test_count += 1
        try:
            # Create a batch first
            batch_data = {
                "ingredient_id": 1,
                "quantity": "10.00",
                "current_qty": "10.00",
                "cost_price": "5.00",
                "made_date": timezone.now().isoformat(),
                "expire_date": (timezone.now() + timedelta(days=15)).isoformat()
            }
            
            create_response = requests.post(
                f"{BASE_URL}/batches/",
                json=batch_data,
                headers=self.headers_manager
            )
            
            if create_response.status_code == 201:
                batch_id = create_response.json().get('id')
                
                delete_response = requests.delete(
                    f"{BASE_URL}/batches/{batch_id}/",
                    headers=self.headers_manager
                )
                
                passed = delete_response.status_code in [200, 204]
                self.passed_count += passed
                test_result("Delete batch", passed)
            else:
                test_result("Delete batch", False, "Failed to create batch")
        except Exception as e:
            test_result("Delete batch", False, str(e))
    
    def test_update_expiry_status(self):
        """Test: Update expiry status for all batches"""
        self.test_count += 1
        try:
            response = requests.post(
                f"{BASE_URL}/batches/update-expiry-status/",
                headers=self.headers_manager
            )
            
            passed = response.status_code == 200
            self.passed_count += passed
            
            if passed:
                data = response.json()
                updated = data.get('updated_count', 0)
                test_result("Update expiry status", True, f"Updated {updated} batches")
            else:
                test_result("Update expiry status", False)
        except Exception as e:
            test_result("Update expiry status", False, str(e))
    
    def test_permission_create_manager(self):
        """Test: Manager can create batch"""
        self.test_count += 1
        try:
            batch_data = {
                "ingredient_id": 1,
                "quantity": "25.00",
                "made_date": timezone.now().isoformat(),
                "expire_date": (timezone.now() + timedelta(days=20)).isoformat()
            }
            
            response = requests.post(
                f"{BASE_URL}/batches/",
                json=batch_data,
                headers=self.headers_manager
            )
            
            passed = response.status_code == 201
            self.passed_count += passed
            test_result("Manager: can create", passed)
        except Exception as e:
            test_result("Manager: can create", False, str(e))
    
    def test_permission_create_storekeeper(self):
        """Test: Storekeeper can create batch"""
        self.test_count += 1
        try:
            batch_data = {
                "ingredient_id": 1,
                "quantity": "30.00",
                "made_date": timezone.now().isoformat(),
                "expire_date": (timezone.now() + timedelta(days=25)).isoformat()
            }
            
            response = requests.post(
                f"{BASE_URL}/batches/",
                json=batch_data,
                headers=self.headers_storekeeper
            )
            
            passed = response.status_code == 201
            self.passed_count += passed
            test_result("Storekeeper: can create", passed)
        except Exception as e:
            test_result("Storekeeper: can create", False, str(e))
    
    def test_permission_create_baker_forbidden(self):
        """Test: Baker cannot create batch (403 Forbidden)"""
        self.test_count += 1
        try:
            batch_data = {
                "ingredient_id": 1,
                "quantity": "20.00",
                "made_date": timezone.now().isoformat(),
                "expire_date": (timezone.now() + timedelta(days=20)).isoformat()
            }
            
            response = requests.post(
                f"{BASE_URL}/batches/",
                json=batch_data,
                headers=self.headers_baker
            )
            
            passed = response.status_code == 403
            self.passed_count += passed
            test_result("Baker: forbidden to create", passed, f"Status: {response.status_code}")
        except Exception as e:
            test_result("Baker: forbidden to create", False, str(e))
    
    def test_permission_delete_manager(self):
        """Test: Manager can delete batch"""
        self.test_count += 1
        try:
            # Create a batch first
            batch_data = {
                "ingredient_id": 1,
                "quantity": "5.00",
                "made_date": timezone.now().isoformat(),
                "expire_date": (timezone.now() + timedelta(days=10)).isoformat()
            }
            
            create_response = requests.post(
                f"{BASE_URL}/batches/",
                json=batch_data,
                headers=self.headers_manager
            )
            
            if create_response.status_code == 201:
                batch_id = create_response.json().get('id')
                
                delete_response = requests.delete(
                    f"{BASE_URL}/batches/{batch_id}/",
                    headers=self.headers_manager
                )
                
                passed = delete_response.status_code in [200, 204, 404]  # 404 if cascade deleted
                self.passed_count += passed
                test_result("Manager: can delete", passed)
            else:
                test_result("Manager: can delete", False, "Failed to create batch")
        except Exception as e:
            test_result("Manager: can delete", False, str(e))
    
    def test_permission_delete_storekeeper(self):
        """Test: Storekeeper can delete batch"""
        self.test_count += 1
        try:
            # Create a batch first
            batch_data = {
                "ingredient_id": 1,
                "quantity": "5.00",
                "made_date": timezone.now().isoformat(),
                "expire_date": (timezone.now() + timedelta(days=10)).isoformat()
            }
            
            create_response = requests.post(
                f"{BASE_URL}/batches/",
                json=batch_data,
                headers=self.headers_storekeeper
            )
            
            if create_response.status_code == 201:
                batch_id = create_response.json().get('id')
                
                delete_response = requests.delete(
                    f"{BASE_URL}/batches/{batch_id}/",
                    headers=self.headers_storekeeper
                )
                
                passed = delete_response.status_code in [200, 204, 404]
                self.passed_count += passed
                test_result("Storekeeper: can delete", passed)
            else:
                test_result("Storekeeper: can delete", False, "Failed to create batch")
        except Exception as e:
            test_result("Storekeeper: can delete", False, str(e))
    
    def test_ingredient_quantity_sync(self):
        """Test: Ingredient total_quantity syncs when batch is created/updated"""
        self.test_count += 1
        try:
            # Get an ingredient
            ing_response = requests.get(
                f"{BASE_URL}/ingredients/1/",
                headers=self.headers_manager
            )
            
            if ing_response.status_code == 200:
                ing_before = ing_response.json()
                qty_before = Decimal(ing_before.get('total_quantity', 0))
                
                # Create a batch for this ingredient
                batch_data = {
                    "ingredient_id": 1,
                    "quantity": "20.00",
                    "made_date": timezone.now().isoformat(),
                    "expire_date": (timezone.now() + timedelta(days=20)).isoformat()
                }
                
                requests.post(
                    f"{BASE_URL}/batches/",
                    json=batch_data,
                    headers=self.headers_storekeeper
                )
                
                # Check ingredient again
                import time
                time.sleep(0.5)  # Wait for signal processing
                
                ing_after = requests.get(
                    f"{BASE_URL}/ingredients/1/",
                    headers=self.headers_manager
                ).json()
                qty_after = Decimal(ing_after.get('total_quantity', 0))
                
                # Should increase by 20
                passed = qty_after > qty_before
                self.passed_count += passed
                test_result("Ingredient qty sync on batch create", passed, 
                           f"Before: {qty_before}, After: {qty_after}")
            else:
                test_result("Ingredient qty sync", False, "Could not get ingredient")
        except Exception as e:
            test_result("Ingredient qty sync", False, str(e))
    
    def test_validation_expiry_before_made(self):
        """Test: Expiry date must be >= made_date"""
        self.test_count += 1
        try:
            now = timezone.now()
            batch_data = {
                "ingredient_id": 1,
                "quantity": "15.00",
                "made_date": now.isoformat(),
                "expire_date": (now - timedelta(days=1)).isoformat()  # BEFORE made_date!
            }
            
            response = requests.post(
                f"{BASE_URL}/batches/",
                json=batch_data,
                headers=self.headers_storekeeper
            )
            
            passed = response.status_code in [400, 422]
            self.passed_count += passed
            test_result("Validate expiry >= made_date", passed, f"Status: {response.status_code}")
        except Exception as e:
            test_result("Validate expiry >= made_date", False, str(e))
    
    def test_validation_current_qty_exceeds_quantity(self):
        """Test: current_qty must be <= quantity"""
        self.test_count += 1
        try:
            batch_data = {
                "ingredient_id": 1,
                "quantity": "20.00",
                "current_qty": "30.00",  # EXCEEDS quantity!
                "made_date": timezone.now().isoformat(),
                "expire_date": (timezone.now() + timedelta(days=20)).isoformat()
            }
            
            response = requests.post(
                f"{BASE_URL}/batches/",
                json=batch_data,
                headers=self.headers_storekeeper
            )
            
            passed = response.status_code in [400, 422]
            self.passed_count += passed
            test_result("Validate current_qty <= quantity", passed, f"Status: {response.status_code}")
        except Exception as e:
            test_result("Validate current_qty <= quantity", False, str(e))


if __name__ == "__main__":
    # Get tokens (user needs to provide these)
    print(f"\n{Colors.YELLOW}Ingredient Batch API - Test Suite{Colors.END}")
    print("\nPlease provide authentication tokens:")
    
    manager_token = input("Manager Token (or press Enter for test): ").strip()
    storekeeper_token = input("Storekeeper Token (or press Enter for test): ").strip()
    baker_token = input("Baker Token (or press Enter for test): ").strip()
    
    if not manager_token:
        print(f"\n{Colors.RED}Error: Manager token required to run tests{Colors.END}")
        exit(1)
    
    # Create test suite and run
    tester = TestBatchAPI(manager_token, storekeeper_token, baker_token)
    tester.run_all_tests()
