# Task 5.3: Ingredient Wastage Tracking - Manual Testing Guide

**Date:** March 25, 2026  
**Task:** Task 5.3 - Implement Ingredient Wastage Tracking  
**Status:** ✅ **COMPLETE**  
**Automated Tests:** 11/11 PASSED

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Test Environment Setup](#test-environment-setup)
3. [API Endpoints Reference](#api-endpoints-reference)
4. [Manual Test Procedures](#manual-test-procedures)
5. [Expected Responses](#expected-responses)
6. [Error Scenarios](#error-scenarios)
7. [Validation Rules](#validation-rules)
8. [Permission Checks](#permission-checks)
9. [Quick Reference](#quick-reference)

---

## 🎯 Overview

### What Was Implemented

**Task 5.3: Ingredient Wastage Tracking**

A comprehensive system to track ingredient wastage events with financial impact and reason tracking.

**Key Components:**
- ✅ IngredientWastage Model with auto-ID generation (IW-001, IW-002, etc.)
- ✅ 1 Serializer (IngredientWastageSerializer)
- ✅ 1 ViewSet with full CRUD operations
- ✅ URL routing configured at `/api/ingredient-wastages/`
- ✅ Database migration applied
- ✅ Comprehensive test suite (11 tests passing)
- ✅ Automatic total_loss calculation

### Model Structure

```
IngredientWastage
├── id (Auto PK)
├── wastage_id (Auto: IW-001, IW-002, etc.)
├── ingredient_id (FK to Ingredient)
├── batch_id (FK to IngredientBatch, optional)
├── quantity (Decimal)
├── unit_cost (Decimal)
├── total_loss (Auto-calculated: quantity * unit_cost)
├── reason_id (FK to WastageReason)
├── reported_by (FK to User)
├── notes (Optional)
├── created_at (Auto timestamp)
└── updated_at (Auto on modification)
```

### Key Features

1. **Auto-ID Generation** - Generates wastage_id in IW-001 format
2. **Total Loss Calculation** - Auto-calculates total_loss = quantity × unit_cost
3. **Role-Based Access** - Manager and Storekeeper can create; only Manager can delete
4. **Batch Tracking** - Optional link to specific IngredientBatch
5. **Financial Tracking** - Tracks unit cost and total loss for reporting
6. **Audit Trail** - Automatic timestamps and user tracking

---

## 🔧 Test Environment Setup

### Prerequisites

1. Django development server running
2. Backend virtual environment activated
3. Database migrated
4. Test users created

### Starting Django Server

```bash
cd Backend
.\venv\Scripts\Activate
python manage.py runserver
```

### Test Users

```
Manager      (username: manager, password: testpass123, role: Manager)
Storekeeper  (username: storekeeper, password: testpass123, role: Storekeeper)
Cashier      (username: cashier, password: testpass123, role: Cashier)
Baker        (username: baker, password: testpass123, role: Baker)
```

### Getting Auth Token

**Request:**
```
POST http://localhost:8000/api/auth/login/
Content-Type: application/json

{
  "username": "manager",
  "password": "testpass123"
}
```

**Response:**
```json
{
  "token": "9b8c7a6d5e4f3g2h1i0j...",
  "user_id": 1,
  "username": "manager",
  "role": "Manager"
}
```

---

## 🔗 API Endpoints Reference

### Base URL
```
http://localhost:8000/api
```

### Endpoints

| Method | Endpoint | Auth | Purpose |
|--------|----------|------|---------|
| GET | `/ingredient-wastages/` | ✅ Required | List all wastages |
| POST | `/ingredient-wastages/` | ✅ Required | Create new wastage |
| GET | `/ingredient-wastages/{id}/` | ✅ Required | Get wastage details |
| PATCH | `/ingredient-wastages/{id}/` | ✅ Required | Update wastage (Manager only) |
| DELETE | `/ingredient-wastages/{id}/` | ✅ Required | Delete wastage (Manager only) |

### Query Parameters

```
GET /api/ingredient-wastages/?ingredient_id=1
GET /api/ingredient-wastages/?reason_id=1
GET /api/ingredient-wastages/?start_date=2026-03-20&end_date=2026-03-25
```

---

## 🧪 Manual Test Procedures

### Test 1: List All Ingredient Wastages

**Objective:** Verify we can retrieve all ingredient wastages

**Request:**
```
GET /api/ingredient-wastages/
Authorization: Token YOUR_TOKEN
```

**Expected Response:** ✅ HTTP 200 OK

```json
{
  "count": 0,
  "next": null,
  "previous": null,
  "results": []
}
```

**Verification Checklist:**
- ✓ Response code is 200
- ✓ Results array present (may be empty)
- ✓ Pagination fields present (count, next, previous)

---

### Test 2: Create Ingredient Wastage by Manager

**Objective:** Test wastage creation with full details

**Prerequisites:**
- Ingredient exists: id=1, name="Flour", category="Dry Goods"
- Wastage reason exists: id=1, reason="Expired"

**Request:**
```
POST /api/ingredient-wastages/
Authorization: Token MANAGER_TOKEN
Content-Type: application/json

{
  "ingredient_id": 1,
  "quantity": "5.50",
  "unit_cost": "10.25",
  "reason_id": 1,
  "notes": "Batch expired on 2026-03-20"
}
```

**Expected Response:** ✅ HTTP 201 CREATED

```json
{
  "id": 1,
  "wastage_id": "IW-001",
  "ingredient_id": 1,
  "ingredient_name": "Flour",
  "quantity": "5.50",
  "unit_cost": "10.25",
  "total_loss": "56.38",
  "reason_id": 1,
  "reason": "Expired",
  "reported_by": 1,
  "reported_by_username": "manager",
  "notes": "Batch expired on 2026-03-20",
  "batch_id": null,
  "created_at": "2026-03-25T10:30:00Z",
  "updated_at": "2026-03-25T10:30:00Z"
}
```

**Verification Checklist:**
- ✓ Response code is 201
- ✓ wastage_id auto-generated (IW-001)
- ✓ total_loss calculated correctly (5.50 × 10.25 = 56.38)
- ✓ reported_by auto-set to current user (Manager)
- ✓ Created timestamp is set
- ✓ Ingredient details returned

---

### Test 3: Create Wastage by Storekeeper

**Objective:** Verify Storekeeper role can create wastage

**Request:**
```
POST /api/ingredient-wastages/
Authorization: Token STOREKEEPER_TOKEN
Content-Type: application/json

{
  "ingredient_id": 1,
  "quantity": "2.00",
  "unit_cost": "10.25",
  "reason_id": 2
}
```

**Expected Response:** ✅ HTTP 201 CREATED

```json
{
  "id": 2,
  "wastage_id": "IW-002",
  "ingredient_id": 1,
  "quantity": "2.00",
  "unit_cost": "10.25",
  "total_loss": "20.50",
  "reason_id": 2,
  "reported_by": 2
}
```

**Verification Checklist:**
- ✓ Response code is 201
- ✓ Storekeeper can create wastage
- ✓ reported_by auto-set to current user (Storekeeper)
- ✓ wastage_id sequence maintained (IW-002)

---

### Test 4: Attempt to Create Wastage by Cashier (Should Fail)

**Objective:** Verify Cashier role CANNOT create wastage

**Request:**
```
POST /api/ingredient-wastages/
Authorization: Token CASHIER_TOKEN
Content-Type: application/json

{
  "ingredient_id": 1,
  "quantity": "3.00",
  "unit_cost": "10.25",
  "reason_id": 1
}
```

**Expected Response:** ❌ HTTP 403 FORBIDDEN

```json
{
  "detail": "You do not have permission to perform this action."
}
```

**Verification Checklist:**
- ✓ Response code is 403
- ✓ Cashier denied access
- ✓ Error message returned

---

### Test 5: Create Wastage Without Authentication (Should Fail)

**Objective:** Verify unauthenticated request is rejected

**Request:**
```
POST /api/ingredient-wastages/
Content-Type: application/json

{
  "ingredient_id": 1,
  "quantity": "5.00",
  "unit_cost": "10.25",
  "reason_id": 1
}
```

**Expected Response:** ❌ HTTP 401 UNAUTHORIZED

```json
{
  "detail": "Authentication credentials were not provided."
}
```

**Verification Checklist:**
- ✓ Response code is 401
- ✓ Error message indicates authentication required

---

### Test 6: Retrieve Ingredient Wastage by ID

**Objective:** Get details of a specific wastage record

**Request:**
```
GET /api/ingredient-wastages/1/
Authorization: Token YOUR_TOKEN
```

**Expected Response:** ✅ HTTP 200 OK

```json
{
  "id": 1,
  "wastage_id": "IW-001",
  "ingredient_id": 1,
  "ingredient_name": "Flour",
  "quantity": "5.50",
  "unit_cost": "10.25",
  "total_loss": "56.38",
  "reason_id": 1,
  "reason": "Expired",
  "reported_by": 1,
  "reported_by_username": "manager",
  "notes": "Batch expired on 2026-03-20",
  "batch_id": null,
  "created_at": "2026-03-25T10:30:00Z",
  "updated_at": "2026-03-25T10:30:00Z"
}
```

**Verification Checklist:**
- ✓ Response code is 200
- ✓ All fields present
- ✓ Correct wastage returned
- ✓ Calculated total_loss displayed

---

### Test 7: Filter by Ingredient

**Objective:** Get wastages for specific ingredient

**Request:**
```
GET /api/ingredient-wastages/?ingredient_id=1
Authorization: Token YOUR_TOKEN
```

**Expected Response:** ✅ HTTP 200 OK

```json
{
  "count": 2,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 2,
      "wastage_id": "IW-002",
      "ingredient_id": 1,
      "quantity": "2.00",
      "unit_cost": "10.25",
      "total_loss": "20.50"
    },
    {
      "id": 1,
      "wastage_id": "IW-001",
      "ingredient_id": 1,
      "quantity": "5.50",
      "unit_cost": "10.25",
      "total_loss": "56.38"
    }
  ]
}
```

**Verification Checklist:**
- ✓ Response code is 200
- ✓ Only wastages for ingredient_id=1 returned
- ✓ Count shows 2
- ✓ Results ordered correctly (newest first)

---

### Test 8: Filter by Wastage Reason

**Objective:** Get wastages with specific reason

**Request:**
```
GET /api/ingredient-wastages/?reason_id=1
Authorization: Token YOUR_TOKEN
```

**Expected Response:** ✅ HTTP 200 OK

```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "wastage_id": "IW-001",
      "ingredient_id": 1,
      "reason_id": 1,
      "reason": "Expired",
      "quantity": "5.50"
    }
  ]
}
```

**Verification Checklist:**
- ✓ Response code is 200
- ✓ Only wastages with reason_id=1 returned
- ✓ Reason detail included in response

---

### Test 9: Update Wastage by Manager

**Objective:** Verify Manager can update wastage

**Request:**
```
PATCH /api/ingredient-wastages/1/
Authorization: Token MANAGER_TOKEN
Content-Type: application/json

{
  "quantity": "7.00",
  "notes": "Updated: Actually 7 units wasted"
}
```

**Expected Response:** ✅ HTTP 200 OK

```json
{
  "id": 1,
  "wastage_id": "IW-001",
  "ingredient_id": 1,
  "quantity": "7.00",
  "unit_cost": "10.25",
  "total_loss": "71.75",
  "notes": "Updated: Actually 7 units wasted",
  "updated_at": "2026-03-25T10:35:00Z"
}
```

**Verification Checklist:**
- ✓ Response code is 200
- ✓ Quantity updated correctly
- ✓ Notes updated
- ✓ total_loss recalculated (7.00 × 10.25 = 71.75)
- ✓ updated_at timestamp changed

---

### Test 10: Delete Wastage by Manager

**Objective:** Verify Manager can delete wastage

**Request:**
```
DELETE /api/ingredient-wastages/1/
Authorization: Token MANAGER_TOKEN
```

**Expected Response:** ✅ HTTP 204 NO CONTENT

(No body returned)

**Verification Checklist:**
- ✓ Response code is 204
- ✓ No response body
- ✓ Wastage record deleted from database
- ✓ Subsequent GET returns 404

---

### Test 11: Attempt to Delete by Non-Manager (Should Fail)

**Objective:** Verify only Manager can delete wastage

**Request:**
```
DELETE /api/ingredient-wastages/2/
Authorization: Token STOREKEEPER_TOKEN
```

**Expected Response:** ❌ HTTP 403 FORBIDDEN

```json
{
  "detail": "You do not have permission to perform this action."
}
```

**Verification Checklist:**
- ✓ Response code is 403
- ✓ Storekeeper denied access
- ✓ Wasteage record still exists in database

---

## ❌ Error Scenarios

### Scenario 1: Missing Required Field (ingredient_id)

**Request:**
```
POST /api/ingredient-wastages/
Authorization: Token MANAGER_TOKEN
Content-Type: application/json

{
  "quantity": "5.00",
  "unit_cost": "10.00",
  "reason_id": 1
}
```

**Expected Response:** ❌ HTTP 400 BAD REQUEST

```json
{
  "ingredient_id": ["This field is required."]
}
```

---

### Scenario 2: Invalid Ingredient ID

**Request:**
```
POST /api/ingredient-wastages/
Authorization: Token MANAGER_TOKEN
Content-Type: application/json

{
  "ingredient_id": 9999,
  "quantity": "5.00",
  "unit_cost": "10.00",
  "reason_id": 1
}
```

**Expected Response:** ❌ HTTP 400 BAD REQUEST

```json
{
  "ingredient_id": ["Invalid pk \"9999\" - object does not exist."]
}
```

---

### Scenario 3: Negative Quantity

**Request:**
```
POST /api/ingredient-wastages/
Authorization: Token MANAGER_TOKEN
Content-Type: application/json

{
  "ingredient_id": 1,
  "quantity": "-5.00",
  "unit_cost": "10.00",
  "reason_id": 1
}
```

**Expected Response:** ❌ HTTP 400 BAD REQUEST

```json
{
  "quantity": ["Ensure this value is greater than or equal to 0.01."]
}
```

---

### Scenario 4: Nonexistent Wastage ID

**Request:**
```
GET /api/ingredient-wastages/9999/
Authorization: Token MANAGER_TOKEN
```

**Expected Response:** ❌ HTTP 404 NOT FOUND

```json
{
  "detail": "Not found."
}
```

---

## ✅ Validation Rules

| Field | Type | Validation | Notes |
|-------|------|-----------|-------|
| ingredient_id | Foreign Key | Required, must exist | Link to Ingredient record |
| quantity | Decimal | Required, ≥ 0.01 | Quantity wasted |
| unit_cost | Decimal | Required, ≥ 0 | Cost per unit at time of wastage |
| reason_id | Foreign Key | Required, must exist | Link to WastageReason |
| batch_id | Foreign Key | Optional, must exist if provided | Link to IngredientBatch |
| reported_by | Foreign Key | Auto-set to current user | Cannot be set manually |
| notes | Text | Optional, max 1000 chars | Additional details |
| wastage_id | String | Auto-generated | IW-001, IW-002, etc. |
| total_loss | Decimal | Auto-calculated | quantity × unit_cost |

---

## 🔐 Permission Checks

### Create Permission
- ✅ **Manager** - Can create
- ✅ **Storekeeper** - Can create
- ❌ **Cashier** - Cannot create
- ❌ **Baker** - Cannot create
- ❌ **Anonymous** - Cannot create (401)

### Update Permission
- ✅ **Manager** - Can update
- ❌ **Storekeeper** - Cannot update
- ❌ **Cashier** - Cannot update
- ❌ **Baker** - Cannot update
- ❌ **Anonymous** - Cannot update (401)

### Delete Permission
- ✅ **Manager** - Can delete
- ❌ **Storekeeper** - Cannot delete
- ❌ **Cashier** - Cannot delete
- ❌ **Baker** - Cannot delete
- ❌ **Anonymous** - Cannot delete (401)

### List/Retrieve Permission
- ✅ **All Authenticated Users** - Can list and retrieve
- ❌ **Anonymous** - Cannot list/retrieve (401)

---

## 📋 Quick Reference

### Common Requests

**Get Token:**
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"manager","password":"testpass123"}'
```

**List Wastages:**
```bash
curl http://localhost:8000/api/ingredient-wastages/ \
  -H "Authorization: Token YOUR_TOKEN"
```

**Create Wastage:**
```bash
curl -X POST http://localhost:8000/api/ingredient-wastages/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ingredient_id": 1,
    "quantity": "5.50",
    "unit_cost": "10.25",
    "reason_id": 1,
    "notes": "Batch expired"
  }'
```

**Get Specific Wastage:**
```bash
curl http://localhost:8000/api/ingredient-wastages/1/ \
  -H "Authorization: Token YOUR_TOKEN"
```

**Update Wastage:**
```bash
curl -X PATCH http://localhost:8000/api/ingredient-wastages/1/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"quantity": "7.00"}'
```

**Delete Wastage:**
```bash
curl -X DELETE http://localhost:8000/api/ingredient-wastages/1/ \
  -H "Authorization: Token YOUR_TOKEN"
```

**Filter by Ingredient:**
```bash
curl http://localhost:8000/api/ingredient-wastages/?ingredient_id=1 \
  -H "Authorization: Token YOUR_TOKEN"
```

**Filter by Reason:**
```bash
curl http://localhost:8000/api/ingredient-wastages/?reason_id=1 \
  -H "Authorization: Token YOUR_TOKEN"
```

---

## 📊 Test Summary

| Test | Expected | Result | Notes |
|------|----------|--------|-------|
| List wastages | 200 | ✅ | Pagination working |
| Create (Manager) | 201 | ✅ | Auto ID generation |
| Create (Storekeeper) | 201 | ✅ | Role-based access |
| Create (Cashier) | 403 | ✅ | Permission denied |
| Retrieve | 200 | ✅ | Full details returned |
| Update (Manager) | 200 | ✅ | Recalculates total_loss |
| Delete (Manager) | 204 | ✅ | Record removed |
| Delete (Storekeeper) | 403 | ✅ | Permission denied |
| Filter by ingredient | 200 | ✅ | Correct filtering |
| Filter by reason | 200 | ✅ | Correct filtering |
| 404 for nonexistent | 404 | ✅ | Proper error handling |

**Overall Status:** ✅ **ALL TESTS PASS**

---

## 🎯 Conclusion

Task 5.3 (Ingredient Wastage Tracking) has been fully implemented and tested. All manual test procedures pass, demonstrating:

- ✅ Proper CRUD operations
- ✅ Role-based access control
- ✅ Automatic ID generation
- ✅ Correct financial calculations
- ✅ Comprehensive error handling
- ✅ Full API documentation

The system is ready for production use.
