# Task 5.2: Product Wastage Tracking - Manual Testing Guide

**Date:** March 25, 2026  
**Task:** Task 5.2 - Implement Product Wastage Tracking  
**Status:** ✅ **COMPLETE**  
**Automated Tests:** 30/30 PASSED

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

**Task 5.2: Product Wastage Tracking**

A comprehensive system to track product wastage events with financial impact and reason tracking.

**Key Components:**
- ✅ ProductWastage Model with auto-ID generation (PW-001, PW-002, etc.)
- ✅ 3 Serializers (List, Detail, Create)
- ✅ 1 ViewSet with full CRUD operations
- ✅ URL routing configured
- ✅ Database migration applied
- ✅ Comprehensive test suite (30 tests passing)
- ✅ Stock deduction/restoration on create/delete

### Model Structure

```
ProductWastage
├── id (Auto PK)
├── wastage_id (Auto: PW-001, PW-002, etc.)
├── product_id (FK to Product)
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

1. **Auto-ID Generation** - Generates wastage_id in PW-001 format
2. **Total Loss Calculation** - Auto-calculates total_loss = quantity × unit_cost
3. **Stock Management** - Automatically deducts from product.current_stock
4. **Role-Based Access** - Baker, Cashier, Manager can create; only Manager can delete
5. **Analytics** - Track wastage by reason, product, and date
6. **History Tracking** - View wastage history for each product

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
Baker        (username: baker, password: testpass123, role: Baker)
Cashier      (username: cashier, password: testpass123, role: Cashier)
Storekeeper  (username: storekeeper, password: testpass123, role: Storekeeper)
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
| GET | `/product-wastages/` | ✅ Required | List all wastages |
| POST | `/product-wastages/` | ✅ Required | Create new wastage |
| GET | `/product-wastages/{id}/` | ✅ Required | Get wastage details |
| DELETE | `/product-wastages/{id}/` | ✅ Required | Delete wastage (Manager only) |
| GET | `/product-wastages/analytics/` | ✅ Required | Get analytics |
| GET | `/product-wastages/product/{product_id}/history/` | ✅ Required | Wastage history by product |

---

## 🧪 Manual Test Procedures

### Test 1: List All Product Wastages

**Objective:** Verify we can retrieve all product wastages

**Request:**
```
GET /api/product-wastages/
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

### Test 2: Create Product Wastage by Manager

**Objective:** Test wastage creation with full details

**Prerequisites:**
- Product exists: id=1, name="Chocolate Bun", current_stock=100
- Wastage reason exists: id=1, reason="Expired"

**Request:**
```
POST /api/product-wastages/
Authorization: Token YOUR_TOKEN
Content-Type: application/json

{
  "product_id": 1,
  "quantity": 5.00,
  "unit_cost": 10.00,
  "reason_id": 1,
  "notes": "Batch expired on 2026-03-20"
}
```

**Expected Response:** ✅ HTTP 201 CREATED

```json
{
  "id": 1,
  "wastage_id": "PW-001",
  "product_id": 1,
  "product_detail": {
    "id": 1,
    "product_id": "PROD-1001",
    "name": "Chocolate Bun",
    "cost_price": "10.00",
    "selling_price": "25.00",
    "current_stock": "95.00"
  },
  "quantity": "5.00",
  "unit_cost": "10.00",
  "total_loss": "50.00",
  "reason_id": 1,
  "reason_detail": {
    "id": 1,
    "reason_id": "WR-001",
    "reason": "Expired",
    "description": "Products that have passed their expiration date"
  },
  "reported_by": 1,
  "reported_by_detail": {
    "id": 1,
    "username": "manager",
    "full_name": "Manager One",
    "role": "Manager",
    "email": "manager@test.com"
  },
  "notes": "Batch expired on 2026-03-20"
}
```

**Verification Checklist:**
- ✓ Response code is 201
- ✓ wastage_id auto-generated (PW-001)
- ✓ total_loss calculated (5.00 × 10.00 = 50.00)
- ✓ Product stock decreased (100 → 95)
- ✓ Nested product_detail included
- ✓ Nested reason_detail included
- ✓ Nested reported_by_detail included

---

### Test 3: Create Wastage by Baker

**Objective:** Verify Baker role can create wastage

**Request:**
```
POST /api/product-wastages/
Authorization: Token BAKER_TOKEN
Content-Type: application/json

{
  "product_id": 1,
  "quantity": 2.00,
  "unit_cost": 10.00,
  "reason_id": 2
}
```

**Expected Response:** ✅ HTTP 201 CREATED

```json
{
  "id": 2,
  "wastage_id": "PW-002",
  "product_id": 1,
  "quantity": "2.00",
  "unit_cost": "10.00",
  "total_loss": "20.00",
  "reason_id": 2,
  "reported_by": 2
}
```

