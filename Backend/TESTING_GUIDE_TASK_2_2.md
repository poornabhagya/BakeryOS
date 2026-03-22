# Task 2.2 - Token Authentication Testing Guide

## 📋 What to Test

This document outlines all tests for Task 2.2: Token Authentication system.

---

## ✅ Test Coverage Overview

### 1. **Setup & Configuration Tests** (`AuthenticationSetupTests`)
What to test:
- ✅ Login endpoint exists and is accessible
- ✅ Me endpoint exists and is accessible
- ✅ Logout endpoint exists and is accessible

Why important: Ensures all endpoints are properly registered in URLs

---

### 2. **Login Endpoint Tests** (`LoginEndpointTests`)

#### ✅ Valid Credentials
- **Test**: Username and password are correct
- **Expected**: 
  - Status: `200 OK`
  - Response includes `token` field
  - Response includes `user` object

- **Test**: Login returns correct user information
- **Expected**: 
  - `username`, `full_name`, `role`, `email`, `employee_id` all correct
  
- **Test**: Login returns valid token
- **Expected**: 
  - Token is a non-empty string
  - Token is stored in database
  - Token can be used for subsequent requests

#### ❌ Invalid Credentials
- **Test**: Wrong password
- **Expected**: Status `401 Unauthorized`, no token returned

- **Test**: Non-existent username
- **Expected**: Status `401 Unauthorized`

- **Test**: Missing username field
- **Expected**: Status `400 Bad Request` or `401 Unauthorized`

- **Test**: Missing password field
- **Expected**: Status `400 Bad Request` or `401 Unauthorized`

#### 🔒 Security Tests
- **Test**: Login with inactive user
- **Expected**: Status `401 Unauthorized`

- **Test**: Username is case-sensitive
- **Expected**: `testuser` ≠ `TESTUSER`

---

### 3. **Me Endpoint Tests** (`MeEndpointTests`)

What to test:
- ✅ Authentication is required
  - Without token: `401 Unauthorized`
  - With valid token: `200 OK`

- ✅ Correct user data is returned
  - All fields present (id, username, email, role, employee_id, contact, nic, etc.)
  - Data matches the authenticated user
  - No password returned

- ✅ Token validation
  - Invalid token: `401 Unauthorized`
  - Malformed header (e.g., `Bearer` instead of `Token`): `401 Unauthorized`

---

### 4. **Logout Endpoint Tests** (`LogoutEndpointTests`)

What to test:
- ✅ Authentication is required (no token = `401 Unauthorized`)

- ✅ Successful logout
  - Valid token: `200 OK`
  - Response includes success message

- ✅ Token invalidation
  - After logout, token is deleted from database
  - Token cannot be used for subsequent requests
  - Using logged-out token: `401 Unauthorized`

---

### 5. **Token Authentication Mechanism** (`TokenAuthenticationTests`)

What to test:
- ✅ Token format:
  - Token is a string
  - Token has sufficient length (>10 characters)
  - Each user has unique token

- ✅ Authorization header format:
  - Correct format: `Authorization: Token abc123...`
  - Wrong format: `Authorization: Bearer abc123...` → Fails
  - Missing header → `401 Unauthorized`

---

### 6. **Role-Based Access Tests** (`RoleBasedAccessTests`)

What to test:
- ✅ All 4 roles can login:
  - Manager
  - Cashier
  - Baker
  - Storekeeper

- ✅ All 4 roles can access `/me` endpoint

- ✅ Role information is correctly returned in response

---

### 7. **Error Handling & Edge Cases** (`ErrorHandlingTests`)

What to test:
- ✅ Empty request body
- ✅ SQL injection attempts (must be blocked)
- ✅ Special characters in password (`p@$$w0rd!#%&`)
- ✅ Very long usernames (>1000 chars)

---

## 🚀 How to Run Tests

### Install pytest (if not already installed)
```bash
pip install pytest pytest-django
```

### Run all authentication tests
```bash
pytest Backend/api/tests_auth.py -v
```

### Run specific test class
```bash
pytest Backend/api/tests_auth.py::LoginEndpointTests -v
```

### Run specific test
```bash
pytest Backend/api/tests_auth.py::LoginEndpointTests::test_login_with_valid_credentials -v
```

### Run with coverage report
```bash
pip install pytest-cov
pytest Backend/api/tests_auth.py --cov=api --cov-report=html
```

### Run tests in verbose mode (see print statements)
```bash
pytest Backend/api/tests_auth.py -v -s
```

---

## 📊 Test Statistics

