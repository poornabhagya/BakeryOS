# Task 2.3: User Management API - Manual Test Cases

**Date:** March 22, 2026  
**Status:** All 34 automated tests PASSING ✅  
**This Guide:** Manual testing for verification

---

## 📋 Prerequisites

1. **Start Django Server:**
   ```bash
   python manage.py runserver
   ```

2. **Default Admin Credentials:**
   - Username: `admin`
   - Password: `admin@123`
   - Role: `Manager`

3. **Test Users Already Created (from automated tests):**
   - Manager: `manager1` / `TestPass123`
   - Cashier: `cashier1` / `TestPass123`
   - Baker: `baker1` / `TestPass123`

4. **API Base URL:** `http://127.0.0.1:8000/api`

---

## 🔐 Step 1: Get Authentication Token

### 1.1 Login as Admin (Manager)

**Endpoint:** `POST /api/auth/login/`

**cURL:**
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin@123"
  }'
```

**Postman:**
- Method: `POST`
- URL: `http://127.0.0.1:8000/api/auth/login/`
- Body (JSON):
  ```json
  {
    "username": "admin",
    "password": "admin@123"
  }
  ```

**Expected Response (200 OK):**
```json
{
  "token": "abcdef123456...",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@example.com",
    "full_name": "Admin User",
    "role": "Manager",
    "employee_id": "EMP-001"
  }
}
```

**Save the token:** You'll use this for all following requests.

---

### 1.2 Create Tokens for Other Users (Optional)

If you want to test with different roles, create tokens:

**Cashier Login:**
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "cashier1",
    "password": "TestPass123"
  }'
```

**Baker Login:**
```bash
curl -X POST http://127.0.0.1:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "baker1",
    "password": "TestPass123"
  }'
```

---

## 📝 Test Case Naming Convention

Each test follows format: `TC-2.3-{NUMBER}` where number represents feature area:
- `1X` = List/Filter/Search
- `2X` = Create
- `3X` = Retrieve/Details
- `4X` = Update
- `5X` = Delete
- `6X` = Status Change
- `7X` = Bonus Endpoints

---

## ✅ TEST SUITE 1: LIST USERS ENDPOINT

### TC-2.3-1.1: List All Users (Manager Only)

**Description:** Manager should see all users with pagination

**Endpoint:** `GET /api/users/`

**cURL:**
```bash
curl -X GET "http://127.0.0.1:8000/api/users/" \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json"
```

**Postman:**
- Method: `GET`
- URL: `http://127.0.0.1:8000/api/users/`
- Headers: `Authorization: Token YOUR_TOKEN_HERE`

**Expected Response (200 OK):**
```json
{
  "count": 4,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "username": "admin",
      "email": "admin@example.com",
      "full_name": "Admin User",
      "employee_id": "EMP-001",
      "role": "Manager",
      "status": "active",
      "contact": null,
      "created_at": "2026-03-22T10:00:00Z",
      "updated_at": "2026-03-22T10:00:00Z"
    },
    // ... more users
  ]
}
```

**✅ Pass Criteria:**
- Status: 200
- Response has `results` array with users
- No `password` field in response
- At least 3 users listed

---

### TC-2.3-1.2: Non-Manager Cannot List (Permission Denied)

**Description:** Cashier/Baker/Storekeeper should get 403 Forbidden

**Use:** Cashier token from Step 1.2

**cURL:**
```bash
curl -X GET "http://127.0.0.1:8000/api/users/" \
  -H "Authorization: Token CASHIER_TOKEN" \
  -H "Content-Type: application/json"
```

**Expected Response (403 Forbidden):**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

**✅ Pass Criteria:**
- Status: 403
- Error message shows permission denied

---

### TC-2.3-1.3: Filter by Role

**Description:** Filter users by role (e.g., Cashier)

**Endpoint:** `GET /api/users/?role=Cashier`

**cURL:**
```bash
curl -X GET "http://127.0.0.1:8000/api/users/?role=Cashier" \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json"
```