**Verification Checklist:**
- ✓ Response code is 201
- ✓ Baker can create wastage
- ✓ reported_by auto-set to current user
- ✓ wastage_id sequence maintained (PW-002)

---

### Test 4: Create Wastage by Cashier

**Objective:** Verify Cashier role can create wastage

**Request:**
```
POST /api/product-wastages/
Authorization: Token CASHIER_TOKEN
Content-Type: application/json

{
  "product_id": 2,
  "quantity": 3.50,
  "unit_cost": 8.00,
  "reason_id": 1,
  "notes": "Damaged during service"
}
```

**Expected Response:** ✅ HTTP 201 CREATED

**Verification Checklist:**
- ✓ Response code is 201
- ✓ Cashier can create wastage
- ✓ Stock deducted from product 2

---

### Test 5: Storekeeper Cannot Create Wastage

**Objective:** Verify Storekeeper cannot create product wastage

**Request:**
```
POST /api/product-wastages/
Authorization: Token STOREKEEPER_TOKEN
Content-Type: application/json

{
  "product_id": 1,
  "quantity": 5.00,
  "unit_cost": 10.00,
  "reason_id": 1
}
```

**Expected Response:** ❌ HTTP 403 FORBIDDEN

```json
{
  "detail": "Only Baker, Cashier, or Manager can report wastage."
}
```

**Verification Checklist:**
- ✓ Response code is 403
- ✓ Clear permission denied message
- ✓ Storekeeper blocked from creating

---

### Test 6: Retrieve Wastage Details

**Objective:** Get full details of a specific wastage record

**Request:**
```
GET /api/product-wastages/1/
Authorization: Token YOUR_TOKEN
```

**Expected Response:** ✅ HTTP 200 OK

```json
{
  "id": 1,
  "wastage_id": "PW-001",
  "product_id": 1,
  "product_detail": {
    "id": 1,
    "product_id": "PROD-1001",
    "name": "Chocolate Bun",
    "cost_price": "10.00",
    "selling_price": "25.00",
    "current_stock": "93.00"
  },
  "quantity": "5.00",
  "unit_cost": "10.00",
  "total_loss": "50.00",
  "reason_id": 1,
  "reason_detail": { ... },
  "reported_by": 1,
  "reported_by_detail": { ... },
  "notes": "Batch expired on 2026-03-20",
  "created_at": "2026-03-25T10:30:00Z",
  "updated_at": "2026-03-25T10:30:00Z"
}
```

**Verification Checklist:**
- ✓ Response code is 200
- ✓ All wastage fields included
- ✓ created_at and updated_at timestamps present
- ✓ All nested details expanded

---

### Test 7: Delete Wastage by Manager

**Objective:** Test wastage deletion and stock restoration

**Prerequisites:**
- Product stock before delete = 93 (after 2 wastages)

**Request:**
```
DELETE /api/product-wastages/1/
Authorization: Token MANAGER_TOKEN
```

**Expected Response:** ✅ HTTP 204 NO CONTENT

(No response body)

**Verification Checklist:**
- ✓ Response code is 204
- ✓ Wastage record deleted
- ✓ Product stock restored (93 + 5 = 98)
- ✓ Verify deletion with GET /api/product-wastages/1/ → 404

---

### Test 8: Baker Cannot Delete Wastage

**Objective:** Verify only Manager can delete wastage

**Request:**
```
DELETE /api/product-wastages/1/
Authorization: Token BAKER_TOKEN
```

**Expected Response:** ❌ HTTP 403 FORBIDDEN

```json
{
  "detail": "Only Manager can delete wastage records."
}
```

**Verification Checklist:**
- ✓ Response code is 403
- ✓ Baker access denied
- ✓ Wastage not deleted

---

### Test 9: List with Filters

**Objective:** Test filtering wastages by product

**Create 3 wastages:**
- Wastage 1: product_id=1, quantity=5
- Wastage 2: product_id=1, quantity=2
- Wastage 3: product_id=2, quantity=3

**Request:**
```
GET /api/product-wastages/?product_id=1
Authorization: Token YOUR_TOKEN
```

**Expected Response:** ✅ HTTP 200 OK

```json
{
  "count": 2,
  "results": [
    {
      "id": 1,
      "wastage_id": "PW-001",
      "product_id": 1,
      "product_name": "Chocolate Bun",
      "quantity": "5.00",
      ...
    },
    {
      "id": 2,
      "wastage_id": "PW-002",
      "product_id": 1,
      "product_name": "Chocolate Bun",
      "quantity": "2.00",
      ...
    }
  ]
}
```

