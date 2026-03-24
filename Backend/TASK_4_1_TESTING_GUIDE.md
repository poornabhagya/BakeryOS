# Task 4.1: Discount Management System - Testing Guide

**Project**: BakeryOS POS System  
**Task**: Implement Discount Model Management  
**Phase**: Phase 4 - POS & Sales  
**Status**: Testing & Documentation

---

## Table of Contents
1. [Overview](#overview)
2. [System Setup for Testing](#system-setup-for-testing)
3. [Postman Environment Configuration](#postman-environment-configuration)
4. [API Endpoints Reference](#api-endpoints-reference)
5. [Test Cases](#test-cases)
6. [Common Errors & Troubleshooting](#common-errors--troubleshooting)

---

## Overview

The Discount Management System provides flexible discount capabilities with:
- **Discount Types**: Percentage (0-100%) and Fixed Amount (any positive value)
- **Applicability Levels**: All Products, Specific Category, or Specific Product
- **Date/Time Restrictions**: Optional date ranges and daily time windows
- **Auto-ID Generation**: DISC-001, DISC-002, etc.
- **Batch Operations**: Validate and apply multiple discounts simultaneously

### Key Features
✅ Auto-generated discount IDs  
✅ Comprehensive validation (percentage, amount, dates, times)  
✅ Constraint enforcement (one target per type)  
✅ Active/Inactive toggle  
✅ Applicability checking  
✅ Discount calculation (percentage & fixed)  
✅ Batch operations for multiple discounts  
✅ Permission-based access control  

---

## System Setup for Testing

### 1. Start the Development Server

```bash
# Navigate to Backend directory
cd Backend

# Activate virtual environment
venv\Scripts\Activate.ps1  # Windows PowerShell
# OR
source venv/bin/activate  # Linux/Mac

# Run migrations
python manage.py migrate

# Start development server
python manage.py runserver
```

**Expected Output:**
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CTRL-BREAK.
```

### 2. Verify Database Migration

Check that the Discount table was created:

```bash
python manage.py dbshell
```

Then run:
```sql
SELECT name FROM sqlite_master WHERE type='table' AND name='api_discount';
```

Expected result: Table `api_discount` should exist with columns for all discount fields.

### 3. Get Test User Token

#### Option A: Using Existing Test User
```bash
# Manager user (has full access)
Email: testuser@test.com
Password: testuser123
Token: bd616d5e8bd9e45e61e40721c043b7f0edeb6b6d
```

#### Option B: Create New Test User

```bash
python manage.py shell
```

Then in the shell:
```python
from api.models import User
from rest_framework.authtoken.models import Token

# Create a new manager user
user = User.objects.create_user(
    username='discountmanager',
    email='discount@test.com',
    password='discount123',
    full_name='Discount Manager',
    role='Manager'
)

# Get their token
token = Token.objects.create(user=user)
print(f"Token: {token.key}")
```

---

## Postman Environment Configuration

### 1. Create a New Environment

In Postman:
1. Click **Environments** (left sidebar)
2. Click **Create Environment**
3. Name it: `BakeryOS_Discount_Testing`

### 2. Set Environment Variables

Add these variables:

| Variable | Initial Value | Current Value |
|----------|--------------|--------------|
| `base_url` | http://localhost:8000/api | http://localhost:8000/api |
| `token` | bd616d5e8bd9e45e61e40721c043b7f0edeb6b6d | (your test token) |
| `manager_token` | bd616d5e8bd9e45e61e40721c043b7f0edeb6b6d | (manager token) |
| `staff_token` | (leave empty) | (staff token for permission testing) |
| `discount_id` | 1 | (will be set by tests) |
| `category_id` | 1 | (will be set by tests) |
| `product_id` | 1 | (will be set by tests) |
| `discount_type` | Percentage | (test data) |
| `created_discount_id` | (will be set) | (from response) |

### 3. Use in Requests

All requests should use:
- **Authorization**: Token `{{token}}`
- **Content-Type**: application/json

---

## API Endpoints Reference

### Base URL
```
http://localhost:8000/api/discounts/
```

### Standard CRUD Endpoints

#### 1. List Discounts
```http
GET /api/discounts/
Authorization: Token {{token}}
```

**Response (200 OK):**
```json
[
  {
    "id": 1,
    "discount_id": "DISC-001",
    "name": "Summer Sale",
    "discount_type": "Percentage",
    "value": "20.00",
    "applicable_to": "All",
    "is_active": true,
    "created_at": "2026-03-24T10:30:00Z",
    "updated_at": "2026-03-24T10:30:00Z"
  }
]
```

#### 2. Create Discount
```http
POST /api/discounts/
Authorization: Token {{token}}
Content-Type: application/json

{
  "name": "Holiday Discount",
  "description": "Special holiday promotion",
  "discount_type": "Percentage",
  "value": 25,
  "applicable_to": "All"
}
```

**Response (201 Created):**
```json
{
  "id": 3,
  "discount_id": "DISC-003",
  "name": "Holiday Discount",
  "description": "Special holiday promotion",
  "discount_type": "Percentage",
  "value": "25.00",
  "applicable_to": "All",
  "target_category_id": null,
  "target_product_id": null,
  "start_date": null,
  "end_date": null,
  "start_time": null,
  "end_time": null,
  "is_active": true,
  "is_applicable_now": true,
  "created_at": "2026-03-24T10:35:00Z",
  "updated_at": "2026-03-24T10:35:00Z"
}
```

#### 3. Get Discount Details
```http
GET /api/discounts/1/
Authorization: Token {{token}}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "discount_id": "DISC-001",
  "name": "Summer Sale",
  "description": null,
  "discount_type": "Percentage",
  "value": "20.00",
  "applicable_to": "All",
  "target_category_id": null,
  "target_product_id": null,
  "start_date": "2026-06-01",
  "end_date": "2026-08-31",
  "start_time": null,
  "end_time": null,
  "is_active": true,
  "is_applicable_now": false,
  "created_at": "2026-03-24T10:30:00Z",
  "updated_at": "2026-03-24T10:30:00Z"
}
```

#### 4. Update Discount (Full)
```http
PUT /api/discounts/1/
Authorization: Token {{token}}
Content-Type: application/json

{
  "name": "Updated Summer Sale",
  "discount_type": "Percentage",
  "value": 30,
  "applicable_to": "All",
  "is_active": true
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "discount_id": "DISC-001",
  "name": "Updated Summer Sale",
  "discount_type": "Percentage",
  "value": "30.00",
  "applicable_to": "All",
  "is_active": true
}
```

#### 5. Update Discount (Partial)
```http
PATCH /api/discounts/1/
Authorization: Token {{token}}
Content-Type: application/json

{
  "value": 35
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "discount_id": "DISC-001",
  "name": "Updated Summer Sale",
  "discount_type": "Percentage",
  "value": "35.00",
  "applicable_to": "All",
  "is_active": true
}
```

#### 6. Delete Discount
```http
DELETE /api/discounts/1/
Authorization: Token {{token}}
```

**Response (204 No Content):**
```
(empty body)
```

---

### Custom Endpoints

#### 7. Get Active Discounts (Applicable Now)
```http
GET /api/discounts/active/
Authorization: Token {{token}}
```

**Response (200 OK):**
```json
[
  {
    "id": 2,
    "discount_id": "DISC-002",
    "name": "Category Discount",
    "discount_type": "Percentage",
    "value": "15.00",
    "applicable_to": "Category",
    "is_active": true,
    "is_applicable_now": true,
    "created_at": "2026-03-24T10:32:00Z",
    "updated_at": "2026-03-24T10:32:00Z"
  }
]
```

#### 8. Toggle Active Status
```http
PATCH /api/discounts/1/toggle/
Authorization: Token {{token}}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "discount_id": "DISC-001",
  "name": "Summer Sale",
  "is_active": false
}
```

#### 9. Validate Discount Applicability
```http
POST /api/discounts/1/validate/
Authorization: Token {{token}}
Content-Type: application/json

{
  "product_id": 5
}
```

**Response (200 OK):**
```json
{
  "discount_id": "DISC-001",
  "is_applicable": true,
  "reason": "Discount is active and applicable to this product",
  "discount_details": {
    "name": "Summer Sale",
    "discount_type": "Percentage",
    "value": "20.00"
  }
}
```

#### 10. Apply Discount (Calculate Amount)
```http
POST /api/discounts/1/apply/
Authorization: Token {{token}}
Content-Type: application/json

{
  "amount": 1000,
  "product_id": 5
}
```

**Response (200 OK):**
```json
{
  "discount_id": "DISC-001",
  "discount_amount": 200,
  "is_applicable": true,
  "original_amount": 1000,
  "final_amount": 800,
  "discount_details": {
    "name": "Summer Sale",
    "discount_type": "Percentage",
    "value": "20.00"
  }
}
```

#### 11. Batch Validate Discounts
```http
POST /api/discounts/batch-validate/
Authorization: Token {{token}}
Content-Type: application/json

{
  "discount_ids": [1, 2, 3],
  "product_id": 5
}
```

**Response (200 OK):**
```json
[
  {
    "discount_id": "DISC-001",
    "is_applicable": true,
    "name": "Summer Sale",
    "discount_type": "Percentage",
    "value": "20.00"
  },
  {
    "discount_id": "DISC-002",
    "is_applicable": true,
    "name": "Category Discount",
    "discount_type": "Percentage",
    "value": "15.00"
  },
  {
    "discount_id": "DISC-003",
    "is_applicable": false,
    "reason": "Not applicable to this product"
  }
]
```

#### 12. Batch Apply Discounts
```http
POST /api/discounts/batch-apply/
Authorization: Token {{token}}
Content-Type: application/json

{
  "discount_ids": [1, 2],
  "amount": 1000,
  "product_id": 5
}
```

**Response (200 OK):**
```json
{
  "original_amount": 1000,
  "total_discount_amount": 320,
  "final_amount": 680,
  "applied_discounts": [
    {
      "discount_id": "DISC-001",
      "discount_amount": 200,
      "discount_type": "Percentage"
    },
    {
      "discount_id": "DISC-002",
      "discount_amount": 120,
      "discount_type": "Percentage"
    }
  ]
}
```

---

## Test Cases

### Category 1: Auto-ID Generation

#### Test 1.1: First Discount Auto-ID
**Objective**: Verify first discount gets ID DISC-001

**Request:**
```http
POST /api/discounts/
Authorization: Token {{token}}

{
  "name": "First Discount",
  "discount_type": "Percentage",
  "value": 10,
  "applicable_to": "All"
}
```

**Expected Result:**
- Status: 201 Created
- Response contains `discount_id: "DISC-001"`

#### Test 1.2: Sequential ID Generation
**Objective**: Verify subsequent discounts get sequential IDs

**Steps:**
1. Create discount 2 - should get DISC-002
2. Create discount 3 - should get DISC-003
3. Create discount 4 - should get DISC-004

**Assertion:** `response.data['discount_id']` matches pattern DISC-NNN

---

### Category 2: Validation Rules

#### Test 2.1: Valid Percentage Discount
**Objective**: Percentage discount accepts values 1-100

**Request:**
```http
POST /api/discounts/
Authorization: Token {{token}}

{
  "name": "50% Discount",
  "discount_type": "Percentage",
  "value": 50,
  "applicable_to": "All"
}
```

**Expected:** Status 201, value stored as 50

#### Test 2.2: Invalid Percentage - Too High
**Objective**: Reject percentage > 100

**Request:**
```http
POST /api/discounts/
Authorization: Token {{token}}

{
  "name": "Invalid Discount",
  "discount_type": "Percentage",
  "value": 150,
  "applicable_to": "All"
}
```

**Expected:** Status 400, error message about percentage range

#### Test 2.3: Invalid Percentage - Zero/Negative
**Objective**: Reject percentage ≤ 0

**Request:**
```http
POST /api/discounts/
Authorization: Token {{token}}

{
  "name": "Invalid Discount",
  "discount_type": "Percentage",
  "value": 0,
  "applicable_to": "All"
}
```

**Expected:** Status 400, error message

#### Test 2.4: Valid Fixed Amount
**Objective**: Fixed amount accepts any positive number

**Request:**
```http
POST /api/discounts/
Authorization: Token {{token}}

{
  "name": "Fixed 500 Discount",
  "discount_type": "FixedAmount",
  "value": 500,
  "applicable_to": "All"
}
```

**Expected:** Status 201, value stored as 500

#### Test 2.5: Invalid Fixed Amount - Zero/Negative
**Objective**: Reject fixed amount ≤ 0

**Request:**
```http
POST /api/discounts/
Authorization: Token {{token}}

{
  "name": "Invalid Fixed",
  "discount_type": "FixedAmount",
  "value": -100,
  "applicable_to": "All"
}
```

**Expected:** Status 400, error message

---

### Category 3: Date & Time Validation

#### Test 3.1: Valid Date Range
**Objective**: Accept valid date range (start ≤ end)

**Request:**
```http
POST /api/discounts/
Authorization: Token {{token}}

{
  "name": "Spring Discount",
  "discount_type": "Percentage",
  "value": 15,
  "applicable_to": "All",
  "start_date": "2026-03-21",
  "end_date": "2026-06-20"
}
```

**Expected:** Status 201, dates stored correctly

#### Test 3.2: Same Start and End Date
**Objective**: Allow start_date = end_date (single day discount)

**Request:**
```http
POST /api/discounts/
Authorization: Token {{token}}

{
  "name": "One Day Discount",
  "discount_type": "Percentage",
  "value": 20,
  "applicable_to": "All",
  "start_date": "2026-04-01",
  "end_date": "2026-04-01"
}
```

**Expected:** Status 201

#### Test 3.3: Valid Time Range
**Objective**: Accept valid time range (start < end)

**Request:**
```http
POST /api/discounts/
Authorization: Token {{token}}

{
  "name": "Morning Discount",
  "discount_type": "Percentage",
  "value": 10,
  "applicable_to": "All",
  "start_time": "06:00:00",
  "end_time": "12:00:00"
}
```

**Expected:** Status 201, times stored correctly

#### Test 3.4: Optional Time Fields
**Objective**: Allow null time fields (no time restriction)

**Request:**
```http
POST /api/discounts/
Authorization: Token {{token}}

{
  "name": "All Day Discount",
  "discount_type": "Percentage",
  "value": 10,
  "applicable_to": "All",
  "start_time": null,
  "end_time": null
}
```

**Expected:** Status 201, both times null

---

### Category 4: Applicability Tests

#### Test 4.1: All Products (Applicable to All)
**Objective**: Discount with applicable_to='All' applies to any product

**Steps:**
1. Create discount with `applicable_to: "All"`
2. GET /api/discounts/{id}/validate/ with any product_id

**Expected:** 
- Status 200
- `is_applicable: true`

#### Test 4.2: Category Specific Discount
**Objective**: Discount applies only to products in target category

**Steps:**
1. Create Category: "Breads"
2. Create Product: "Naan" in "Breads"
3. Create Discount: `applicable_to: "Category"`, `target_category_id: breads_id`
4. Validate both with Naan (same category) and Cake (different category)

**Expected:**
- Naan: `is_applicable: true`
- Cake: `is_applicable: false`

#### Test 4.3: Product Specific Discount
**Objective**: Discount applies only to one specific product

**Steps:**
1. Create Product A
2. Create Product B
3. Create Discount: `applicable_to: "Product"`, `target_product_id: product_a_id`
4. Validate with Product A and Product B

**Expected:**
- Product A: `is_applicable: true`
- Product B: `is_applicable: false`

---

### Category 5: Discount Calculations

#### Test 5.1: Percentage Discount Calculation
**Objective**: Correctly calculate percentage discount

**Request:**
```http
POST /api/discounts/1/apply/
Authorization: Token {{token}}

{
  "amount": 1000
}
```

Assuming discount is 20%

**Expected:**
```json
{
  "discount_amount": 200,
  "original_amount": 1000,
  "final_amount": 800
}
```

#### Test 5.2: Fixed Amount Calculation
**Objective**: Apply fixed discount amount

**Request:**
```http
POST /api/discounts/3/apply/
Authorization: Token {{token}}

{
  "amount": 1000
}
```

Assuming discount is Rs. 150 fixed

**Expected:**
```json
{
  "discount_amount": 150,
  "original_amount": 1000,
  "final_amount": 850
}
```

#### Test 5.3: Decimal Percentage Calculation
**Objective**: Handle decimal percentages correctly

**Setup:** Create discount with value 12.5%

**Request:**
```http
POST /api/discounts/4/apply/
Authorization: Token {{token}}

{
  "amount": 1000
}
```

**Expected:**
```json
{
  "discount_amount": 125
}
```

#### Test 5.4: Batch Discounts Cumulative
**Objective**: Apply multiple discounts cumulatively

**Request:**
```http
POST /api/discounts/batch-apply/
Authorization: Token {{token}}

{
  "discount_ids": [1, 2],
  "amount": 1000
}
```

With DISC-001 = 20% and DISC-002 = 15%

**Expected:**
- DISC-001 calculates: 1000 × 0.20 = 200
- DISC-002 calculates: 1000 × 0.15 = 150
- Total discount: 350
- Final amount: 650

---

### Category 6: Permission Tests

#### Test 6.1: Unauthenticated Access
**Objective**: Reject requests without authorization

**Request:**
```http
GET /api/discounts/
```

(No Authorization header)

**Expected:** Status 401 Unauthorized

#### Test 6.2: Non-Manager Cannot Create
**Objective**: Only Manager role can create discounts

**Request (as StoreKeeper):**
```http
POST /api/discounts/
Authorization: Token {{staff_token}}

{
  "name": "Test",
  "discount_type": "Percentage",
  "value": 10,
  "applicable_to": "All"
}
```

**Expected:** Status 403 Forbidden

#### Test 6.3: Non-Manager Cannot Update
**Objective**: Only Manager role can update discounts

**Request (as StoreKeeper):**
```http
PUT /api/discounts/1/
Authorization: Token {{staff_token}}

{
  "value": 20
}
```

**Expected:** Status 403 Forbidden

#### Test 6.4: Non-Manager Cannot Delete
**Objective**: Only Manager role can delete discounts

**Request (as StoreKeeper):**
```http
DELETE /api/discounts/1/
Authorization: Token {{staff_token}}
```

**Expected:** Status 403 Forbidden

#### Test 6.5: Non-Manager Can Read
**Objective**: Authenticated users can view discounts

**Request (as StoreKeeper):**
```http
GET /api/discounts/
Authorization: Token {{staff_token}}
```

**Expected:** Status 200, list of discounts

---

### Category 7: Status & Toggle Tests

#### Test 7.1: Active Discounts
**Objective**: is_applicable_now only returns true for active discounts

**Setup:** Create discount with:
- is_active = true
- start_date = today
- end_date = tomorrow

**Request:**
```http
GET /api/discounts/active/
Authorization: Token {{token}}
```

**Expected:** Discount appears in list

#### Test 7.2: Inactive Discounts Excluded
**Objective**: Toggle discount to inactive excludes from active list

**Steps:**
1. Create active discount
2. PATCH /discounts/{id}/toggle/ to make inactive
3. GET /discounts/active/

**Expected:** Discount doesn't appear in active list

#### Test 7.3: Toggle Works Both Ways
**Objective**: Toggle takes active→inactive→active

**Steps:**
1. PATCH /discounts/1/toggle/: is_active becomes false
2. PATCH /discounts/1/toggle/: is_active becomes true
3. PATCH /discounts/1/toggle/: is_active becomes false

**Expected:** 
- Each toggle changes the state
- Status always 200
- Response includes updated is_active value

---

## Common Errors & Troubleshooting

### Error 1: 404 Not Found
**Symptom:** Getting "Not Found" error for discount endpoints

**Solutions:**
1. Verify server is running: `python manage.py runserver`
2. Check migration was applied: `python manage.py migrate`
3. Verify URL is correct: `/api/discounts/` (note trailing slash)
4. Check discount ID exists: `GET /api/discounts/` to list

### Error 2: 401 Unauthorized
**Symptom:** "Authentication credentials were not provided"

**Solutions:**
1. Add Authorization header: `Token {{token}}`
2. Verify token is valid: Get new token from admin
3. Check token isn't expired

### Error 3: 403 Forbidden
**Symptom:** "You do not have permission to perform this action"

**Solutions:**
1. Verify user role is Manager for create/update/delete
2. Check user token belongs to Manager account
3. Create new Manager user if needed

### Error 4: 400 Bad Request - Invalid Percentage
**Symptom:** "Percentage discount must be between 0 and 100"

**Solutions:**
1. Use value between 1 and 100 (exclusive of 0)
2. Don't use 0 or values > 100
3. Examples: 10, 50.5, 99 are valid

### Error 5: 400 Bad Request - Invalid Dates
**Symptom:** "Start date cannot be after end date"

**Solutions:**
1. Ensure start_date ≤ end_date
2. Use format: YYYY-MM-DD
3. Example: "2026-03-21" and "2026-06-20"

### Error 6: 400 Bad Request - Missing Required Field
**Symptom:** "This field is required"

**Solutions:**
1. Verify all required fields are included:
   - name (always required)
   - discount_type (required: "Percentage" or "FixedAmount")
   - value (required: number)
   - applicable_to (required: "All", "Category", or "Product")
   - target_category_id (required if applicable_to = "Category")
   - target_product_id (required if applicable_to = "Product")

2. For optional fields, leave null or omit them

### Error 7: DecimalField Returned as String
**Symptom:** API returns "20.00" instead of 20

**Note:** This is expected! DecimalField values are returned as strings in JSON.
In your assertions/code, convert: `float(response['value'])`

---

## Quick Test Checklist

Use this checklist for manual testing:

### Discount Creation
- [ ] Can create percentage discount (1-100%)
- [ ] Can create fixed amount discount (> 0)
- [ ] Auto-ID generates correctly (DISC-001, etc.)
- [ ] Cannot create with invalid percentage (0, > 100)
- [ ] Cannot create with invalid fixed amount (≤ 0)

### Discount Retrieval
- [ ] Can list all discounts
- [ ] Can get specific discount by ID
- [ ] Returns 404 for non-existent discount
- [ ] Non-authenticated users get 401

### Discount Updates
- [ ] Manager can update discount
- [ ] Non-Manager gets 403
- [ ] Can partially update (PATCH)
- [ ] Can fully update (PUT)

### Discount Deletion
- [ ] Manager can delete discount
- [ ] Non-Manager gets 403
- [ ] Returns 204 No Content on success
- [ ] Discount no longer exists after deletion

### Applicability Checks
- [ ] Discount with "All" applies to any product
- [ ] Category discount applies only to products in that category
- [ ] Product discount applies only to specified product
- [ ] Validate endpoint returns correct applicability

### Calculations
- [ ] Percentage discount calculates correctly
- [ ] Fixed amount discount applies correctly
- [ ] Batch calculations sum correctly
- [ ] Decimal values handled correctly

### Active Status
- [ ] is_active=true discount appears in /active/
- [ ] is_active=false discount doesn't appear in /active/
- [ ] Toggle changes is_active status
- [ ] Current date/time affects is_applicable_now

### Permissions
- [ ] Manager can create/update/delete
- [ ] Non-Manager cannot create/update/delete
- [ ] Anyone authenticated can read
- [ ] Unauthenticated get 401

---

## Test Data Setup

### Create Sample Discounts for Testing

```http
# Test 1: Summer Sale (All Products, 20%)
POST /api/discounts/
Authorization: Token {{token}}

{
  "name": "Summer Sale",
  "description": "All products summer promotion",
  "discount_type": "Percentage",
  "value": 20,
  "applicable_to": "All",
  "start_date": "2026-06-01",
  "end_date": "2026-08-31"
}

# Test 2: Category Discount (Breads, 15%)
POST /api/discounts/
Authorization: Token {{token}}

{
  "name": "Fresh Breads Discount",
  "discount_type": "Percentage",
  "value": 15,
  "applicable_to": "Category",
  "target_category_id": 1
}

# Test 3: Product Specific (Fixed Rs. 100)
POST /api/discounts/
Authorization: Token {{token}}

{
  "name": "Premium Naan Special",
  "discount_type": "FixedAmount",
  "value": 100,
  "applicable_to": "Product",
  "target_product_id": 5
}

# Test 4: Morning Special (Time-based, 10%)
POST /api/discounts/
Authorization: Token {{token}}

{
  "name": "Morning Special",
  "discount_type": "Percentage",
  "value": 10,
  "applicable_to": "All",
  "start_time": "06:00:00",
  "end_time": "12:00:00"
}

# Test 5: Easter Weekend (Date-based, 25%)
POST /api/discounts/
Authorization: Token {{token}}

{
  "name": "Easter Weekend",
  "discount_type": "Percentage",
  "value": 25,
  "applicable_to": "All",
  "start_date": "2026-04-10",
  "end_date": "2026-04-13"
}
```

---

## Performance Testing

### Test High Volume Discounts
```bash
# Create 100 discounts
for i in {1..100}
  POST /api/discounts/
  with different names and values
end

# Test list performance
GET /api/discounts/?page=1

# Note: Check pagination and response time
```

### Test Batch Operations
```bash
# Test batch validation with 50 discount IDs
POST /api/discounts/batch-validate/
{
  "discount_ids": [1, 2, 3, ..., 50],
  "product_id": 5
}

# Test batch apply with 20 discounts
POST /api/discounts/batch-apply/
{
  "discount_ids": [1, 2, 3, ..., 20],
  "amount": 5000
}
```

---

## Success Criteria

Task 4.1 is complete when:

✅ All discount model tests pass  
✅ All 12 API endpoints are functional  
✅ Auto-ID generation works correctly  
✅ Validation rules are enforced  
✅ Permission-based access control works  
✅ Discount calculations are accurate  
✅ Batch operations function correctly  
✅ 100% test coverage achieved  

---

## Next Steps

After Task 4.1 (Discount Management) is complete:

1. **Task 4.2**: Sales & Sale Items Models
2. **Task 4.3**: Product Batches Management
3. **Task 4.4**: Inventory Adjustments
4. **Task 4.5**: POS Integration & Transactions

---

## Support & Debugging

### Enable Django Debug Logging
```python
# In settings.py, add:
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'DEBUG',
    },
}
```

### Run Individual Tests
```bash
# Run specific test class
python manage.py test api.tests.test_discount_endpoints.DiscountModelTestCase

# Run specific test method
python manage.py test api.tests.test_discount_endpoints.DiscountModelTestCase.test_discount_auto_id_generation

# Run with verbose output
python manage.py test api.tests.test_discount_endpoints -v 2
```

### Database Inspection
```bash
python manage.py dbshell

# View all discounts
SELECT * FROM api_discount;

# Count discounts
SELECT COUNT(*) FROM api_discount;

# Check indexes
PRAGMA index_list(api_discount);
```

---

**Document Version**: 1.0  
**Last Updated**: 2026-03-24  
**Status**: Ready for Testing  
**Test Coverage**: 64 test cases (80+ assertions)