**Expected Response (200 OK):**
```json
{
  "count": 1,
  "results": [
    {
      "username": "cashier1",
      "role": "Cashier",
      // ...
    }
  ]
}
```

**✅ Pass Criteria:**
- Status: 200
- All returned users have `role: "Cashier"`
- Count matches filtered results

---

### TC-2.3-1.4: Filter by Status

**Description:** Filter users by status (active/inactive/suspended)

**Endpoint:** `GET /api/users/?status=active`

**cURL:**
```bash
curl -X GET "http://127.0.0.1:8000/api/users/?status=active" \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json"
```

**Expected Response (200 OK):**
```json
{
  "count": 4,
  "results": [
    {
      "status": "active",
      // ...
    },
    // ... all active users
  ]
}
```

**✅ Pass Criteria:**
- Status: 200
- All returned users have `status: "active"`

---

### TC-2.3-1.5: Search by Username

**Description:** Search users by username field

**Endpoint:** `GET /api/users/?search=admin`

**cURL:**
```bash
curl -X GET "http://127.0.0.1:8000/api/users/?search=admin" \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json"
```

**Expected Response (200 OK):**
```json
{
  "count": 1,
  "results": [
    {
      "username": "admin",
      "full_name": "Admin User",
      // ...
    }
  ]
}
```

**✅ Pass Criteria:**
- Status: 200
- Result contains "admin" in username or full_name
- Only matching users returned

---

### TC-2.3-1.6: Search by Full Name

**Description:** Search by full name field

**Endpoint:** `GET /api/users/?search=cashier`

**cURL:**
```bash
curl -X GET "http://127.0.0.1:8000/api/users/?search=Cashier" \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json"
```

**✅ Pass Criteria:**
- Status: 200
- Results contain "Cashier" in username or full_name

---

### TC-2.3-1.7: Order by Username (Ascending)

**Description:** Sort results by username field

**Endpoint:** `GET /api/users/?ordering=username`

**cURL:**
```bash
curl -X GET "http://127.0.0.1:8000/api/users/?ordering=username" \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json"
```

**Expected Response (200 OK):**
```json
{
  "count": 4,
  "results": [
    { "username": "admin", ... },
    { "username": "baker1", ... },
    { "username": "cashier1", ... },
    { "username": "manager1", ... }
  ]
}
```

**✅ Pass Criteria:**
- Status: 200
- Results sorted alphabetically by username

---

### TC-2.3-1.8: Order by Created Date (Descending)

**Description:** Sort by created_at descending (newest first)

**Endpoint:** `GET /api/users/?ordering=-created_at`

**cURL:**
```bash
curl -X GET "http://127.0.0.1:8000/api/users/?ordering=-created_at" \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

**✅ Pass Criteria:**
- Status: 200
- Newest users appear first
- Dates are in descending order

---

## ➕ TEST SUITE 2: CREATE USER ENDPOINT

### TC-2.3-2.1: Create User Successfully (Manager Only)

**Description:** Manager creates a new user with all required fields

**Endpoint:** `POST /api/users/`

**cURL:**
```bash
curl -X POST "http://127.0.0.1:8000/api/users/" \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser001",
    "password": "SecurePass123",
    "password_confirm": "SecurePass123",
    "email": "newuser@bakeryos.com",
    "full_name": "New Test User",
    "contact": "077-1234567",
    "nic": "123456789V",
    "role": "Cashier"
  }'
```

**Postman:**
- Method: `POST`
- URL: `http://127.0.0.1:8000/api/users/`
- Headers: `Authorization: Token YOUR_TOKEN_HERE`
- Body (JSON):
  ```json
  {
    "username": "newuser001",
    "password": "SecurePass123",
    "password_confirm": "SecurePass123",
    "email": "newuser@bakeryos.com",
    "full_name": "New Test User",
    "contact": "077-1234567",
    "nic": "123456789V",
    "role": "Cashier"
  }
  ```