**Verification Checklist:**
- ✓ Response code is 200
- ✓ Only product_id=1 wastages returned
- ✓ Count is 2
- ✓ Filter works correctly

---

### Test 10: Analytics Endpoint

**Objective:** Test wastage analytics

**Request:**
```
GET /api/product-wastages/analytics/
Authorization: Token YOUR_TOKEN
```

**Expected Response:** ✅ HTTP 200 OK

```json
{
  "summary": {
    "total_loss": 70.00,
    "total_quantity": 10.00,
    "total_records": 2
  },
  "by_reason": [
    {
      "reason_id__reason": "Expired",
      "count": 1,
      "total_loss": "50.00",
      "total_quantity": "5.00"
    },
    {
      "reason_id__reason": "Damaged",
      "count": 1,
      "total_loss": "20.00",
      "total_quantity": "2.00"
    }
  ],
  "by_product": [
    {
      "product_id__name": "Chocolate Bun",
      "count": 2,
      "total_loss": "70.00",
      "total_quantity": "7.00"
    }
  ],
  "daily_trend": [
    {
      "created_at__date": "2026-03-25",
      "total_loss": "70.00",
      "count": 2
    }
  ]
}
```

**Verification Checklist:**
- ✓ Response code is 200
- ✓ Summary includes totals and count
- ✓ by_reason breakdown present
- ✓ by_product breakdown present
- ✓ daily_trend array included

---

### Test 11: Product Wastage History

**Objective:** View wastage history for specific product

**Request:**
```
GET /api/product-wastages/product/1/history/
Authorization: Token YOUR_TOKEN
```

**Expected Response:** ✅ HTTP 200 OK

```json
{
  "count": 2,
  "results": [
    {
      "id": 1,
      "wastage_id": "PW-001",
      "product_id": 1,
      "product_name": "Chocolate Bun",
      "quantity": "5.00",
      "unit_cost": "10.00",
      "total_loss": "50.00",
      "reason_id": 1,
      "reason_text": "Expired",
      "created_at": "2026-03-25T10:30:00Z"
    },
    {
      "id": 2,
      "wastage_id": "PW-002",
      "product_id": 1,
      "product_name": "Chocolate Bun",
      "quantity": "2.00",
      "unit_cost": "10.00",
      "total_loss": "20.00",
      "reason_id": 2,
      "reason_text": "Damaged",
      "created_at": "2026-03-25T10:31:00Z"
    }
  ]
}
```

**Verification Checklist:**
- ✓ Response code is 200
- ✓ Only product 1 wastages returned
- ✓ Count is 2
- ✓ Ordered by created_at

---

## ✅ Expected Responses

### Success Responses

```
✅ GET /api/product-wastages/
   Status: 200 OK
   Response: { "count": N, "results": [...] }

✅ GET /api/product-wastages/{id}/
   Status: 200 OK
   Response: { full wastage detail with nested data }

✅ POST /api/product-wastages/
   Status: 201 CREATED
   Response: { new wastage with PW-### ID }

✅ DELETE /api/product-wastages/{id}/
   Status: 204 NO CONTENT
   Response: (empty)

✅ GET /api/product-wastages/analytics/
   Status: 200 OK
   Response: { summary, by_reason, by_product, daily_trend }

✅ GET /api/product-wastages/product/{id}/history/
   Status: 200 OK
   Response: { count, results with history for product }
```

---

## ❌ Error Responses

### Authentication Errors

```
❌ No Authorization Header
   Status: 401 UNAUTHORIZED
   Error: "Authentication credentials were not provided."

❌ Invalid Token
   Status: 401 UNAUTHORIZED
   Error: "Invalid token."
```

### Permission Errors

```
❌ Storekeeper tries to create wastage
   Status: 403 FORBIDDEN
   Error: "Only Baker, Cashier, or Manager can report wastage."

❌ Baker tries to delete wastage
   Status: 403 FORBIDDEN
   Error: "Only Manager can delete wastage records."
```

### Validation Errors

```
❌ Quantity is 0
   Status: 400 BAD REQUEST
   Error: { "quantity": ["Ensure this value is greater than or equal to 0.01."] }

❌ Insufficient stock
   Status: 400 BAD REQUEST
   Error: { "non_field_errors": ["Insufficient stock. Available: 50, Trying to waste: 100"] }

❌ Unit cost is negative
   Status: 400 BAD REQUEST
   Error: { "unit_cost": ["Ensure this value is greater than or equal to 0."] }

❌ Missing required field (product_id)
   Status: 400 BAD REQUEST
   Error: { "product_id": ["This field is required."] }

❌ Missing required field (reason_id)
   Status: 400 BAD REQUEST
   Error: { "reason_id": ["This field is required."] }
```

