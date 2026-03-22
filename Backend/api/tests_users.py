"""
Tests for Task 2.3: User Management CRUD API
Testing all endpoints, permissions, serializers, and validation
"""

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework.authtoken.models import Token

User = get_user_model()


class UserListEndpointTests(APITestCase):
    """Test GET /api/users/ endpoint"""
    
    def setUp(self):
        self.client = APIClient()
        # Create test users with different roles
        self.manager = User.objects.create_user(
            username='manager1',
            password='TestPass123',
            full_name='Manager One',
            role='Manager'
        )
        self.cashier = User.objects.create_user(
            username='cashier1',
            password='TestPass123',
            full_name='Cashier One',
            role='Cashier'
        )
        self.baker = User.objects.create_user(
            username='baker1',
            password='TestPass123',
            full_name='Baker One',
            role='Baker'
        )
        # Create tokens for authentication
        self.manager_token = Token.objects.create(user=self.manager)
        self.cashier_token = Token.objects.create(user=self.cashier)
        self.baker_token = Token.objects.create(user=self.baker)
        self.list_url = reverse('user-list')
    
    def test_list_requires_authentication(self):
        """Test that list endpoint requires authentication"""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_list_requires_manager_role(self):
        """Test that only Manager can list all users"""
        token = Token.objects.get(user=self.cashier)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_manager_can_list_all_users(self):
        """Test that Manager can list all users"""
        token = Token.objects.get(user=self.manager)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data['results']), 3)  # At least 3 users created
    
    def test_list_excludes_password(self):
        """Test that password is not returned in list"""
        token = Token.objects.get(user=self.manager)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        for user in response.data['results']:
            self.assertNotIn('password', user)
    
    def test_list_filtering_by_role(self):
        """Test filtering users by role"""
        token = Token.objects.get(user=self.manager)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        
        url = f"{self.list_url}?role=Cashier"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        for user in response.data['results']:
            self.assertEqual(user['role'], 'Cashier')
    
    def test_list_filtering_by_status(self):
        """Test filtering users by status"""
        token = Token.objects.get(user=self.manager)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        
        url = f"{self.list_url}?status=active"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # All created users should be active
        for user in response.data['results']:
            self.assertEqual(user['status'], 'active')
    
    def test_list_search_by_username(self):
        """Test searching by username"""
        token = Token.objects.get(user=self.manager)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        
        url = f"{self.list_url}?search=manager1"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['username'], 'manager1')
    
    def test_list_ordering(self):
        """Test ordering by different fields"""
        token = Token.objects.get(user=self.manager)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        
        url = f"{self.list_url}?ordering=username"
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Results should be ordered by username
        if len(response.data['results']) > 1:
            usernames = [u['username'] for u in response.data['results']]
            self.assertEqual(usernames, sorted(usernames))


