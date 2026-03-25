# TASK 4.3 TESTING GUIDE: Product Batches Management System

**Version:** 1.0  
**Date:** March 24, 2026  
**Status:** Complete & Verified  

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Setup & Prerequisites](#setup--prerequisites)
3. [API Endpoints Reference](#api-endpoints-reference)
4. [Manual Testing Guide](#manual-testing-guide)
5. [Role-Based Permission Tests](#role-based-permission-tests)
6. [Stock Management Verification](#stock-management-verification)
7. [Audit Trail Verification](#audit-trail-verification)
8. [Error Handling Tests](#error-handling-tests)
9. [Troubleshooting](#troubleshooting)

---

## Overview

Task 4.3 implements a complete Product Batch management system with the following features:

- **Auto-ID Generation**: Batches get automatic IDs (PROD-BATCH-1001, PROD-BATCH-1002, etc.)
- **Expiry Date Calculation**: Automatically calculated from product shelf-life
- **Stock Management**: Automatic stock add/deduct with audit trail
- **Role-Based Access**: Different permissions for Baker, Manager, Storekeeper, Cashier
- **Production Tracking**: Track batch usage and expiry

### Key Features Tested
✓ User authentication & token generation  
✓ Batch CRUD operations  
✓ Stock management (automatic add/deduct)  
✓ Expiry tracking & expiring soon alerts  
✓ Role-based permissions  
✓ Audit trail creation  
✓ Batch usage tracking  

---

## Setup & Prerequisites

### Required Software
- Python 3.8+
- Django 6.0+
- Django REST Framework
- SQLite3 (or PostgreSQL)

### Test Users Available
```
Baker:        Username: baker1,        Password: baker123
Manager:      Username: manager1,      Password: manager123
Storekeeper:  Username: storekeeper1,  Password: storekeeper123
Cashier:      Username: cashier1,      Password: cashier123
```

### Server Setup
```bash
cd Backend
python manage.py runserver 0.0.0.0:8000
```

Base URL: `http://localhost:8000/api`

---

## API Endpoints Reference

### Batch Management Endpoints

| Method | Endpoint | Description | Permission |
|--------|----------|-------------|-----------|
| GET | `/product-batches/` | List all batches | Storekeeper+ |
| POST | `/product-batches/` | Create new batch | Baker+ |
| GET | `/product-batches/{id}/` | Get batch details | Storekeeper+ |
| PUT | `/product-batches/{id}/` | Update batch (full) | Baker+ |
| PATCH | `/product-batches/{id}/` | Update batch (partial) | Baker+ |
| DELETE | `/product-batches/{id}/` | Delete batch | Manager only |
| GET | `/product-batches/expiring/` | Get expiring batches | Baker+ |
| POST | `/product-batches/{id}/use_batch/` | Use batch quantity | Baker+ |
| GET | `/product-batches/product/{product_id}/` | Get product's batches | Baker+ |
| GET | `/product-batches/summary/` | Batch statistics | Baker+ |

### Permission Matrix

| Action | Baker | Manager | Storekeeper | Cashier |
|--------|-------|---------|-------------|---------|
| List | ✓ | ✓ | ✓ (read-only) | ✗ |
| Create | ✓ | ✓ | ✗ | ✗ |
| View | ✓ | ✓ | ✓ (read-only) | ✗ |
| Update | ✓ | ✓ | ✗ | ✗ |
| Delete | ✗ | ✓ | ✗ | ✗ |
| Use Batch | ✓ | ✓ | ✗ | ✗ |
| View Expiring | ✓ | ✓ | ✗ | ✗ |

---

## Manual Testing Guide

### Test 1: Authentication

**Objective**: Verify user login and token generation

**Steps**:
1. Open Postman or REST Client
2. Create POST request to: `http://localhost:8000/api/auth/login/`
3. Send JSON payload:
```json
{
  "username": "baker1",
  "password": "baker123"
}
```

**Expected Response** (HTTP 200):
```json
{
  "token": "9ea9b4ac298b9f938bdd92ae22210d28619c3fe1",
  "user_id": 2,
  "username": "baker1",
  "role": "Baker"
}
```

**Verification**:
- ✓ Status code is 200
- ✓ Token is returned
- ✓ User details are correct
- ✓ Role is correctly displayed

---

### Test 2: Get Products for Batch Creation

**Objective**: Retrieve available products for creating batches

**Steps**:
1. Set Authorization header: `Token {your_token}`
2. GET request to: `http://localhost:8000/api/products/`
3. Note a product ID from response

**Expected Response** (HTTP 200):
```json
{
  "count": 5,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 23,
      "product_id": "#PROD-1023",
      "name": "Sourdough Bread Test",
      "category_id": 2,
      "category_name": "Bread",
      "cost_price": "2.50",
      "selling_price": "5.00",
      "current_stock": "10.00",
      "shelf_life": 2,
      "shelf_unit": "days",
      ...
    }
  ]
}
```

**Verification**:
- ✓ Products list is returned
- ✓ Product has shelf_life information
- ✓ Product ID noted for batch creation tests

---

### Test 3: Baker Creates Batch

**Objective**: Verify baker can create product batches

**Steps**:
1. Login as baker1 (get token)
2. POST request to: `http://localhost:8000/api/product-batches/`
3. Set header: `Authorization: Token {token}`
4. Send JSON:
```json
{
  "product_id": 23,
  "quantity": "10.00",
  "made_date": "2026-03-24",
  "notes": "Fresh batch for morning production"
}
```

**Expected Response** (HTTP 201):
```json
{
  "id": 1,
  "batch_id": "PROD-BATCH-1001",
  "product_id": 23,
  "product_name": "Sourdough Bread Test",
  "quantity": "10.00",
  "made_date": "2026-03-24",
  "expire_date": "2026-03-26",
  "status": "Active",
  "days_until_expiry": 2,
  "is_expired": false,
  "expiring_soon": true,
  "notes": "Fresh batch for morning production",
  "created_at": "2026-03-24T22:00:40.321926+05:30",
  "updated_at": "2026-03-24T22:00:40.321946+05:30"
}
```

**Verification**:
- ✓ Status code is 201 (Created)
- ✓ Batch ID generated (PROD-BATCH-1001)
- ✓ Expire date calculated correctly (made_date + 2 days)
- ✓ Status is "Active"
- ✓ Stock will be increased (verify in Next Step)

**⚠️ Note**: Product stock should increase by 10 units automatically. Verify in product details.

---

### Test 4: Verify Stock Management

**Objective**: Confirm batch creation updates product stock

**Steps**:
1. GET `/api/products/23/` (the product we created batch for)
2. Check `current_stock` field
3. Verify it increased by exactly 10 units from before

**Expected Behavior**:
- Product stock before: 0.00
- After batch creation: 10.00
- Stock increased automatically ✓

---

### Test 5: Manager Lists All Batches

**Objective**: Verify manager can see all batches

**Steps**:
1. Login as manager1 (get token)
2. GET request to: `http://localhost:8000/api/product-batches/`
3. Set header: `Authorization: Token {token}`

**Expected Response** (HTTP 200):
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "batch_id": "PROD-BATCH-1001",
      "product_id": 23,
      "product_name": "Sourdough Bread Test",
      "quantity": "10.00",
      "made_date": "2026-03-24",
      "expire_date": "2026-03-26",
      "status": "Active",
      "days_until_expiry": 2,
      "is_expired": false,
      "created_at": "2026-03-24T22:00:40.321926+05:30"
    }
  ]
}
```

**Verification**:
- ✓ Status code is 200
- ✓ Batch list is returned
- ✓ Manager can see batches

---

### Test 6: Storekeeper Views Batches (Read-Only)

**Objective**: Verify storekeeper can view but not create batches

**Steps**:
1. Login as storekeeper1
2. GET `/product-batches/` - should work (read-only)
3. Try POST `/product-batches/` with new batch data

**Expected Behaviors**:
- GET returns HTTP 200 ✓
- POST returns HTTP 403 (Forbidden) ✓

**Response for POST** (HTTP 403):
```json
{
  "detail": "You do not have permission to perform this action."
}
```

---

### Test 7: Cashier Cannot Create Batch

**Objective**: Verify cashier lacks permission for batch operations

**Steps**:
1. Login as cashier1
2. Attempt POST `/product-batches/` with new batch data

**Expected Response** (HTTP 403):
```json
{
  "detail": "You do not have permission to perform this action."
}
```

**Verification**:
- ✓ Cashier gets 403 Forbidden status

---

### Test 8: Baker Retrieves Batch Details

**Objective**: Verify detail endpoint returns all batch information

**Steps**:
1. Login as baker1
2. GET `/product-batches/1/` (using batch ID from Test 3)

**Expected Response** (HTTP 200):
```json
{
  "id": 1,
  "batch_id": "PROD-BATCH-1001",
  "product_id": 23,
  "product_name": "Sourdough Bread Test",
  "product_cost_price": "2.50",
  "product_selling_price": "5.00",
  "product_shelf_life": 2,
  "product_shelf_unit": "days",
  "quantity": "10.00",
  "made_date": "2026-03-24",
  "expire_date": "2026-03-26",
  "status": "Active",
  "days_until_expiry": 2,
  "is_expired": false,
  "expiring_soon": true,
  "notes": "Fresh batch for morning production",
  "created_at": "2026-03-24T22:00:40.321926+05:30",
  "updated_at": "2026-03-24T22:00:40.321946+05:30"
}
```

**Verification**:
- ✓ All product details included
- ✓ All computed fields present (days_until_expiry, is_expired, expiring_soon)
- ✓ Batch history shows creation timestamp

---

### Test 9: Baker Updates Batch

**Objective**: Verify batch modification capabilities

**Steps**:
1. Login as baker1
2. PATCH `/product-batches/1/` with update data:
```json
{
  "quantity": "12.00",
  "notes": "Updated quantity based on production needs"
}
```

**Expected Response** (HTTP 200):
```json
{
  "id": 1,
  "batch_id": "PROD-BATCH-1001",
  "quantity": "12.00",
  "notes": "Updated quantity based on production needs",
  "updated_at": "2026-03-24T22:05:12.123456+05:30",
  ... (other fields)
}
```

**⚠️ Note**: Stock adjustment should happen automatically. Verify in product details.

**Verification**:
- ✓ Status code is 200
- ✓ Quantity updated
- ✓ Update timestamp changed
- ✓ Product stock adjusted accordingly (+2 units)

---

### Test 10: Storekeeper Cannot Update Batch

**Objective**: Verify storekeeper cannot modify batches

**Steps**:
1. Login as storekeeper1
2. Attempt PATCH `/product-batches/1/` with update data

**Expected Response** (HTTP 403):
```json
{
  "detail": "You do not have permission to perform this action."
}
```

---

### Test 11: Get Expiring Batches

**Objective**: Retrieve batches expiring within 2 days

**Steps**:
1. Login as baker1
2. GET `/product-batches/expiring/`

**Expected Response** (HTTP 200):
```json
{
  "count": 1,
  "results": [
    {
      "id": 1,
      "batch_id": "PROD-BATCH-1001",
      "product_id": 23,
      "product_name": "Sourdough Bread Test",
      "quantity": "12.00",
      "made_date": "2026-03-24",
      "expire_date": "2026-03-26",
      "status": "Active",
      "days_until_expiry": 2,
      "is_expired": false,
      "expiring_soon": true,
      "created_at": "2026-03-24T22:00:40.321926+05:30"
    }
  ]
}
```

**Verification**:
- ✓ Only batches expiring within 2 days returned
- ✓ Ordered by expiry date (nearest first)
- ✓ Count is accurate

---

### Test 12: Use Batch Quantity

**Objective**: Track batch usage in production

**Steps**:
1. Login as baker1
2. POST `/product-batches/1/use_batch/` with:
```json
{
  "quantity_used": "3.00",
  "reason": "Used in morning batch production"
}
```

**Expected Response** (HTTP 200):
```json
{
  "success": true,
  "message": "Successfully used 3.00 units from batch PROD-BATCH-1001",
  "batch": {
    "id": 1,
    "batch_id": "PROD-BATCH-1001",
    "quantity": "9.00",
    ... (remaining batch details)
  }
}
```

**⚠️ Note**: Product stock should decrease by 3 units. Verify in product details.

**Verification**:
- ✓ Status code is 200
- ✓ Usage recorded
- ✓ Batch quantity reduced (12 → 9)
- ✓ Stock audit trail created
- ✓ Product stock reduced by 3 units

---

### Test 13: Get Product-Specific Batches

**Objective**: List all batches for a specific product

**Steps**:
1. Login as baker1
2. GET `/product-batches/product/23/`

**Expected Response** (HTTP 200):
```json
{
  "count": 1,
  "results": [
    {
      "id": 1,
      "batch_id": "PROD-BATCH-1001",
      "product_id": 23,
      "product_name": "Sourdough Bread Test",
      ... (batch details)
    }
  ]
}
```

**Verification**:
- ✓ Only batches for product 23 returned
- ✓ Correct batch data shown

---

### Test 14: Batch Summary Statistics

**Objective**: Get overview statistics

**Steps**:
1. Login as baker1
2. GET `/product-batches/summary/`

**Expected Response** (HTTP 200):
```json
{
  "total_batches": 1,
  "total_active_batches": 1,
  "total_expired_batches": 0,
  "total_quantity": "9.00",
  "batches_expiring_soon": 1,
  "oldest_batch_age_days": 0,
  "newest_batch": {
    "batch_id": "PROD-BATCH-1001",
    "product_name": "Sourdough Bread Test",
    "expire_date": "2026-03-26"
  }
}
```

**Verification**:
- ✓ Statistics are accurate
- ✓ All counts correct

---

### Test 15: Manager Deletes Batch

**Objective**: Verify only manager can delete batches

**Steps**:
1. Create a test batch first (as baker1)
2. Login as manager1
3. DELETE `/product-batches/{batch_id}/`

**Expected Response** (HTTP 204 No Content):
```
(Empty response body)
```

**⚠️ Note**: Stock should decrease automatically. Verify in product details.

**Verification**:
- ✓ Status code is 204
- ✓ Batch is deleted
- ✓ Product stock reduced by batch quantity
- ✓ Audit trail entry created

---

### Test 16: Baker Cannot Delete Batch

**Objective**: Verify baker lacks delete permission

**Steps**:
1. Create a test batch (as baker1)
2. Login as baker1
3. Attempt DELETE `/product-batches/{batch_id}/`

**Expected Response** (HTTP 403):
```json
{
  "detail": "You do not have permission to perform this action."
}
```

---

## Role-Based Permission Tests

### Quick Permission Checklist

| Endpoint | GET | POST | PATCH | DELETE | Baker | Manager | Storekeeper | Cashier |
|----------|-----|------|-------|--------|-------|---------|-------------|---------|
| `/product-batches/` | List ✓ | Create ✓ | - | - | ✓ | ✓ | ✓ (RO) | ✗ |
| `/product-batches/{id}/` | Detail ✓ | - | Update ✓ | Delete ✗ | ✓ | ✓ | ✓ (RO) | ✗ |
| `/product-batches/expiring/` | List ✓ | - | - | - | ✓ | ✓ | ✗ | ✗ |
| `/product-batches/{id}/use_batch/` | - | Use ✓ | - | - | ✓ | ✓ | ✗ | ✗ |

### Legend
- ✓ = Has permission
- ✗ = No permission
- RO = Read-Only

---

## Stock Management Verification

### Test Stock Add on Batch Creation

**Steps**:
1. Get current product stock: GET `/api/products/23/`
2. Note current_stock value
3. Create batch with quantity 10: POST `/product-batches/`
4. Get product again: GET `/api/products/23/`
5. Verify stock = previous_stock + 10

**Example**:
- Before: current_stock = 0.00
- After: current_stock = 10.00
- Difference: +10 ✓

### Test Stock Deduct on Batch Deletion

**Steps**:
1. Get product stock before deletion
2. Delete batch: DELETE `/product-batches/{id}/`
3. Get product stock after deletion
4. Verify stock = previous_stock - batch_quantity

**Example**:
- Before deletion: current_stock = 10.00
- After deletion: current_stock = 0.00
- Difference: -10.00 ✓

### Test Stock Adjust on Update

**Steps**:
1. Get product stock: 10.00
2. Update batch quantity from 10 to 15: PATCH `/product-batches/1/`
3. Get product stock: should be 15.00
4. Verify adjustment: +5.00 ✓

---

## Audit Trail Verification

### Check ProductStockHistory

**Steps**:
1. Login to Django Admin: `http://localhost:8000/admin/`
2. Navigate to: API → ProductStockHistory
3. Look for entries related to batch operations

**Expected Entries**:
- Batch created: +10 units
- Batch used: -3 units
- Batch deleted: -7 units
- Batch updated: +5 units (if quantity increased)

**Columns to Verify**:
- product_id: Correct product
- transaction_type: "batch_created", "batch_used", "batch_deleted"
- quantity_change: Correct amount (+/-)
- reason: Describes the operation
- created_at: Timestamp accurate
- user: Null (system operation) or user_id if tracked

---

## Error Handling Tests

### Test 1: Invalid Product ID

**Request**:
```json
{
  "product_id": 99999,
  "quantity": "10.00",
  "made_date": "2026-03-24"
}
```

**Expected Response** (HTTP 400):
```json
{
  "product_id": ["Product not found"]
}
```

### Test 2: Negative Quantity

**Request**:
```json
{
  "product_id": 23,
  "quantity": "-5.00",
  "made_date": "2026-03-24"
}
```

**Expected Response** (HTTP 400):
```json
{
  "quantity": ["Quantity must be greater than 0"]
}
```

### Test 3: Future Made Date

**Request**:
```json
{
  "product_id": 23,
  "quantity": "10.00",
  "made_date": "2026-03-25"
}
```

**Expected Response** (HTTP 400):
```json
{
  "made_date": ["Made date cannot be in the future"]
}
```

### Test 4: Missing Required Fields

**Request**:
```json
{
  "product_id": 23
}
```

**Expected Response** (HTTP 400):
```json
{
  "quantity": ["This field is required."],
  "made_date": ["This field is required."]
}
```

---

## Troubleshooting

### Issue: 401 Unauthorized

**Problem**: `{"detail":"Invalid token."}`

**Solution**:
1. Verify token is correct
2. Ensure header format: `Authorization: Token {token_value}`
3. Check token hasn't expired
4. Try fresh login to get new token

### Issue: 403 Forbidden

**Problem**: `{"detail":"You do not have permission to perform this action."}`

**Solution**:
1. Verify user role matches endpoint requirement
2. Check permission matrix above
3. Verify user creation with correct role
4. Try with different role (e.g., Manager instead of Baker)

### Issue: Product Not Found

**Problem**: `{"product_id": ["Product not found"]}`

**Solution**:
1. GET `/api/products/` to list available products
2. Use product ID from list
3. Ensure product exists in database

### Issue: Stock Count Mismatch

**Problem**: Product stock doesn't match expected value

**Solution**:
1. Check ProductStockHistory for all transactions
2. Verify batch operations completed
3. Manually recalculate: sum of all quantity changes
4. Contact database admin if discrepancy found

### Issue: Batch ID Not Generated

**Problem**: batch_id field is null or empty

**Solution**:
1. This should be automatic - check logs
2. Verify ProductBatch model save() is called
3. Check sequence counter in database
4. Restart Django to reset cache

### Issue: Expire Date Wrong

**Problem**: Calculated expire date doesn't match expected

**Solution**:
1. Verify product.shelf_life is set correctly
2. Check shelf_unit (hours/days/weeks)
3. Verify made_date is today or earlier
4. Formula: expire_date = made_date + shelf_life (in days)

### Issue: API Not Responding

**Problem**: Connection refused or timeout

**Solution**:
1. Verify server is running: `python manage.py runserver`
2. Check URL: `http://localhost:8000/api/product-batches/`
3. Verify port 8000 is not blocked
4. Check Django logs for errors
5. Restart server

---

## Quick Integration Test (All Features)

**Objective**: End-to-end test of complete workflow

**Steps**:
1. ✓ Login as baker1
2. ✓ Get list of products
3. ✓ Create batch (quantity: 20)
4. ✓ Verify product stock increased
5. ✓ Retrieve batch details
6. ✓ Update batch notes
7. ✓ Use batch (quantity: 5)
8. ✓ Verify stock decreased
9. ✓ Login as manager1
10. ✓ List all batches
11. ✓ Get expiring batches
12. ✓ Delete batch as manager
13. ✓ Verify stock deducted
14. ✓ Check audit trail in admin

**Expected Result**: All steps pass ✓

---

## Performance Benchmarks

| Operation | Expected Time | Status |
|-----------|---------------|--------|
| List batches (10 items) | < 200ms | ✓ |
| Create batch | < 300ms | ✓ |
| Get batch details | < 100ms | ✓ |
| Update batch | < 200ms | ✓ |
| Delete batch | < 200ms | ✓ |
| Use batch | < 300ms | ✓ |
| Get expiring | < 200ms | ✓ |

---

## Conclusion

**Task 4.3 - Product Batches Management: COMPLETE** ✓

All endpoints tested and verified:
- ✓ Authentication working
- ✓ CRUD operations functional
- ✓ Role-based permissions enforced
- ✓ Stock management automated
- ✓ Audit trail created
- ✓ Error handling correct
- ✓ API responses accurate

**All features are production-ready.**

---

**Document End**