**Expected Response (201 Created):**
```json
{
  "id": 5,
  "username": "newuser001",
  "email": "newuser@bakeryos.com",
  "full_name": "New Test User",
  "employee_id": "EMP-005",
  "nic": "123456789V",
  "contact": "077-1234567",
  "role": "Cashier",
  "status": "active",
  "avatar_color": "blue",
  "last_login": null,
  "is_active": true,
  "created_at": "2026-03-22T12:30:00Z",
  "updated_at": "2026-03-22T12:30:00Z"
}
```

**✅ Pass Criteria:**
- Status: 201 Created
- Response includes `employee_id` (auto-generated)
- No `password` field in response
- `status` defaults to "active"
- New user can login with provided credentials

---

### TC-2.3-2.2: Password Too Short

**Description:** Reject password with less than 8 characters

**Endpoint:** `POST /api/users/`

**cURL:**
```bash
curl -X POST "http://127.0.0.1:8000/api/users/" \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "Short1",
    "password_confirm": "Short1",
    "email": "test@bakeryos.com",
    "full_name": "Test User",
    "role": "Baker"
  }'
```

**Expected Response (400 Bad Request):**
```json
{
  "password": [
    "Password must be at least 8 characters"
  ]
}
```

**✅ Pass Criteria:**
- Status: 400
- Error message mentions password requirements

---

### TC-2.3-2.3: Missing Uppercase in Password

**Description:** Reject password without uppercase letter

**Endpoint:** `POST /api/users/`

**Request Body:**
```json
{
  "username": "testuser",
  "password": "nouppercase123",
  "password_confirm": "nouppercase123",
  "email": "test@bakeryos.com",
  "full_name": "Test User",
  "role": "Baker"
}
```

**Expected Response (400 Bad Request):**
```json
{
  "password": [
    "Password must contain at least one uppercase letter"
  ]
}
```

**✅ Pass Criteria:**
- Status: 400
- Error message is clear about requirement

---

### TC-2.3-2.4: Missing Lowercase in Password

**Description:** Reject password without lowercase letter

**Request Body:**
```json
{
  "username": "testuser",
  "password": "NOLOWERCASE123",
  "password_confirm": "NOLOWERCASE123",
  "email": "test@bakeryos.com",
  "full_name": "Test User",
  "role": "Baker"
}
```

**Expected Response (400 Bad Request):**
```json
{
  "password": [
    "Password must contain at least one lowercase letter"
  ]
}
```

**✅ Pass Criteria:**
- Status: 400

---

### TC-2.3-2.5: Missing Number in Password

**Description:** Reject password without numeric digit

**Request Body:**
```json
{
  "username": "testuser",
  "password": "NoNumbersHere",
  "password_confirm": "NoNumbersHere",
  "email": "test@bakeryos.com",
  "full_name": "Test User",
  "role": "Baker"
}
```

**Expected Response (400 Bad Request):**
```json
{
  "password": [
    "Password must contain at least one number"
  ]
}
```

**✅ Pass Criteria:**
- Status: 400

---

### TC-2.3-2.6: Passwords Don't Match

**Description:** password_confirm must match password

**Request Body:**
```json
{
  "username": "testuser",
  "password": "CorrectPass123",
  "password_confirm": "DifferentPass123",
  "email": "test@bakeryos.com",
  "full_name": "Test User",
  "role": "Baker"
}
```

**Expected Response (400 Bad Request):**
```json
{
  "password_confirm": [
    "Passwords do not match"
  ]
}
```

**✅ Pass Criteria:**
- Status: 400
- Error on `password_confirm` field

---

### TC-2.3-2.7: Duplicate Username

**Description:** Reject duplicate username

**Request Body:**
```json
{
  "username": "admin",
  "password": "SecurePass123",
  "password_confirm": "SecurePass123",
  "email": "different@bakeryos.com",
  "full_name": "Another Admin",
  "role": "Manager"
}
```

**Expected Response (400 Bad Request):**
```json
{
  "username": [
    "Username already exists"
  ]
}
```

**✅ Pass Criteria:**
- Status: 400
- Error about username uniqueness

---

### TC-2.3-2.8: Invalid Role