class UserCreateEndpointTests(APITestCase):
    """Test POST /api/users/ endpoint"""
    
    def setUp(self):
        self.client = APIClient()
        self.manager = User.objects.create_user(
            username='manager',
            password='TestPass123',
            role='Manager'
        )
        self.cashier = User.objects.create_user(
            username='cashier',
            password='TestPass123',
            role='Cashier'
        )
        # Create tokens for authentication
        self.manager_token = Token.objects.create(user=self.manager)
        self.cashier_token = Token.objects.create(user=self.cashier)
        self.create_url = reverse('user-list')
    
    def test_create_requires_authentication(self):
        """Test that create requires authentication"""
        response = self.client.post(self.create_url, {
            'username': 'newuser',
            'password': 'TestPass123',
            'password_confirm': 'TestPass123',
            'email': 'new@example.com',
            'full_name': 'New User',
            'role': 'Cashier'
        })
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_create_requires_manager_role(self):
        """Test that only Manager can create users"""
        token = Token.objects.get(user=self.cashier)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        
        response = self.client.post(self.create_url, {
            'username': 'newuser',
            'password': 'TestPass123',
            'password_confirm': 'TestPass123',
            'email': 'new@example.com',
            'full_name': 'New User',
            'role': 'Cashier'
        })
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_create_user_successfully(self):
        """Test successful user creation"""
        token = Token.objects.get(user=self.manager)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        
        response = self.client.post(self.create_url, {
            'username': 'newuser',
            'password': 'TestPass123',
            'password_confirm': 'TestPass123',
            'email': 'new@example.com',
            'full_name': 'New User',
            'contact': '077-1234567',
            'nic': '123456789V',
            'role': 'Baker'
        })
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['username'], 'newuser')
        self.assertEqual(response.data['role'], 'Baker')
        self.assertNotIn('password', response.data)
    
    def test_create_validates_password_strength(self):
        """Test password strength validation"""
        token = Token.objects.get(user=self.manager)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        
        invalid_passwords = [
            ('short', 'Too short (< 8 chars)'),
            ('nonuppercase123', 'no uppercase letter'),
            ('NOLOWERCASE123', 'no lowercase letter'),
            ('NoNumbersHere', 'no numbers'),
        ]
        
        for pwd, reason in invalid_passwords:
            response = self.client.post(self.create_url, {
                'username': f'user_{pwd}',
                'password': pwd,
                'password_confirm': pwd,
                'email': f'{pwd}@example.com',
                'full_name': 'Test User',
                'role': 'Cashier'
            })
            
            # Should fail validation
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST, 
                           f"Password validation failed for {reason}")
    
    def test_create_password_mismatch(self):
        """Test that passwords must match"""
        token = Token.objects.get(user=self.manager)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        
        response = self.client.post(self.create_url, {
            'username': 'newuser',
            'password': 'TestPass123',
            'password_confirm': 'TestPass124',  # Different
            'email': 'new@example.com',
            'full_name': 'New User',
            'role': 'Cashier'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('password_confirm', response.data)
    
    def test_create_duplicate_username(self):
        """Test that username must be unique"""
        token = Token.objects.get(user=self.manager)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        
        response = self.client.post(self.create_url, {
            'username': 'manager',  # Already exists
            'password': 'TestPass123',
            'password_confirm': 'TestPass123',
            'email': 'dup@example.com',
            'full_name': 'Duplicate',
            'role': 'Cashier'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_invalid_role(self):
        """Test that role must be valid"""
        token = Token.objects.get(user=self.manager)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        
        response = self.client.post(self.create_url, {
            'username': 'newuser',
            'password': 'TestPass123',
            'password_confirm': 'TestPass123',
            'email': 'new@example.com',
            'full_name': 'New User',
            'role': 'InvalidRole'
        })
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_create_generates_employee_id(self):
        """Test that employee_id is auto-generated"""
        token = Token.objects.get(user=self.manager)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        
        response = self.client.post(self.create_url, {
            'username': 'newuser',
            'password': 'TestPass123',
            'password_confirm': 'TestPass123',
            'email': 'new@example.com',
            'full_name': 'New User',
            'role': 'Baker'
        })
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNotNone(response.data['employee_id'])
        self.assertTrue(response.data['employee_id'].startswith('EMP-'))


class UserRetrieveEndpointTests(APITestCase):
    """Test GET /api/users/{id}/ endpoint"""
    
    def setUp(self):
        self.client = APIClient()
        self.manager = User.objects.create_user(
            username='manager',
            password='TestPass123',
            role='Manager'
        )
        self.cashier = User.objects.create_user(
            username='cashier',
            password='TestPass123',
            role='Cashier'
        )
        # Create tokens for authentication
        self.manager_token = Token.objects.create(user=self.manager)
        self.cashier_token = Token.objects.create(user=self.cashier)
    
    def test_retrieve_requires_authentication(self):
        """Test that retrieve requires authentication"""
        url = reverse('user-detail', kwargs={'pk': self.cashier.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_user_can_view_own_profile(self):
        """Test that users can view their own profile"""
        token = Token.objects.get(user=self.cashier)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        
        url = reverse('user-detail', kwargs={'pk': self.cashier.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'cashier')
    
    def test_user_cannot_view_others_profile(self):
        """Test that users cannot view other users' profiles (only Manager can)"""
        token = Token.objects.get(user=self.cashier)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        
        url = reverse('user-detail', kwargs={'pk': self.manager.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_manager_can_view_any_profile(self):
        """Test that Manager can view any user profile"""
        token = Token.objects.get(user=self.manager)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        
        url = reverse('user-detail', kwargs={'pk': self.cashier.id})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'cashier')


class UserUpdateEndpointTests(APITestCase):
    """Test PUT /api/users/{id}/ endpoint"""
    
    def setUp(self):
        self.client = APIClient()
        self.manager = User.objects.create_user(
            username='manager',
            password='TestPass123',
            role='Manager'
        )
        self.cashier = User.objects.create_user(
            username='cashier',
            password='TestPass123',
            full_name='Cashier One',
            role='Cashier'
        )        # Create tokens for authentication
        self.manager_token = Token.objects.create(user=self.manager)
        self.cashier_token = Token.objects.create(user=self.cashier)    
    def test_user_can_update_own_profile(self):
        """Test that users can update own profile (limited fields)"""
        token = Token.objects.get(user=self.cashier)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        
        url = reverse('user-detail', kwargs={'pk': self.cashier.id})
        response = self.client.put(url, {
            'full_name': 'Updated Cashier',
            'email': 'cashier@example.com',
            'contact': '077-9999999'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['full_name'], 'Updated Cashier')
    
    def test_user_cannot_change_own_role(self):
        """Test that users cannot change their own role"""
        token = Token.objects.get(user=self.cashier)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        
        url = reverse('user-detail', kwargs={'pk': self.cashier.id})
        response = self.client.put(url, {
            'full_name': 'Cashier One',
            'role': 'Manager'  # Try to change role
        })
        
        # Role should remain Cashier
        user = User.objects.get(pk=self.cashier.id)
        self.assertEqual(user.role, 'Cashier')
    
    def test_manager_can_update_any_user(self):
        """Test that Manager can update any user"""
        token = Token.objects.get(user=self.manager)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        
        url = reverse('user-detail', kwargs={'pk': self.cashier.id})
        response = self.client.put(url, {
            'full_name': 'Updated by Manager',
            'email': 'new@example.com',
            'role': 'Baker'
        })
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['role'], 'Baker')


class UserDeleteEndpointTests(APITestCase):
    """Test DELETE /api/users/{id}/ endpoint"""
    
    def setUp(self):
        self.client = APIClient()
        self.manager = User.objects.create_user(
            username='manager',
            password='TestPass123',
            role='Manager'
        )
        self.cashier = User.objects.create_user(
            username='cashier',
            password='TestPass123',
            role='Cashier'
        )
        # Create tokens for authentication
        self.manager_token = Token.objects.create(user=self.manager)
        self.cashier_token = Token.objects.create(user=self.cashier)
    
    def test_delete_requires_manager(self):
        """Test that only Manager can delete users"""
        token = Token.objects.get(user=self.cashier)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        
        url = reverse('user-detail', kwargs={'pk': self.manager.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_manager_cannot_delete_self(self):
        """Test that Manager cannot delete their own account"""
        token = Token.objects.get(user=self.manager)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        
        url = reverse('user-detail', kwargs={'pk': self.manager.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_manager_can_delete_other_user(self):
        """Test that Manager can delete other users"""
        token = Token.objects.get(user=self.manager)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        
        url = reverse('user-detail', kwargs={'pk': self.cashier.id})
        response = self.client.delete(url)
        
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        
        # User should be marked as inactive
        user = User.objects.get(pk=self.cashier.id)
        self.assertEqual(user.status, 'inactive')
        self.assertFalse(user.is_active)


class UserStatusEndpointTests(APITestCase):
    """Test PATCH /api/users/{id}/status/ endpoint"""
    
    def setUp(self):
        self.client = APIClient()
        self.manager = User.objects.create_user(
            username='manager',
            password='TestPass123',
            role='Manager'
        )
        self.cashier = User.objects.create_user(
            username='cashier',
            password='TestPass123',
            role='Cashier'
        )
        # Create tokens for authentication
        self.manager_token = Token.objects.create(user=self.manager)
        self.cashier_token = Token.objects.create(user=self.cashier)
    
    def test_status_requires_manager(self):
        """Test that only Manager can change status"""
        token = Token.objects.get(user=self.cashier)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        
        url = reverse('user-status', kwargs={'pk': self.cashier.id})
        response = self.client.patch(url, {'status': 'inactive'})
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_manager_cannot_change_own_status(self):
        """Test that Manager cannot change their own status"""
        token = Token.objects.get(user=self.manager)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        
        url = reverse('user-status', kwargs={'pk': self.manager.id})
        response = self.client.patch(url, {'status': 'inactive'})
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_manager_can_change_user_status(self):
        """Test that Manager can change other users' status"""
        token = Token.objects.get(user=self.manager)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        
        url = reverse('user-status', kwargs={'pk': self.cashier.id})
        response = self.client.patch(url, {'status': 'suspended'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'suspended')


class UserAdditionalActionsTests(APITestCase):
    """Test additional user endpoints (me, managers, statistics, etc.)"""
    
    def setUp(self):
        self.client = APIClient()
        self.manager = User.objects.create_user(
            username='manager',
            password='TestPass123',
            role='Manager'
        )
        self.cashier = User.objects.create_user(
            username='cashier',
            password='TestPass123',
            role='Cashier'
        )
        # Create tokens for authentication
        self.manager_token = Token.objects.create(user=self.manager)
        self.cashier_token = Token.objects.create(user=self.cashier)
    
    def test_me_endpoint(self):
        """Test /api/users/me/ endpoint"""
        token = Token.objects.get(user=self.cashier)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        
        url = reverse('user-me')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'cashier')
    
    def test_managers_endpoint_requires_auth(self):
        """Test /api/users/managers/ requires Manager role"""
        token = Token.objects.get(user=self.cashier)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        
        url = reverse('user-managers')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_managers_endpoint_lists_managers(self):
        """Test /api/users/managers/ lists all managers"""
        token = Token.objects.get(user=self.manager)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        
        url = reverse('user-managers')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
    
    def test_statistics_endpoint_requires_manager(self):
        """Test /api/users/statistics/ requires Manager"""
        token = Token.objects.get(user=self.cashier)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        
        url = reverse('user-statistics')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_statistics_endpoint_returns_stats(self):
        """Test /api/users/statistics/ returns user statistics"""
        token = Token.objects.get(user=self.manager)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        
        url = reverse('user-statistics')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_users', response.data)
        self.assertIn('by_role', response.data)
        self.assertIn('by_status', response.data)


# ==================== RUNNING TESTS ====================
# Run all tests:
# pytest Backend/api/tests_users.py -v
#
# Run specific test class:
# pytest Backend/api/tests_users.py::UserListEndpointTests -v
#
# Run with coverage:
# pytest Backend/api/tests_users.py --cov=api --cov-report=html