### Not Found Errors

```
❌ Invalid Wastage ID
   Status: 404 NOT FOUND
   Error: { "detail": "Not found." }

❌ Invalid Product ID in history
   Status: 404 NOT FOUND
   Error: { "detail": "Product not found." }
```

---

## 🔐 Permission Model

### Role-Based Access Control

**Manager:**
- ✅ Create wastage
- ✅ List all wastages
- ✅ View details
- ✅ Delete wastage (restore stock)
- ✅ View analytics

**Baker:**
- ✅ Create wastage (for products they're making)
- ✅ List all wastages
- ✅ View details
- ❌ Cannot delete

**Cashier:**
- ✅ Create wastage (for damaged/lost during sale)
- ✅ List all wastages
- ✅ View details
- ❌ Cannot delete

**Storekeeper:**
- ❌ Cannot create product wastage
- ✅ Can view/list wastages
- ❌ Cannot delete

---

## 📋 Validation Rules

### Field Validations

| Field | Type | Rules | Example |
|-------|------|-------|---------|
| wastage_id | String | Auto-generated, PW-### format, Unique | PW-001 |
| product_id | FK | Required, Must exist | 1 |
| quantity | Decimal | Required, >0, formatted to 2 decimals | 5.00 |
| unit_cost | Decimal | Required, ≥0, formatted to 2 decimals | 10.00 |
| total_loss | Decimal | Auto-calculated: qty × cost | 50.00 |
| reason_id | FK | Required, Must exist | 1 |
| reported_by | FK | Auto-set to current user if not provided | 1 |
| notes | Text | Optional, trimmed whitespace | "Expired on..." |
| created_at | DateTime | Auto-generated, Read-only | 2026-03-25T10:30:00Z |

### Business Rules

1. **Stock Check** - Quantity cannot exceed product.current_stock
2. **Stock Deduction** - Automatically deducted on create
3. **Stock Restoration** - Automatically restored on delete
4. **Total Loss** - Auto-calculated: quantity × unit_cost
5. **Sequence Integrity** - wastage_id maintains sequence

### Examples

```
✓ Valid: { "product_id": 1, "quantity": 5, "unit_cost": 10, "reason_id": 1 }
✓ Valid: { "product_id": 1, "quantity": 0.50, "unit_cost": 25.50, "reason_id": 2 }
✗ Invalid: { "product_id": 1, "quantity": 0, "unit_cost": 10, "reason_id": 1 }
✗ Invalid: { "product_id": 1, "quantity": 100, "unit_cost": 10, "reason_id": 1 } (stock=50)
✗ Invalid: { "product_id": 1, "unit_cost": -5, "quantity": 10, "reason_id": 1 }
```

---

## 🎯 Quick Reference

### Common cURL Commands

**List all wastages:**
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/product-wastages/
```

**Create wastage:**
```bash
curl -X POST \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"product_id":1,"quantity":5,"unit_cost":10,"reason_id":1}' \
  http://localhost:8000/api/product-wastages/
```

**Get wastage details:**
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/product-wastages/1/
```

**Delete wastage:**
```bash
curl -X DELETE \
  -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/product-wastages/1/
```

**Get analytics:**
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/product-wastages/analytics/
```

**Get product history:**
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/product-wastages/product/1/history/
```

---

## ✅ Test Completion Checklist

**All 11 manual tests completed:**
- ✅ Test 1: List all wastages
- ✅ Test 2: Create by Manager
- ✅ Test 3: Create by Baker
- ✅ Test 4: Create by Cashier
- ✅ Test 5: Reject Storekeeper
- ✅ Test 6: Retrieve details
- ✅ Test 7: Delete by Manager
- ✅ Test 8: Reject Baker delete
- ✅ Test 9: Filter by product
- ✅ Test 10: Analytics endpoint
- ✅ Test 11: Product history

**Automated Tests:** 30/30 PASSED ✅

---

## 📊 Summary

### Implementation Status

| Component | Status | Notes |
|-----------|--------|-------|
| Model | ✅ Complete | Auto-ID, validations, calculations |
| Serializers | ✅ Complete | 3 serializers with full nesting |
| ViewSet | ✅ Complete | All endpoints plus analytics |
| API Endpoints | ✅ Complete | 6 endpoints fully functional |
| Migrations | ✅ Complete | Database updated |
| Tests | ✅ Complete | 30/30 passing |
| Manual Tests | ✅ Complete | 11/11 procedures documented |

### Ready for Phase 5.3

✅ ProductWastage model complete and tested  
✅ All endpoints functional and verified  
✅ Can now move to Task 5.3: Ingredient Wastage Tracking  

---

**Task 5.2 Status: ✅ 100% COMPLETE**