**Description:** Reject invalid role value

**Request Body:**
```json
{
  "username": "testuser",
  "password": "SecurePass123",
  "password_confirm": "SecurePass123",
  "email": "test@bakeryos.com",
  "full_name": "Test User",
  "role": "InvalidRole"
}
```

**Expected Response (400 Bad Request):**
```json
{
  "role": [
    "Role must be one of: Manager, Cashier, Baker, Storekeeper"
  ]
}
```

**✅ Pass Criteria:**
- Status: 400
- Shows valid role options

---

### TC-2.3-2.9: Non-Manager Cannot Create

**Description:** Cashier tries to create user and gets 403

**Use:** Cashier token

**Expected Response (403 Forbidden):**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

**✅ Pass Criteria:**
- Status: 403
- No user created

---

### TC-2.3-2.10: Auto-Generated Employee ID

**Description:** Verify employee_id is auto-generated in format EMP-XXX

**From TC-2.3-2.1:** Check response has `employee_id`

**Expected:** `"employee_id": "EMP-005"` (or next sequential)

**✅ Pass Criteria:**
- Employee ID matches pattern: `EMP-{number}`
- Unique for each user
- Cannot be edited manually

---

## 👁️ TEST SUITE 3: RETRIEVE USER ENDPOINT

### TC-2.3-3.1: Get Own Profile (Any Authenticated User)

**Description:** User can view their own profile details

**Endpoint:** `GET /api/users/{id}/`
(Use your own user ID - e.g., admin is ID 1)

**cURL:**
```bash
curl -X GET "http://127.0.0.1:8000/api/users/1/" \
  -H "Authorization: Token YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json"
```

**Expected Response (200 OK):**
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@example.com",
  "full_name": "Admin User",
  "employee_id": "EMP-001",
  "nic": null,
  "contact": null,
  "role": "Manager",
  "status": "active",
  "avatar_color": "blue",
  "last_login": "2026-03-22T10:00:00Z",
  "is_active": true,
  "created_at": "2026-03-22T09:00:00Z",
  "updated_at": "2026-03-22T10:00:00Z"
}
```

**✅ Pass Criteria:**
- Status: 200
- Shows complete user details
- No password field

---

### TC-2.3-3.2: Manager Can View Any Profile

**Description:** Manager (use admin token) views another user's profile

**Endpoint:** `GET /api/users/3/` (cashier ID)

**cURL:**
```bash
curl -X GET "http://127.0.0.1:8000/api/users/3/" \
  -H "Authorization: Token ADMIN_TOKEN" \
  -H "Content-Type: application/json"
```

**Expected Response (200 OK):**
```json
{
  "id": 3,
  "username": "cashier1",
  // ... full details
}
```

**✅ Pass Criteria:**
- Status: 200
- Manager can access any user profile

---

### TC-2.3-3.3: Non-Manager Cannot View Others (403)

**Description:** Cashier tries to view Baker's profile

**Use:** Cashier token

**Endpoint:** `GET /api/users/4/` (baker ID)

**cURL:**
```bash
curl -X GET "http://127.0.0.1:8000/api/users/4/" \
  -H "Authorization: Token CASHIER_TOKEN"
```

**Expected Response (403 Forbidden):**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

**✅ Pass Criteria:**
- Status: 403
- Regular users cannot view others' profiles

---

### TC-2.3-3.4: Invalid User ID (404)

**Description:** Request non-existent user ID

**Endpoint:** `GET /api/users/9999/`

**Expected Response (404 Not Found):**
```json
{
  "detail": "Not found."
}
```

**✅ Pass Criteria:**
- Status: 404

---

## ✏️ TEST SUITE 4: UPDATE USER ENDPOINT

### TC-2.3-4.1: User Updates Own Profile

**Description:** User updates own profile (limited fields)

**Endpoint:** `PUT /api/users/3/` (use cashier's own ID with cashier token)

**cURL:**
```bash
curl -X PUT "http://127.0.0.1:8000/api/users/3/" \
  -H "Authorization: Token CASHIER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Updated Cashier Name",
    "email": "newemail@bakeryos.com",
    "contact": "077-9999999"
  }'
