"""
Tests for Task 2.2: Token Authentication
Testing: Login, Logout, Me endpoints, and Token generation
"""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework.authtoken.models import Token

User = get_user_model()


class AuthenticationSetupTests(APITestCase):
    """Test that authentication system is properly configured"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            full_name='Test User',
            role='Manager',
            email='test@example.com'
        )
    
    def test_login_endpoint_exists(self):
        """Test that login endpoint is accessible"""
        url = reverse('login')  # or '/api/auth/login/'
        response = self.client.post(url, {})
        # Should fail with 401 (invalid credentials) not 404 (endpoint missing)
        self.assertNotEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_me_endpoint_exists(self):
        """Test that me endpoint is accessible"""
        token = Token.objects.get(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        url = reverse('me')  # or '/api/auth/me/'
        response = self.client.get(url)
        self.assertNotEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_logout_endpoint_exists(self):
        """Test that logout endpoint is accessible"""
        token = Token.objects.get(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        url = reverse('logout')  # or '/api/auth/logout/'
        response = self.client.post(url, {})
        self.assertNotEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class LoginEndpointTests(APITestCase):
    """Test the POST /api/auth/login/ endpoint"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            full_name='Test User',
            role='Manager',
            email='test@example.com'
        )
        self.login_url = reverse('login')
    
    # ✅ Valid Login Tests
    def test_login_with_valid_credentials(self):
        """Test successful login with correct username/password"""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('token', response.data)
        self.assertIn('user', response.data)
    
    def test_login_returns_user_info(self):
        """Test that login response includes correct user information"""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        user_data = response.data['user']
        self.assertEqual(user_data['username'], 'testuser')
        self.assertEqual(user_data['full_name'], 'Test User')
        self.assertEqual(user_data['role'], 'Manager')
        self.assertEqual(user_data['email'], 'test@example.com')
    
    def test_login_returns_valid_token(self):
        """Test that login returns a valid token that can be used"""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        token = response.data['token']
        
        # Token should be a string
        self.assertIsInstance(token, str)
        self.assertGreater(len(token), 0)
    
    def test_login_creates_token_in_database(self):
        """Test that login token is stored in database"""
        initial_token_count = Token.objects.count()
        
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Token should exist for this user
        token = Token.objects.get(user=self.user)
        self.assertIsNotNone(token)
        self.assertEqual(token.key, response.data['token'])
    
    # ❌ Invalid Login Tests
    def test_login_with_wrong_password(self):
        """Test login fails with incorrect password"""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertNotIn('token', response.data)
    
    def test_login_with_nonexistent_user(self):
        """Test login fails for non-existent username"""
        response = self.client.post(self.login_url, {
            'username': 'nonexistent',
            'password': 'anypassword'
        })
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_login_with_missing_username(self):
        """Test login fails when username is missing"""
        response = self.client.post(self.login_url, {
            'password': 'testpass123'
        })
        
        self.assertIn(response.status_code, [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_401_UNAUTHORIZED
        ])
    
    def test_login_with_missing_password(self):
        """Test login fails when password is missing"""
        response = self.client.post(self.login_url, {
            'username': 'testuser'
        })
        
        self.assertIn(response.status_code, [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_401_UNAUTHORIZED
        ])
    
    def test_login_with_inactive_user(self):
        """Test login fails for inactive users"""
        self.user.is_active = False
        self.user.save()
        
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_login_case_sensitive_username(self):
        """Test login username is case-sensitive"""
        response = self.client.post(self.login_url, {
            'username': 'TESTUSER',  # Wrong case
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class MeEndpointTests(APITestCase):
    """Test the GET /api/auth/me/ endpoint"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            full_name='Test User',
            role='Cashier',
            email='test@example.com',
            contact='077-1234567',
            nic='123456789V',
            employee_id='EMP-001'
        )
        self.token = Token.objects.get(user=self.user)
        self.me_url = reverse('me')
    
    def test_me_requires_authentication(self):
        """Test that /me endpoint requires authentication"""
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_me_with_valid_token(self):
        """Test getting current user info with valid token"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get(self.me_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'testuser')
        self.assertEqual(response.data['id'], self.user.id)
    
    def test_me_returns_all_user_fields(self):
        """Test that /me returns all required user fields"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get(self.me_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        required_fields = [
            'id', 'username', 'email', 'full_name', 'employee_id',
            'role', 'status', 'contact', 'nic', 'created_at', 'updated_at'
        ]
        for field in required_fields:
            self.assertIn(field, response.data)
    
    def test_me_with_invalid_token(self):
        """Test /me endpoint with invalid token"""
        self.client.credentials(HTTP_AUTHORIZATION='Token invalidtoken123')
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_me_with_malformed_auth_header(self):
        """Test /me with malformed Authorization header"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)  # Wrong scheme
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_me_shows_correct_user_data(self):
        """Test that /me returns authenticated user's data"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get(self.me_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)
        self.assertEqual(response.data['role'], self.user.role)
        self.assertEqual(response.data['contact'], self.user.contact)


class LogoutEndpointTests(APITestCase):
    """Test the POST /api/auth/logout/ endpoint"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            full_name='Test User',
            role='Baker'
        )
        self.token = Token.objects.get(user=self.user)
        self.logout_url = reverse('logout')
    
    def test_logout_requires_authentication(self):
        """Test that logout endpoint requires authentication"""
        response = self.client.post(self.logout_url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_logout_with_valid_token(self):
        """Test successful logout with valid token"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.post(self.logout_url, {})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('detail', response.data)
    
    def test_logout_invalidates_token(self):
        """Test that logout invalidates the token"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        # First, verify token works
        me_url = reverse('me')
        response = self.client.get(me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Logout
        response = self.client.post(self.logout_url, {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Token should no longer work (optional - depends on implementation)
        # If using Token deletion:
        self.assertFalse(Token.objects.filter(user=self.user).exists())
    
    def test_logout_with_invalid_token(self):
        """Test logout with invalid token"""
        self.client.credentials(HTTP_AUTHORIZATION='Token invalidtoken')
        response = self.client.post(self.logout_url, {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_logout_prevents_future_requests(self):
        """Test that token cannot be used after logout"""
        # Logout
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        self.client.post(self.logout_url, {})
        
        # Try to use token for another request
        me_url = reverse('me')
        response = self.client.get(me_url)
        
        # Should fail (token deleted or invalidated)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class TokenAuthenticationTests(APITestCase):
    """Test Token Authentication mechanism"""
    
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='Manager'
        )
        self.token = Token.objects.get(user=self.user)
        self.me_url = reverse('me')
    
    def test_token_format(self):
        """Test that token is a valid string"""
        self.assertIsInstance(self.token.key, str)
        self.assertGreater(len(self.token.key), 10)
    
    def test_token_uniqueness(self):
        """Test that each user has unique token"""
        user2 = User.objects.create_user(
            username='testuser2',
            password='testpass123',
            role='Cashier'
        )
        token2 = Token.objects.get(user=user2)
        
        self.assertNotEqual(self.token.key, token2.key)
    
    def test_correct_auth_header_format(self):
        """Test correct Authorization header format: Token <key>"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_bearer_not_supported(self):
        """Test that Bearer scheme is not supported (Token uses Token scheme)"""
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + self.token.key)
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_missing_auth_header(self):
        """Test request without Authorization header fails"""
        response = self.client.get(self.me_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class RoleBasedAccessTests(APITestCase):
    """Test that all roles can authenticate"""
    
    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('login')
        self.me_url = reverse('me')
        
        # Create users with different roles
        self.roles = ['Manager', 'Cashier', 'Baker', 'Storekeeper']
        self.users = {}
        for role in self.roles:
            user = User.objects.create_user(
                username=f'user_{role.lower()}',
                password='testpass123',
                role=role
            )
            self.users[role] = user
    
    @pytest.mark.parametrize('role', ['Manager', 'Cashier', 'Baker', 'Storekeeper'])
    def test_all_roles_can_login(self, role):
        """Test that users with all roles can login"""
        response = self.client.post(self.login_url, {
            'username': f'user_{role.lower()}',
            'password': 'testpass123'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['user']['role'], role)
    
    @pytest.mark.parametrize('role', ['Manager', 'Cashier', 'Baker', 'Storekeeper'])
    def test_all_roles_can_access_me_endpoint(self, role):
        """Test that users with all roles can access /me endpoint"""
        user = self.users[role]
        token = Token.objects.get(user=user)
        
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        response = self.client.get(self.me_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['role'], role)


class ErrorHandlingTests(APITestCase):
    """Test error handling and edge cases"""
    
    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('login')
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='Manager'
        )
    
    def test_empty_request_body(self):
        """Test login with empty body"""
        response = self.client.post(self.login_url)
        self.assertIn(response.status_code, [
            status.HTTP_400_BAD_REQUEST,
            status.HTTP_401_UNAUTHORIZED
        ])
    
    def test_sql_injection_attempt(self):
        """Test that SQL injection is not possible"""
        response = self.client.post(self.login_url, {
            'username': "admin' OR '1'='1",
            'password': 'anything'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_special_characters_in_password(self):
        """Test login with special characters in password"""
        special_user = User.objects.create_user(
            username='special',
            password='p@$$w0rd!#%&',
            role='Manager'
        )
        
        response = self.client.post(self.login_url, {
            'username': 'special',
            'password': 'p@$$w0rd!#%&'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_very_long_username_attempt(self):
        """Test with very long username"""
        response = self.client.post(self.login_url, {
            'username': 'a' * 1000,
            'password': 'testpass123'
        })
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


# ==================== RUNNING TESTS ====================
# Run all tests:
# pytest Backend/api/tests.py -v
#
# Run specific test class:
# pytest Backend/api/tests.py::LoginEndpointTests -v
#
# Run specific test:
# pytest Backend/api/tests.py::LoginEndpointTests::test_login_with_valid_credentials -v
#
# Run with coverage:
# pytest Backend/api/tests.py --cov=api --cov-report=html
#
# Run by marker (if using @pytest.mark.XXX):
# pytest -m "slow"