| Test Class | Number of Tests | Coverage Area |
|---|---|---|
| AuthenticationSetupTests | 3 | Endpoint existence |
| LoginEndpointTests | 10 | Login endpoint validation |
| MeEndpointTests | 6 | Current user retrieval |
| LogoutEndpointTests | 5 | Logout & token invalidation |
| TokenAuthenticationTests | 5 | Token mechanism |
| RoleBasedAccessTests | 3 | Multi-role support |
| ErrorHandlingTests | 4 | Security & edge cases |
| **TOTAL** | **36 tests** | **Complete auth system** |

---

## ✨ What Gets Tested

### Functionality
- [x] Login with valid credentials → Token + user data returned
- [x] Login with invalid credentials → 401 error
- [x] Get current user info with valid token → User data returned
- [x] Get current user without token → 401 error
- [x] Logout with valid token → Token deleted
- [x] Logout without token → 401 error
- [x] Token format and storage
- [x] All 4 roles can authenticate

### Security
- [x] Password validation
- [x] Token validation
- [x] SQL injection prevention
- [x] Invalid authentication headers
- [x] Special characters in passwords
- [x] Case-sensitive username
- [x] Inactive user prevention

### Edge Cases
- [x] Empty requests
- [x] Missing fields
- [x] Very long usernames
- [x] Wrong auth header scheme

---

## 🎯 Expected Test Results

After running tests, you should see:
```
===== 36 passed in 2.34s =====
```

If any test fails, check:
1. URL routing (ensure endpoints are named correctly: 'login', 'me', 'logout')
2. Response format (serializer output structure)
3. Token creation (Token model configuration)
4. Authentication class configuration in settings.py

---

## 🔍 Understanding Test Results

### ✅ PASSED
- Green checkmark
- Feature works as expected
- No action needed

### ❌ FAILED
- Red X mark
- Shows assertion error
- Example: `AssertionError: 401 != 200`
- **Fix**: Check the code implementing that feature

### ⚠️ SKIPPED
- Blue dash (if using `@pytest.mark.skip`)
- Test deliberately skipped
- Usually for incomplete features

---

## 💡 Troubleshooting Common Issues

### Error: "ModuleNotFoundError: No module named 'rest_framework.authtoken'"
**Solution**: 
```bash
pip install djangorestframework
python manage.py migrate authtoken
```

### Error: "No such table: authtoken_token"
**Solution**: Run migrations
```bash
python manage.py migrate
```

### Error: "Reverse for 'login' not found"
**Solution**: Check URL names in `api/urls_token.py` match test references

### Error: "Token matching query does not exist"
**Solution**: Ensure Token is created when user is created (via signals)

---

## 📝 Test Template for New Tests

If you want to add more tests:

```python
class MyNewAuthTests(APITestCase):
    """Describe what you're testing"""
    
    def setUp(self):
        """Create test user and client"""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            role='Manager'
        )
        self.token = Token.objects.get(user=self.user)
    
    def test_my_new_feature(self):
        """Describe what this test checks"""
        # Setup
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)
        
        # Action
        response = self.client.get('/api/endpoint/')
        
        # Assert
        self.assertEqual(response.status_code, status.HTTP_200_OK)
```

---

## 🎓 What Each Test Class Tests

```
Authentication System (Task 2.2)
│
├── AuthenticationSetupTests (3 tests)
│   └── Are endpoints registered?
│
├── LoginEndpointTests (10 tests)
│   ├── Valid credentials → Token returned
│   ├── Invalid credentials → 401 error
│   ├── User data validation
│   └── Security checks (inactive users, case-sensitivity)
│
├── MeEndpointTests (6 tests)
│   ├── Requires authentication
│   ├── Returns correct user data
│   └── Token validation
│
├── LogoutEndpointTests (5 tests)
│   ├── Requires authentication
│   ├── Token deletion
│   └── Prevents future use
│
├── TokenAuthenticationTests (5 tests)
│   ├── Token format & uniqueness
│   └── Header format validation
│
├── RoleBasedAccessTests (3 tests)
│   └── All 4 roles can authenticate
│
└── ErrorHandlingTests (4 tests)
    ├── SQL injection prevention
    ├── Special characters
    └── Malformed requests
```

---

## ✅ Acceptance Criteria

Your authentication system passes Task 2.2 when:
- [x] All 36 tests pass (100% passing)
- [x] Login endpoint returns valid token
- [x] Me endpoint returns current user info
- [x] Logout endpoint invalidates token
- [x] All 4 roles can authenticate
- [x] Security tests pass (SQL injection, special chars, etc.)
- [x] Edge cases handled properly

---

**Last Updated**: March 22, 2026  
**Test File**: `Backend/api/tests_auth.py`  
**Coverage**: Token Authentication System (Task 2.2)