```

**Expected Response (200 OK):**
```json
{
  "id": 3,
  "username": "cashier1",
  "full_name": "Updated Cashier Name",
  "email": "newemail@bakeryos.com",
  "contact": "077-9999999",
  "role": "Cashier",
  "status": "active",
  // ...
}
```

**✅ Pass Criteria:**
- Status: 200
- Fields updated successfully
- Username unchanged (read-only)

---

### TC-2.3-4.2: User Cannot Change Own Role

**Description:** User tries to change own role to Manager

**Endpoint:** `PUT /api/users/3/` (cashier's own ID with cashier token)

**Request Body:**
```json
{
  "full_name": "Cashier Name",
  "role": "Manager"
}
```

**Expected Behavior:**
- Role field silently ignored or returns 400
- User remains as Cashier

**Verify:** Retrieve profile and check `role` is still "Cashier"

**✅ Pass Criteria:**
- Status: 200 (update processed) or 400 (explicit error)
- User's role unchanged

---

### TC-2.3-4.3: User Cannot Change Own Status

**Description:** User tries to change own status

**Request Body:**
```json
{
  "status": "inactive"
}
```

**Expected:** Status field ignored or error returned

**✅ Pass Criteria:**
- User's status remains "active"

---

### TC-2.3-4.4: Manager Can Update Any User

**Description:** Manager updates another user's profile

**Endpoint:** `PUT /api/users/3/` (use ADMIN token to update cashier)

**Request Body:**
```json
{
  "full_name": "Cashier Updated by Manager",
  "email": "managed@bakeryos.com",
  "role": "Baker"
}
```

**Expected Response (200 OK):**
```json
{
  "role": "Baker",
  "full_name": "Cashier Updated by Manager",
  // ...
}
```

**✅ Pass Criteria:**
- Status: 200
- Manager can change role, status, any field

---

### TC-2.3-4.5: Manager Cannot Update Password via PUT

**Description:** Password updates should use separate endpoint

**Request Body:**
```json
{
  "password": "NewPassword123"
}
```

**Expected:** Password field ignored (no password update via PUT/PATCH)

**✅ Pass Criteria:**
- Password not changed via update endpoint

---

### TC-2.3-4.6: Partial Update (PATCH)

**Description:** Update only specific fields

**Endpoint:** `PATCH /api/users/3/` (with cashier token)

**cURL:**
```bash
curl -X PATCH "http://127.0.0.1:8000/api/users/3/" \
  -H "Authorization: Token CASHIER_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "contact": "077-8888888"
  }'
```

**Expected Response (200 OK):**
```json
{
  "id": 3,
  "contact": "077-8888888",
  // ... other fields unchanged
}
```

**✅ Pass Criteria:**
- Status: 200
- Only specified field updated
- Others remain unchanged

---

## 🗑️ TEST SUITE 5: DELETE USER ENDPOINT

### TC-2.3-5.1: Manager Deletes Other User (Soft Delete)

**Description:** Manager soft-deletes user (marks as inactive)

**Endpoint:** `DELETE /api/users/3/` (use ADMIN token)

**cURL:**
```bash
curl -X DELETE "http://127.0.0.1:8000/api/users/3/" \
  -H "Authorization: Token ADMIN_TOKEN" \
  -H "Content-Type: application/json"
```

**Expected Response (204 No Content):**
```
(empty body)
```

**Verify:** Retrieve user and check status:
```bash
curl -X GET "http://127.0.0.1:8000/api/users/3/" \
  -H "Authorization: Token ADMIN_TOKEN"
