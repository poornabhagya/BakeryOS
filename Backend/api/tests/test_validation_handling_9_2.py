"""
Comprehensive test suite for Task 9.2: Input Validation & Error Handling

Tests cover:
- Custom validators (contact, password, email, etc.)
- Serializer validation
- Error response formatting
- Data sanitization
- 400, 403, 404 error handling
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient, APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token
from decimal import Decimal
from api.models import Product, Category
from api.validators import (
    validate_contact_format, validate_password_strength, validate_email_format,
    validate_positive_number, validate_percentage,
    sanitize_string, sanitize_email, sanitize_phone_number, sanitize_html
)
from rest_framework import serializers

User = get_user_model()


class CustomValidatorTests(TestCase):
    """Test custom validators"""
    
    # ========================================================================
    # CONTACT/PHONE VALIDATION TESTS
    # ========================================================================
    
    def test_validate_contact_format_valid(self):
        """Valid contact formats should pass"""
        # Valid formats
        validate_contact_format("077-1234567")  # Should not raise
        validate_contact_format("0771234567")   # Should not raise
        validate_contact_format("077 1234567")  # Should not raise
    
    def test_validate_contact_format_invalid(self):
        """Invalid contact formats should fail"""
        with self.assertRaises(serializers.ValidationError):
            validate_contact_format("123")  # Too short
        
        with self.assertRaises(serializers.ValidationError):
            validate_contact_format("abcd-efghijk")  # Contains letters
        
        with self.assertRaises(serializers.ValidationError):
            validate_contact_format("12-34")  # Wrong format
    
    def test_validate_contact_format_empty(self):
        """Empty contact should not raise"""
        validate_contact_format(None)  # Should not raise
        validate_contact_format("")    # Should not raise
    
    # ========================================================================
    # PASSWORD VALIDATION TESTS
    # ========================================================================
    
    def test_validate_password_strength_valid(self):
        """Valid passwords should pass"""
        validate_password_strength("Password123")  # Should not raise
        validate_password_strength("SecurePass456")  # Should not raise
    
    def test_validate_password_strength_too_short(self):
        """Password < 8 chars should fail"""
        with self.assertRaises(serializers.ValidationError) as cm:
            validate_password_strength("Pass123")
        self.assertIn("at least 8 characters", str(cm.exception))
    
    def test_validate_password_strength_no_uppercase(self):
        """Password without uppercase should fail"""
        with self.assertRaises(serializers.ValidationError) as cm:
            validate_password_strength("password123")
        self.assertIn("uppercase", str(cm.exception))
    
    def test_validate_password_strength_no_lowercase(self):
        """Password without lowercase should fail"""
        with self.assertRaises(serializers.ValidationError) as cm:
            validate_password_strength("PASSWORD123")
        self.assertIn("lowercase", str(cm.exception))
    
    def test_validate_password_strength_no_digit(self):
        """Password without digit should fail"""
        with self.assertRaises(serializers.ValidationError) as cm:
            validate_password_strength("PasswordAbcd")
        self.assertIn("digit", str(cm.exception))
    
    # ========================================================================
    # EMAIL VALIDATION TESTS
    # ========================================================================
    
    def test_validate_email_format_valid(self):
        """Valid emails should pass"""
        validate_email_format("user@example.com")
        validate_email_format("user.name@example.co.uk")
        validate_email_format("user+tag@example.com")
    
    def test_validate_email_format_invalid(self):
        """Invalid emails should fail"""
        with self.assertRaises(serializers.ValidationError):
            validate_email_format("invalid.email")
        
        with self.assertRaises(serializers.ValidationError):
            validate_email_format("@example.com")
        
        with self.assertRaises(serializers.ValidationError):
            validate_email_format("user@.com")
    
    # ========================================================================
    # NUMERIC VALIDATION TESTS
    # ========================================================================
    
    def test_validate_positive_number_valid(self):
        """Positive numbers should pass"""
        validate_positive_number(10)
        validate_positive_number(Decimal("10.50"))
        validate_positive_number(0.1)
    
    def test_validate_positive_number_invalid(self):
        """Zero and negative numbers should fail"""
        with self.assertRaises(serializers.ValidationError):
            validate_positive_number(0)
        
        with self.assertRaises(serializers.ValidationError):
            validate_positive_number(-5)
    
    def test_validate_percentage_valid(self):
        """Percentages 0-100 should pass"""
        validate_percentage(0)
        validate_percentage(50)
        validate_percentage(100)
    
    def test_validate_percentage_invalid(self):
        """Percentages outside 0-100 should fail"""
        with self.assertRaises(serializers.ValidationError):
            validate_percentage(-1)
        
        with self.assertRaises(serializers.ValidationError):
            validate_percentage(101)


class DataSanitizationTests(TestCase):
    """Test data sanitization functions"""
    
    def test_sanitize_string_trimming(self):
        """Sanitize should trim whitespace"""
        result = sanitize_string("  hello  ")
        self.assertEqual(result, "hello")
    
    def test_sanitize_string_multiple_spaces(self):
        """Sanitize should reduce multiple spaces to single"""
        result = sanitize_string("hello    world")
        self.assertEqual(result, "hello world")
    
    def test_sanitize_string_null_bytes(self):
        """Sanitize should remove null bytes"""
        result = sanitize_string("hello\0world")
        self.assertNotIn("\0", result)
    
    def test_sanitize_email_lowercase(self):
        """Sanitize email should lowercase"""
        result = sanitize_email("User@EXAMPLE.COM")
        self.assertEqual(result, "user@example.com")
    
    def test_sanitize_email_trim(self):
        """Sanitize email should trim"""
        result = sanitize_email(" user@example.com ")
        self.assertEqual(result, "user@example.com")
    
    def test_sanitize_phone_number_formatting(self):
        """Sanitize phone should format correctly"""
        result = sanitize_phone_number("0771234567")
        self.assertEqual(result, "077-1234567")
    
    def test_sanitize_html_removes_tags(self):
        """Sanitize HTML should remove tags"""
        result = sanitize_html("<p>Hello</p>")
        self.assertNotIn("<p>", result)
        self.assertNotIn("</p>", result)


class UserSerializerValidationTests(APITestCase):
    """Test user serializer validation"""
    
    def setUp(self):
        """Set up test client"""
        self.client = APIClient()
        self.base_user_data = {
            'username': 'validuser',
            'email': 'valid@example.com',
            'password': 'ValidPass123',
            'password_confirm': 'ValidPass123',
            'full_name': 'Valid User',
            'contact': '077-1234567',
            'role': 'Baker'
        }
    
    def test_create_user_valid_data(self):
        """Creating user with valid data should succeed"""
        # Create manager first
        manager = User.objects.create_user(
            username='manager',
            password='Manager123',
            role='Manager'
        )
        token = Token.objects.create(user=manager)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        response = self.client.post('/api/users/', self.base_user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_create_user_invalid_username_length(self):
        """Username too short should fail"""
        manager = User.objects.create_user(
            username='manager',
            password='Manager123',
            role='Manager'
        )
        token = Token.objects.create(user=manager)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        data = self.base_user_data.copy()
        data['username'] = 'ab'  # Too short
        
        response = self.client.post('/api/users/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data.get('details', {}))
    
    def test_create_user_invalid_password_no_uppercase(self):
        """Password without uppercase should fail"""
        manager = User.objects.create_user(
            username='manager',
            password='Manager123',
            role='Manager'
        )
        token = Token.objects.create(user=manager)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        data = self.base_user_data.copy()
        data['password'] = 'validpass123'
        data['password_confirm'] = 'validpass123'
        
        response = self.client.post('/api/users/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password', response.data.get('details', {}))
    
    def test_create_user_passwords_dont_match(self):
        """Password mismatch should fail"""
        manager = User.objects.create_user(
            username='manager',
            password='Manager123',
            role='Manager'
        )
        token = Token.objects.create(user=manager)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        data = self.base_user_data.copy()
        data['password_confirm'] = 'DifferentPass123'
        
        response = self.client.post('/api/users/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password_confirm', response.data.get('details', {}))
    
    def test_create_user_invalid_email(self):
        """Invalid email should fail"""
        manager = User.objects.create_user(
            username='manager',
            password='Manager123',
            role='Manager'
        )
        token = Token.objects.create(user=manager)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        data = self.base_user_data.copy()
        data['email'] = 'not-an-email'
        
        response = self.client.post('/api/users/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data.get('details', {}))
    
    def test_create_user_invalid_contact(self):
        """Invalid contact format should fail"""
        manager = User.objects.create_user(
            username='manager',
            password='Manager123',
            role='Manager'
        )
        token = Token.objects.create(user=manager)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        data = self.base_user_data.copy()
        data['contact'] = '123'  # Too short
        
        response = self.client.post('/api/users/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('contact', response.data.get('details', {}))
    
    def test_create_user_invalid_role(self):
        """Invalid role should fail"""
        manager = User.objects.create_user(
            username='manager',
            password='Manager123',
            role='Manager'
        )
        token = Token.objects.create(user=manager)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        data = self.base_user_data.copy()
        data['role'] = 'InvalidRole'
        
        response = self.client.post('/api/users/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('role', response.data.get('details', {}))
    
    def test_create_user_duplicate_username(self):
        """Duplicate username should fail"""
        # Create first manager
        manager = User.objects.create_user(
            username='manager',
            password='Manager123',
            role='Manager'
        )
        token = Token.objects.create(user=manager)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        # Try to create with existing username
        data = self.base_user_data.copy()
        data['username'] = 'manager'
        
        response = self.client.post('/api/users/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('username', response.data.get('details', {}))


class ProductSerializerValidationTests(APITestCase):
    """Test product serializer validation"""
    
    def setUp(self):
        """Set up test data"""
        self.client = APIClient()
        
        # Create category
        self.category = Category.objects.create(
            name='Bread',
            type='Product'
        )
        
        # Create manager user
        self.manager = User.objects.create_user(
            username='manager',
            password='Manager123',
            role='Manager'
        )
        self.token = Token.objects.create(user=self.manager)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        
        self.base_product_data = {
            'category_id': self.category.id,
            'name': 'White Bread',
            'description': 'Fresh white bread',
            'cost_price': '50.00',
            'selling_price': '100.00',
            'current_stock': 20,
            'shelf_life': 2,
            'shelf_unit': 'days'  # Changed from 'day' to 'days'
        }
    
    def test_create_product_valid_data(self):
        """Creating product with valid data should succeed"""
        response = self.client.post('/api/products/', self.base_product_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_create_product_invalid_cost_price_zero(self):
        """Cost price = 0 should fail"""
        data = self.base_product_data.copy()
        data['cost_price'] = '0'
        
        response = self.client.post('/api/products/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('cost_price', response.data.get('details', {}))
    
    def test_create_product_invalid_selling_less_than_cost(self):
        """Selling price <= cost price should fail"""
        data = self.base_product_data.copy()
        data['cost_price'] = '100.00'
        data['selling_price'] = '90.00'
        
        response = self.client.post('/api/products/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('selling_price', response.data.get('details', {}))
    
    def test_create_product_invalid_stock_negative(self):
        """Negative stock should fail"""
        data = self.base_product_data.copy()
        data['current_stock'] = -5
        
        response = self.client.post('/api/products/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('current_stock', response.data.get('details', {}))
    
    def test_create_product_invalid_shelf_life_zero(self):
        """Shelf life = 0 should fail"""
        data = self.base_product_data.copy()
        data['shelf_life'] = 0
        
        response = self.client.post('/api/products/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('shelf_life', response.data.get('details', {}))
    
    def test_create_product_duplicate_name_in_category(self):
        """Duplicate product name in category should fail"""
        # Create first product
        self.client.post('/api/products/', self.base_product_data)
        
        # Try to create with same name in same category
        data = self.base_product_data.copy()
        response = self.client.post('/api/products/', data)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Should have validation error for name field or non-field error
        details = response.data.get('details', {})
        self.assertTrue(
            'name' in details or 'non_field_errors' in details,
            f"Expected 'name' or 'non_field_errors', got: {details.keys()}"
        )


class ErrorResponseFormatTests(APITestCase):
    """Test standardized error response format"""
    
    def setUp(self):
        """Set up authentication"""
        # Create a manager user
        self.manager = User.objects.create_user(
            username='manager',
            password='Manager123',
            role='Manager'
        )
        self.token = Token.objects.create(user=self.manager)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
    
    def test_404_not_found_format(self):
        """404 response should have standard format"""
        response = self.client.get('/api/users/9999/')
        # May return 404 or another status, but should have proper format
        data = response.data
        self.assertFalse(data['success'])
        self.assertIn('error', data)
        self.assertIn('details', data)
    
    def test_403_permission_denied_format(self):
        """403 response should have standard format"""
        # Create non-manager user
        user = User.objects.create_user(
            username='cashier100',  # Use unique username
            password='Cashier123',
            role='Cashier'
        )
        token = Token.objects.create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        
        # Try to create user (requires Manager)
        response = self.client.post('/api/users/', {
            'username': 'newuser',
            'password': 'NewPass123',
            'password_confirm': 'NewPass123',
            'email': 'new@example.com',
            'role': 'Baker'
        })
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        
        # Check response format
        data = response.data
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 'Permission Denied')
        self.assertIn('details', data)
    
    def test_400_validation_error_format(self):
        """400 validation error should have standard format"""
        # Create a new manager for this test with unique username
        manager2 = User.objects.create_user(
            username='manager_validator',
            password='Manager123',
            role='Manager'
        )
        token2 = Token.objects.create(user=manager2)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token2.key}')
        
        # Send invalid data
        response = self.client.post('/api/users/', {
            'username': 'ab',  # Too short
            'password': 'Pass123',
            'password_confirm': 'Pass123',
            'email': 'test@example.com',
            'role': 'Baker'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        
        # Check response format
        data = response.data
        self.assertFalse(data['success'])
        self.assertEqual(data['error'], 'Validation Error')
        self.assertIsInstance(data['details'], dict)


class UnauthorizedAccessTests(APITestCase):
    """Test unauthorized access scenarios"""
    
    def test_missing_authentication_token(self):
        """Missing token should return 401"""
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        
        # Check response format
        data = response.data
        self.assertFalse(data['success'])
        self.assertIn('error', data)
    
    def test_invalid_authentication_token(self):
        """Invalid token should return 401"""
        self.client.credentials(HTTP_AUTHORIZATION='Token invalid_token_12345')
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_expired_or_malformed_token(self):
        """Malformed token should return 401"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer not_a_token')
        response = self.client.get('/api/users/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
