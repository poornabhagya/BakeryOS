"""
Comprehensive tests for Product API endpoints.

Test Coverage:
- List products with pagination and filtering
- Get product details
- Create new product with validation
- Update product (PATCH)
- Delete product
- Filter by category
- Low-stock and out-of-stock endpoints
- Permission checks
- Profit margin calculation
"""

import json
import requests
from decimal import Decimal
from datetime import datetime


# Configuration
BASE_URL = "http://localhost:8000/api"
TOKEN = "bd616d5e8bd9e45e61e40721c043b7f0edeb6b6d"  # testuser token

# Test user tokens (will need to create or use existing)
HEADERS = {
    'Authorization': f'Token {TOKEN}',
    'Content-Type': 'application/json'
}


class Colors:
    """Terminal colors for output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    END = '\033[0m'


def print_header(text):
    """Print colored header"""
    print(f"\n{Colors.CYAN}{'='*70}")
    print(f"{text.center(70)}")
    print(f"{'='*70}{Colors.END}\n")


def test_result(test_name, passed, details=""):
    """Print test result with color"""
    status = f"{Colors.GREEN}✓ PASS{Colors.END}" if passed else f"{Colors.RED}✗ FAIL{Colors.END}"
    print(f"  {status} - {test_name}")
    if details:
        for line in str(details).split('\n'):
            if line.strip():
                print(f"      {line}")


class TestProductAPI:
    """Test suite for Product API"""

    def __init__(self):
        self.base_url = f"{BASE_URL}/products"
        self.headers = HEADERS
        self.test_product_id = None
        self.passed = 0
        self.failed = 0

    def run_all_tests(self):
        """Run all test groups"""
        print_header("TASK 3.4 - PRODUCT API ENDPOINTS TEST")

        print(f"{Colors.BLUE}Server: {BASE_URL}{Colors.END}")
        print(f"{Colors.BLUE}Test User: testuser{Colors.END}\n")

        # Test Groups
        self.test_group_1_list_filter()
        self.test_group_2_get_details()
        self.test_group_3_create()
        self.test_group_4_update()
        self.test_group_5_custom_actions()
        self.test_group_6_delete()
        self.test_group_7_permissions()
        self.test_group_8_validation()
        self.test_group_9_calculations()

        # Summary
        self.print_summary()

    # ==========================================
    # TEST GROUP 1: List & Filter Products
    # ==========================================
    def test_group_1_list_filter(self):
        """Test listing and filtering products"""
        print_header("TEST GROUP 1: List & Filter Products")

        # Test 1.1: List all products
        try:
            response = requests.get(f"{self.base_url}/", headers=self.headers)
            passed = response.status_code == 200
            test_result(
                "GET /api/products/ - List all products",
                passed,
                f"Status: {response.status_code}, Count: {response.json().get('count', 0)}"
            )
            if passed:
                self.passed += 1
            else:
                self.failed += 1
        except Exception as e:
            test_result("GET /api/products/ - List all products", False, str(e))
            self.failed += 1

        # Test 1.2: Filter by category
        try:
            response = requests.get(
                f"{self.base_url}/?category_id=1",
                headers=self.headers
            )
            passed = response.status_code == 200
            test_result(
                "GET /api/products/?category_id=1 - Filter by category",
                passed,
                f"Status: {response.status_code}"
            )
            if passed:
                self.passed += 1
            else:
                self.failed += 1
        except Exception as e:
            test_result("GET /api/products/?category_id=1 - Filter by category", False, str(e))
            self.failed += 1

        # Test 1.3: Filter by status
        try:
            response = requests.get(
                f"{self.base_url}/?status=low_stock",
                headers=self.headers
            )
            passed = response.status_code == 200
            test_result(
                "GET /api/products/?status=low_stock - Filter by status",
                passed,
                f"Status: {response.status_code}"
            )
            if passed:
                self.passed += 1
            else:
                self.failed += 1
        except Exception as e:
            test_result("GET /api/products/?status=low_stock - Filter by status", False, str(e))
            self.failed += 1

        # Test 1.4: Search products
        try:
            response = requests.get(
                f"{self.base_url}/?search=Bread",
                headers=self.headers
            )
            passed = response.status_code == 200 and response.json().get('count', 0) > 0
            test_result(
                "GET /api/products/?search=Bread - Search functionality",
                passed,
                f"Status: {response.status_code}, Results: {response.json().get('count', 0)}"
            )
            if passed:
                self.passed += 1
            else:
                self.failed += 1
        except Exception as e:
            test_result("GET /api/products/?search=Bread - Search functionality", False, str(e))
            self.failed += 1

    # ==========================================
    # TEST GROUP 2: Get Product Details
    # ==========================================
    def test_group_2_get_details(self):
        """Test getting product details"""
        print_header("TEST GROUP 2: Get Product Details")

        # Get first product
        try:
            response = requests.get(f"{self.base_url}/", headers=self.headers)
            if response.status_code == 200 and response.json().get('results'):
                product_id = response.json()['results'][0]['id']
                self.test_product_id = product_id

                # Test 2.1: Get product details
                response = requests.get(
                    f"{self.base_url}/{product_id}/",
                    headers=self.headers
                )
                passed = response.status_code == 200
                data = response.json()
                test_result(
                    f"GET /api/products/{product_id}/ - Get product details",
                    passed,
                    f"Status: {response.status_code}, Product: {data.get('product_id', 'N/A')}"
                )
                if passed:
                    self.passed += 1
                    # Test profit margin is calculated
                    has_margin = 'profit_margin' in data
                    test_result(
                        "Profit margin calculated",
                        has_margin,
                        f"Margin: {data.get('profit_margin', 'N/A')}%"
                    )
                    if has_margin:
                        self.passed += 1
                    else:
                        self.failed += 1
                else:
                    self.failed += 2
        except Exception as e:
            test_result("Get product details", False, str(e))
            self.failed += 2

    # ==========================================
    # TEST GROUP 3: Create Products
    # ==========================================
    def test_group_3_create(self):
        """Test creating new products"""
        print_header("TEST GROUP 3: Create Products")

        # Test 3.1: Create product with valid data
        try:
            product_data = {
                "category_id": 1,
                "name": f"Test Bread {datetime.now().timestamp()}",
                "description": "Test product",
                "cost_price": "50.00",
                "selling_price": "100.00",
                "current_stock": "10",
                "shelf_life": 3,
                "shelf_unit": "days"
            }
            response = requests.post(
                f"{self.base_url}/",
                headers=self.headers,
                json=product_data
            )
            passed = response.status_code == 201
            test_result(
                "POST /api/products/ - Create product",
                passed,
                f"Status: {response.status_code}"
            )
            if passed:
                self.passed += 1
                created_id = response.json().get('id')
                if created_id:
                    self.test_product_id = created_id
            else:
                self.failed += 1
                test_result("Create product error", False, response.json())
        except Exception as e:
            test_result("POST /api/products/ - Create product", False, str(e))
            self.failed += 1

        # Test 3.2: Validation - selling_price must be > cost_price
        try:
            invalid_data = {
                "category_id": 1,
                "name": f"Invalid {datetime.now().timestamp()}",
                "cost_price": "100.00",
                "selling_price": "50.00",  # Invalid: selling < cost
                "shelf_life": 1,
                "shelf_unit": "days"
            }
            response = requests.post(
                f"{self.base_url}/",
                headers=self.headers,
                json=invalid_data
            )
            passed = response.status_code == 400
            test_result(
                "Validation: selling_price > cost_price",
                passed,
                f"Status: {response.status_code}, Error: {response.json().get('selling_price', 'N/A')}"
            )
            if passed:
                self.passed += 1
            else:
                self.failed += 1
        except Exception as e:
            test_result("Validation test", False, str(e))
            self.failed += 1

    # ==========================================
    # TEST GROUP 4: Update Products
    # ==========================================
    def test_group_4_update(self):
        """Test updating products"""
        print_header("TEST GROUP 4: Update Products")

        if not self.test_product_id:
            print("  ⚠ Skipping update tests - no product ID available")
            return

        # Test 4.1: PATCH update
        try:
            update_data = {
                "current_stock": "25",
                "selling_price": "120.00"
            }
            response = requests.patch(
                f"{self.base_url}/{self.test_product_id}/",
                headers=self.headers,
                json=update_data
            )
            passed = response.status_code == 200
            test_result(
                f"PATCH /api/products/{self.test_product_id}/ - Update product",
                passed,
                f"Status: {response.status_code}"
            )
            if passed:
                self.passed += 1
            else:
                self.failed += 1
        except Exception as e:
            test_result("PATCH update product", False, str(e))
            self.failed += 1

    # ==========================================
    # TEST GROUP 5: Custom Actions
    # ==========================================
    def test_group_5_custom_actions(self):
        """Test custom product endpoints"""
        print_header("TEST GROUP 5: Custom Actions")

        # Test 5.1: Low-stock products
        try:
            response = requests.get(
                f"{self.base_url}/low-stock/",
                headers=self.headers
            )
            passed = response.status_code == 200
            test_result(
                "GET /api/products/low-stock/ - Low stock products",
                passed,
                f"Status: {response.status_code}, Count: {response.json().get('count', 0)}"
            )
            if passed:
                self.passed += 1
            else:
                self.failed += 1
        except Exception as e:
            test_result("GET /api/products/low-stock/", False, str(e))
            self.failed += 1

        # Test 5.2: Out-of-stock products
        try:
            response = requests.get(
                f"{self.base_url}/out-of-stock/",
                headers=self.headers
            )
            passed = response.status_code == 200
            test_result(
                "GET /api/products/out-of-stock/ - Out of stock products",
                passed,
                f"Status: {response.status_code}, Count: {response.json().get('count', 0)}"
            )
            if passed:
                self.passed += 1
            else:
                self.failed += 1
        except Exception as e:
            test_result("GET /api/products/out-of-stock/", False, str(e))
            self.failed += 1

        # Test 5.3: Products by category
        try:
            response = requests.get(
                f"{self.base_url}/by-category/1/",
                headers=self.headers
            )
            passed = response.status_code == 200
            test_result(
                "GET /api/products/by-category/1/ - Products by category",
                passed,
                f"Status: {response.status_code}, Count: {response.json().get('count', 0)}"
            )
            if passed:
                self.passed += 1
            else:
                self.failed += 1
        except Exception as e:
            test_result("GET /api/products/by-category/1/", False, str(e))
            self.failed += 1

    # ==========================================
    # TEST GROUP 6: Delete Product
    # ==========================================
    def test_group_6_delete(self):
        """Test deleting products"""
        print_header("TEST GROUP 6: Delete Product")

        if not self.test_product_id:
            print("  ⚠ Skipping delete test - no product ID available")
            return

        try:
            response = requests.delete(
                f"{self.base_url}/{self.test_product_id}/",
                headers=self.headers
            )
            passed = response.status_code == 204
            test_result(
                f"DELETE /api/products/{self.test_product_id}/ - Delete product",
                passed,
                f"Status: {response.status_code}"
            )
            if passed:
                self.passed += 1
            else:
                self.failed += 1
        except Exception as e:
            test_result("DELETE product", False, str(e))
            self.failed += 1

    # ==========================================
    # TEST GROUP 7: Permissions
    # ==========================================
    def test_group_7_permissions(self):
        """Test permission checks"""
        print_header("TEST GROUP 7: Permissions")

        # Test 7.1: Read-only for all roles
        try:
            response = requests.get(f"{self.base_url}/", headers=self.headers)
            passed = response.status_code == 200
            test_result(
                "GET /api/products/ - Authenticated users can read",
                passed,
                f"Status: {response.status_code}"
            )
            if passed:
                self.passed += 1
            else:
                self.failed += 1
        except Exception as e:
            test_result("Read permission test", False, str(e))
            self.failed += 1

    # ==========================================
    # TEST GROUP 8: Validation
    # ==========================================
    def test_group_8_validation(self):
        """Test input validation"""
        print_header("TEST GROUP 8: Validation")

        # Test 8.1: Cost price must be positive
        try:
            invalid_data = {
                "category_id": 1,
                "name": f"Test {datetime.now().timestamp()}",
                "cost_price": "0",  # Invalid
                "selling_price": "100.00",
                "shelf_life": 1,
                "shelf_unit": "days"
            }
            response = requests.post(
                f"{self.base_url}/",
                headers=self.headers,
                json=invalid_data
            )
            passed = response.status_code == 400
            test_result(
                "Validation: cost_price > 0",
                passed,
                f"Status: {response.status_code}"
            )
            if passed:
                self.passed += 1
            else:
                self.failed += 1
        except Exception as e:
            test_result("Cost price validation", False, str(e))
            self.failed += 1

    # ==========================================
    # TEST GROUP 9: Profit Margin Calculation
    # ==========================================
    def test_group_9_calculations(self):
        """Test calculated fields"""
        print_header("TEST GROUP 9: Profit Margin Calculation")

        try:
            response = requests.get(f"{self.base_url}/", headers=self.headers)
            if response.status_code == 200 and response.json().get('results'):
                product = response.json()['results'][0]
                
                # Verify profit margin calculation
                cost = Decimal(str(product.get('cost_price', 0)))
                selling = Decimal(str(product.get('selling_price', 0)))
                margin = product.get('profit_margin', 0)
                
                if cost > 0:
                    expected_margin = float((selling - cost) / cost * 100)
                    is_correct = abs(float(margin) - expected_margin) < 0.1
                    
                    test_result(
                        "Profit margin calculated correctly",
                        is_correct,
                        f"Expected: {expected_margin:.2f}%, Got: {margin}%"
                    )
                    if is_correct:
                        self.passed += 1
                    else:
                        self.failed += 1
        except Exception as e:
            test_result("Profit margin calculation", False, str(e))
            self.failed += 1

    # ==========================================
    # Print Summary
    # ==========================================
    def print_summary(self):
        """Print test summary"""
        total = self.passed + self.failed
        pass_percentage = (self.passed / total * 100) if total > 0 else 0

        print_header("TEST SUMMARY")
        print(f"  Total Tests: {total}")
        print(f"  {Colors.GREEN}Passed: {self.passed}{Colors.END}")
        print(f"  {Colors.RED}Failed: {self.failed}{Colors.END}")
        print(f"  Success Rate: {pass_percentage:.1f}%\n")

        if self.failed == 0:
            print(f"{Colors.GREEN}✓ ALL TESTS PASSED!{Colors.END}\n")
        else:
            print(f"{Colors.RED}✗ Some tests failed. Please review.{Colors.END}\n")


if __name__ == "__main__":
    tester = TestProductAPI()
    tester.run_all_tests()