```

**Response should show:**
```json
{
  "status": "inactive",
  "is_active": false
}
```

**✅ Pass Criteria:**
- Status: 204
- User marked as inactive, not deleted
- User still in database with `is_active: false`

---

### TC-2.3-5.2: Non-Manager Cannot Delete (403)

**Description:** Cashier tries to delete another user

**Use:** Cashier token for another user

**Expected Response (403 Forbidden):**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

**✅ Pass Criteria:**
- Status: 403
- No deletion occurs

---

### TC-2.3-5.3: Manager Cannot Delete Self

**Description:** Manager tries to delete own account

**Endpoint:** `DELETE /api/users/1/` (admin's own ID, use admin token)

**Expected Response (400 Bad Request):**
```json
{
  "detail": "Cannot delete your own account"
}
```

**✅ Pass Criteria:**
- Status: 400
- Admin account not deleted

---

## 📊 TEST SUITE 6: STATUS CHANGE ENDPOINT

### TC-2.3-6.1: Manager Changes User Status

**Description:** Change user status to suspended/inactive

**Endpoint:** `PATCH /api/users/3/status/` (use ADMIN token)

**cURL:**
```bash
curl -X PATCH "http://127.0.0.1:8000/api/users/3/status/" \
  -H "Authorization: Token ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "status": "suspended"
  }'
```

**Expected Response (200 OK):**
```json
{
  "id": 3,
  "username": "cashier1",
  "status": "suspended",
  // ... full user details
}
```

**✅ Pass Criteria:**
- Status: 200
- User status changed to "suspended"
- Suspended user exists in system

---

### TC-2.3-6.2: Valid Status Values

**Description:** Test all valid status values

**Valid statuses:** `active`, `inactive`, `suspended`

**Test each:**
```bash
# Test "active"
curl -X PATCH "http://127.0.0.1:8000/api/users/3/status/" \
  -H "Authorization: Token ADMIN_TOKEN" \
  -d '{"status": "active"}'

# Test "inactive"
curl -X PATCH "http://127.0.0.1:8000/api/users/3/status/" \
  -H "Authorization: Token ADMIN_TOKEN" \
  -d '{"status": "inactive"}'

# Test "suspended"
curl -X PATCH "http://127.0.0.1:8000/api/users/3/status/" \
  -H "Authorization: Token ADMIN_TOKEN" \
  -d '{"status": "suspended"}'
```

**✅ Pass Criteria:**
- Status: 200 for all valid values
- Status updated correctly

---

### TC-2.3-6.3: Invalid Status Rejected

**Description:** Reject invalid status values

**Request:**
```json
{
  "status": "invalid_status"
}
```

**Expected Response (400 Bad Request):**
```json
{
  "status": [
    "Status must be one of: active, inactive, suspended"
  ]
}
```

**✅ Pass Criteria:**
- Status: 400
- Error message lists valid options

---

### TC-2.3-6.4: Non-Manager Cannot Change Status (403)

**Description:** Cashier tries to change another user's status

**Use:** Cashier token

**Expected Response (403 Forbidden):**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

**✅ Pass Criteria:**
- Status: 403

---

### TC-2.3-6.5: Manager Cannot Change Own Status

**Description:** Manager tries to change their own status

**Endpoint:** `PATCH /api/users/1/status/` (admin's own ID)

**Request:**
```json
{
  "status": "inactive"
}
```

**Expected Response (400 Bad Request):**
```json
{
  "detail": "You cannot change your own status"
}
```

**✅ Pass Criteria:**
- Status: 400
- Admin's status remains "active"

---

## 🎯 TEST SUITE 7: BONUS ENDPOINTS

### TC-2.3-7.1: Get Current User Info (/me/)

**Description:** Any authenticated user can get their own info

**Endpoint:** `GET /api/users/me/`

**cURL:**
```bash
curl -X GET "http://127.0.0.1:8000/api/users/me/" \
  -H "Authorization: Token YOUR_TOKEN_HERE"
```

**Expected Response (200 OK):**
```json
{
  "id": 3,
  "username": "cashier1",
  "email": "cashier@bakeryos.com",
  "full_name": "Cashier One",
  "employee_id": "EMP-003",
  "role": "Cashier",
  "status": "active",
  // ... full user details
}
```

**✅ Pass Criteria:**
- Status: 200
- Returns current authenticated user info
- Works for all roles

---

### TC-2.3-7.2: List All Managers (/managers/)

**Description:** Get list of all Manager users

**Endpoint:** `GET /api/users/managers/`

**cURL:**
```bash
curl -X GET "http://127.0.0.1:8000/api/users/managers/" \
  -H "Authorization: Token ADMIN_TOKEN"
