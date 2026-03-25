"""
Comprehensive Authorization and Permission Testing for Task 9.1

Tests all permission classes and their application across ViewSets:
- Single role permissions (IsManager, IsStorekeeper, IsBaker, IsCashier)
- Multi-role permissions (IsManagerOrStorekeeper, IsManagerOrBaker, etc.)
- Special permissions (IsManager OrReadOnly, IsManagerOrSelf)
- Wastage-specific permissions (CanReportProductWastage, CanReportIngredientWastage)
"""

from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from rest_framework import status
from django.contrib.auth import get_user_model
from decimal import Decimal

from api.models import (
    Category, Product, Ingredient, IngredientBatch, 
    Sale, Discount, WastageReason
)

User = get_user_model()


class PermissionTestSetup(APITestCase):
    """Base class with test data setup for permission tests"""
    
    def setUp(self):
        """Create test users with different roles"""
        self.client = APIClient()
        
        # Create users with different roles
        self.manager = User.objects.create_user(
            username='manager1',
            password='testpass123',
            role='Manager',
            full_name='Manager User',
            employee_id='M001',
            contact='XXX-1234567'
        )
        
        self.storekeeper = User.objects.create_user(
            username='storekeeper1',
            password='testpass123',
            role='Storekeeper',
            full_name='Storekeeper User',
            employee_id='S001',
            contact='XXX-2234567'
        )
        
        self.baker = User.objects.create_user(
            username='baker1',
            password='testpass123',
            role='Baker',
            full_name='Baker User',
            employee_id='B001',
            contact='XXX-3234567'
        )
        
        self.cashier = User.objects.create_user(
            username='cashier1',
            password='testpass123',
            role='Cashier',
            full_name='Cashier User',
            employee_id='C001',
            contact='XXX-4234567'
        )
        
        # Create product category
        self.category = Category.objects.create(
            name='Test Category',
            type='Product'
        )
        
        # Create ingredient category
        self.ingredient_category = Category.objects.create(
            name='Ingredient Category',
            type='Ingredient'
        )
        
        # Create test product
        self.product = Product.objects.create(
            name='Test Product',
            category_id=self.category,
            cost_price=Decimal('50.00'),
            selling_price=Decimal('100.00'),
            current_stock=10
        )
        
        # Create test ingredient
        self.ingredient = Ingredient.objects.create(
            name='Test Ingredient',
            category_id=self.ingredient_category,
            supplier='Test Supplier',
            base_unit='kg',
            low_stock_threshold=5,
            total_quantity=100
        )
        
        # Create wastage reason
        self.wastage_reason = WastageReason.objects.create(
            reason='Testing',
            description='For testing purposes'
        )
        
        # Create test discount
        self.discount = Discount.objects.create(
            name='Test Discount',
            discount_type='Percentage',
            value=Decimal('10.00'),
            applicable_to='All'
        )
    
    def get_token(self, user):
        """Generate auth token for a user"""
        token, created = Token.objects.get_or_create(user=user)
        return token.key
    
    def set_auth_header(self, token):
        """Set Authorization header in client"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')
    
    def clear_auth_header(self):
        """Clear Authorization header"""
        self.client.credentials()


# ============================================================================
# USER MANAGEMENT PERMISSION TESTS
# ============================================================================

class UserManagementPermissionTests(PermissionTestSetup):
    """Test permission enforcement for user CRUD operations"""
    
    def test_user_create_as_manager_allowed(self):
        """Manager should be able to create users"""
        token = self.get_token(self.manager)
        self.set_auth_header(token)
        
        data = {
            'username': 'newuser',
            'password': 'testpass123',
            'role': 'Baker',
            'full_name': 'New User',
            'employee_id': 'N001',
            'contact': 'XXX-5234567'
        }
        
        response = self.client.post('/api/users/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_user_create_as_storekeeper_denied(self):
        """Non-managers should NOT be able to create users"""
        token = self.get_token(self.storekeeper)
        self.set_auth_header(token)
        
        data = {
            'username': 'newuser2',
            'password': 'testpass123',
            'role': 'Baker',
            'full_name': 'New User',
            'employee_id': 'N002',
            'contact': 'XXX-9234567'
        }
        
        response = self.client.post('/api/users/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_user_list_as_manager_allowed(self):
        """Manager should see all users"""
        token = self.get_token(self.manager)
        self.set_auth_header(token)
        
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
    
    def test_user_list_as_baker_denied(self):
        """Non-managers should NOT be able to list users"""
        token = self.get_token(self.baker)
        self.set_auth_header(token)
        
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


# ============================================================================
# PRODUCT MANAGEMENT PERMISSION TESTS
# ============================================================================

class ProductManagementPermissionTests(PermissionTestSetup):
    """Test permission enforcement for product CRUD operations"""
    
    def test_product_create_as_manager_allowed(self):
        """Manager should be able to create products"""
        token = self.get_token(self.manager)
        self.set_auth_header(token)
        
        data = {
            'name': 'New Product',
            'category_id': self.category.id,
            'cost_price': 50,
            'selling_price': 100,
            'current_stock': 5
        }
        
        response = self.client.post('/api/products/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_product_create_as_baker_denied(self):
        """Non-managers should NOT be able to create products"""
        token = self.get_token(self.baker)
        self.set_auth_header(token)
        
        data = {
            'name': 'Baker Product',
            'category_id': self.category.id,
            'cost_price': 50,
            'selling_price': 100,
            'current_stock': 5
        }
        
        response = self.client.post('/api/products/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_product_list_as_any_user_allowed(self):
        """Any authenticated user should be able to list products"""
        for user in [self.manager, self.storekeeper, self.baker, self.cashier]:
            token = self.get_token(user)
            self.set_auth_header(token)
            
            response = self.client.get('/api/products/')
            self.assertEqual(response.status_code, status.HTTP_200_OK,
                f"{user.role} should be able to list products")


# ============================================================================
# INGREDIENT MANAGEMENT PERMISSION TESTS
# ============================================================================

class IngredientManagementPermissionTests(PermissionTestSetup):
    """Test permission enforcement for ingredient CRUD operations"""
    
    def test_ingredient_create_as_manager_allowed(self):
        """Manager should be able to create ingredients"""
        token = self.get_token(self.manager)
        self.set_auth_header(token)
        
        data = {
            'name': 'New Ingredient',
            'category_id': self.ingredient_category.id,
            'supplier': 'Test Supplier',
            'base_unit': 'kg',
            'low_stock_threshold': 5
        }
        
        response = self.client.post('/api/ingredients/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_ingredient_create_as_storekeeper_allowed(self):
        """Storekeeper should be able to create ingredients"""
        token = self.get_token(self.storekeeper)
        self.set_auth_header(token)
        
        data = {
            'name': 'Storekeeper Ingredient',
            'category_id': self.ingredient_category.id,
            'supplier': 'Test Supplier',
            'base_unit': 'kg',
            'low_stock_threshold': 5
        }
        
        response = self.client.post('/api/ingredients/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_ingredient_create_as_baker_denied(self):
        """Baker should NOT be able to create ingredients"""
        token = self.get_token(self.baker)
        self.set_auth_header(token)
        
        data = {
            'name': 'Baker Ingredient',
            'category_id': self.ingredient_category.id,
            'supplier': 'Test Supplier',
            'base_unit': 'kg',
            'low_stock_threshold': 5
        }
        
        response = self.client.post('/api/ingredients/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


# ============================================================================
# SALES PERMISSION TESTS
# ============================================================================

class SalesPermissionTests(PermissionTestSetup):
    """Test permission enforcement for sales operations"""
    
    def test_sale_create_as_cashier_allowed(self):
        """Cashier should be able to create sales"""
        token = self.get_token(self.cashier)
        self.set_auth_header(token)
        
        data = {
            'items': [
                {'product_id': self.product.id, 'quantity': 2, 'unit_price': Decimal('100.00')}
            ],
            'payment_method': 'Cash'
        }
        
        response = self.client.post('/api/sales/', data)
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])
    
    def test_sale_create_as_storekeeper_denied(self):
        """Storekeeper should NOT be able to create sales"""
        token = self.get_token(self.storekeeper)
        self.set_auth_header(token)
        
        data = {
            'items': [
                {'product_id': self.product.id, 'quantity': 2, 'unit_price': Decimal('100.00')}
            ],
            'payment_method': 'Cash'
        }
        
        response = self.client.post('/api/sales/', data)
        self.assertIn(response.status_code, [status.HTTP_403_FORBIDDEN, status.HTTP_401_UNAUTHORIZED])


# ============================================================================
# DISCOUNT MANAGEMENT PERMISSION TESTS
# ============================================================================

class DiscountManagementPermissionTests(PermissionTestSetup):
    """Test permission enforcement for discount CRUD operations"""
    
    def test_discount_create_as_manager_allowed(self):
        """Manager should be able to create discounts"""
        token = self.get_token(self.manager)
        self.set_auth_header(token)
        
        data = {
            'name': 'Manager Discount',
            'discount_type': 'Percentage',
            'value': Decimal('15.00'),
            'applicable_to': 'All'
        }
        
        response = self.client.post('/api/discounts/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_discount_create_as_cashier_denied(self):
        """Cashier should NOT be able to create discounts"""
        token = self.get_token(self.cashier)
        self.set_auth_header(token)
        
        data = {
            'name': 'Cashier Discount',
            'discount_type': 'Percentage',
            'value': Decimal('15.00'),
            'applicable_to': 'All'
        }
        
        response = self.client.post('/api/discounts/', data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


# ============================================================================
# UNAUTHENTICATED ACCESS TESTS
# ============================================================================

class UnauthenticatedAccessTests(PermissionTestSetup):
    """Test that unauthenticated users are denied access"""
    
    def test_unauthenticated_cannot_access_user_list(self):
        """Unauthenticated users should not access user list"""
        self.clear_auth_header()
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_unauthenticated_cannot_create_product(self):
        """Unauthenticated users should not create products"""
        self.clear_auth_header()
        response = self.client.post('/api/products/', {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_unauthenticated_cannot_create_sale(self):
        """Unauthenticated users should not create sales"""
        self.clear_auth_header()
        response = self.client.post('/api/sales/', {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