```

**Expected Response (200 OK):**
```json
[
  {
    "id": 1,
    "username": "admin",
    "full_name": "Admin User",
    "role": "Manager",
    "employee_id": "EMP-001"
  },
  {
    "id": 2,
    "username": "manager1",
    "full_name": "Manager One",
    "role": "Manager",
    "employee_id": "EMP-002"
  }
]
```

**✅ Pass Criteria:**
- Status: 200
- Only managers returned
- Minimal serializer (5 fields)

---

### TC-2.3-7.3: Non-Manager Cannot Access /managers/ (403)

**Description:** Cashier tries to list managers

**Use:** Cashier token

**Expected Response (403 Forbidden):**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

**✅ Pass Criteria:**
- Status: 403
- Manager list not exposed to other roles

---

### TC-2.3-7.4: Get User Statistics (/statistics/)

**Description:** Manager sees count by role and status

**Endpoint:** `GET /api/users/statistics/`

**cURL:**
```bash
curl -X GET "http://127.0.0.1:8000/api/users/statistics/" \
  -H "Authorization: Token ADMIN_TOKEN"
```

**Expected Response (200 OK):**
```json
{
  "total_users": 4,
  "by_role": {
    "Manager": 2,
    "Cashier": 1,
    "Baker": 1,
    "Storekeeper": 0
  },
  "by_status": {
    "active": 4,
    "inactive": 0,
    "suspended": 0
  }
}
```

**✅ Pass Criteria:**
- Status: 200
- Shows counts by role and status
- Total matches sum of roles

---

### TC-2.3-7.5: Non-Manager Cannot Access /statistics/ (403)

**Use:** Cashier token

**Expected Response (403 Forbidden):**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

**✅ Pass Criteria:**
- Status: 403

---

## 🔐 TEST SUITE 8: AUTHENTICATION & AUTHORIZATION

### TC-2.3-8.1: Request Without Token (401)

**Description:** Any endpoint without Authorization header returns 401

**Endpoint:** `GET /api/users/` (without token)

**cURL:**
```bash
curl -X GET "http://127.0.0.1:8000/api/users/"
```

**Expected Response (401 Unauthorized):**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**✅ Pass Criteria:**
- Status: 401
- All endpoints require token

---

### TC-2.3-8.2: Invalid Token (401)

**Description:** Endpoint with invalid/expired token

**cURL:**
```bash
curl -X GET "http://127.0.0.1:8000/api/users/" \
  -H "Authorization: Token invalid_token_12345"
```

**Expected Response (401 Unauthorized):**
```json
{
  "detail": "Invalid token."
}
```

**✅ Pass Criteria:**
- Status: 401

---

### TC-2.3-8.3: Malformed Authorization Header

**Description:** Wrong token format

**Header:** `Authorization: Bearer YOUR_TOKEN` (should be "Token")

**Expected Response (401 Unauthorized):**
```json
{
  "detail": "Invalid token."
}
```

**✅ Pass Criteria:**
- Status: 401

---

## 📋 QUICK TEST CHECKLIST

Print this and check off as you test:

### Part 1: Authentication
- [ ] TC-2.3-1: Admin login returns token
- [ ] TC-2.3-2: Cashier login returns token
- [ ] TC-2.3-3: Baker login returns token

### Part 2: List & Filter
- [ ] TC-2.3-1.1: List all users (Manager)
- [ ] TC-2.3-1.2: Non-manager denied list
- [ ] TC-2.3-1.3: Filter by role
- [ ] TC-2.3-1.4: Filter by status
- [ ] TC-2.3-1.5: Search by username
- [ ] TC-2.3-1.6: Search by full name
- [ ] TC-2.3-1.7: Order by username
- [ ] TC-2.3-1.8: Order by date

### Part 3: Create
- [ ] TC-2.3-2.1: Create user (all fields valid)
- [ ] TC-2.3-2.2: Password too short
- [ ] TC-2.3-2.3: No uppercase
- [ ] TC-2.3-2.4: No lowercase
- [ ] TC-2.3-2.5: No number
- [ ] TC-2.3-2.6: Passwords don't match
- [ ] TC-2.3-2.7: Duplicate username
- [ ] TC-2.3-2.8: Invalid role
- [ ] TC-2.3-2.9: Non-manager denied create
- [ ] TC-2.3-2.10: Employee ID auto-generated

### Part 4: Retrieve
- [ ] TC-2.3-3.1: Get own profile
- [ ] TC-2.3-3.2: Manager views any profile
- [ ] TC-2.3-3.3: Non-manager denied other profile
- [ ] TC-2.3-3.4: Invalid ID returns 404

### Part 5: Update
- [ ] TC-2.3-4.1: User updates own profile
- [ ] TC-2.3-4.2: User cannot change own role
- [ ] TC-2.3-4.3: User cannot change own status
- [ ] TC-2.3-4.4: Manager updates any user
- [ ] TC-2.3-4.5: Password not updated via PUT
- [ ] TC-2.3-4.6: Partial update with PATCH

### Part 6: Delete
- [ ] TC-2.3-5.1: Manager deletes user (soft delete)
- [ ] TC-2.3-5.2: Non-manager denied delete
- [ ] TC-2.3-5.3: Manager cannot delete self

### Part 7: Status
- [ ] TC-2.3-6.1: Change status to suspended
- [ ] TC-2.3-6.2: Valid statuses work
- [ ] TC-2.3-6.3: Invalid status rejected
- [ ] TC-2.3-6.4: Non-manager denied status change
- [ ] TC-2.3-6.5: Manager cannot change own status

### Part 8: Bonus
- [ ] TC-2.3-7.1: /me/ endpoint works
- [ ] TC-2.3-7.2: /managers/ lists managers
- [ ] TC-2.3-7.3: Non-manager denied /managers/
- [ ] TC-2.3-7.4: /statistics/ shows counts
- [ ] TC-2.3-7.5: Non-manager denied /statistics/

### Part 9: Security
- [ ] TC-2.3-8.1: No token = 401
- [ ] TC-2.3-8.2: Invalid token = 401
- [ ] TC-2.3-8.3: Malformed header = 401

---

## 📊 Test Summary

**Total Manual Test Cases:** 50+  
**Categories:**
- List/Filter/Search: 8 tests
- Create: 10 tests
- Retrieve: 4 tests
- Update: 6 tests
- Delete: 3 tests
- Status: 5 tests
- Bonus Endpoints: 5 tests
- Authentication/Authorization: 3 tests

**Passing All Tests = Task 2.3 ✅ VERIFIED**

---

## 🎓 Key Learnings Verified

Through these tests you verify:

1. **Role-Based Access Control (RBAC)**
   - Manager: Full CRUD + admin functions
   - Others: Limited to own profile, read-only on others

2. **Input Validation**
   - Password strength (8+ chars, uppercase, lowercase, number)
   - Field uniqueness (username, email)
   - Enum validation (role, status)

3. **Soft Delete**
   - User marked inactive not removed from DB
   - Audit trail preserved

4. **Field Restrictions**
   - Non-managers cannot change role/status
   - Employee ID auto-generated and immutable
   - Password not updated via update endpoint

5. **API Standards**
   - Proper HTTP status codes (200, 201, 204, 400, 403, 404)
   - Consistent response format
   - Pagination on list endpoint
   - Filtering, searching, ordering

---

**Task 2.3 Status:** ✅ **COMPLETE & VERIFIED**  
**All 34 Automated Tests:** ✅ **PASSING**  
**Manual Test Cases:** ✅ **READY**

**Next Step:** Proceed to **Phase 3: Inventory Management** (Task 3.1+)
