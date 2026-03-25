# Task 6.1: Stock History Models - Manual Testing Guide

**Status:** COMPLETE ✅  
**Date:** March 25, 2026  
**Implementation:** Stock History Models with Django Signals Auto-Logging

---

## 📋 Overview

This guide covers manual testing of the Stock History implementation, which tracks all inventory movements for both products and ingredients. The system automatically creates audit trail entries via Django signals when stock-affecting operations occur.

**Key Features Tested:**
- ProductStockHistory model and API endpoints
- IngredientStockHistory model and API endpoints
- Automatic creation via Django signals
- Stock history filtering and search
- Audit trail completeness

---

## 🔧 Prerequisites

**Required Setup:**
1. Django development server running: `python manage.py runserver`
2. Test database populated with:
   - At least 1 Manager user for authentication
   - At least 1 Product with stock
   - At least 1 Ingredient with batch
   - At least 1 Sale transaction
3. API client (Postman, curl, or similar)

**Authentication:**
```
POST /api/auth/login/
{
  "username": "manager_user",
  "password": "password123"
}

Response includes: "access" token (use in headers)
Header: Authorization: Bearer {access_token}
```

---

## 📊 Database Setup for Testing

### Create Test Data

**1. Create a Manager User (via Admin or API)**
```
POST /api/users/
{
  "username": "test_manager",
  "password": "testpass123",
  "email": "manager@test.com",
  "full_name": "Test Manager",
  "role": "Manager"
}
```

**2. Create a Category**
```
POST /api/categories/
{
  "name": "Test Category",
  "type": "Product",
  "description": "For testing"
}
Response: category_id = {id}
```

**3. Create a Product**
```
POST /api/products/
{
  "category_id": {category_id},
  "name": "Test Product",
  "cost_price": "10.00",
  "selling_price": "20.00",
  "current_stock": "100.00"
}
Response: product_id = {id}
```

**4. Create Ingredient Category**
```
POST /api/categories/
{
  "name": "Test Ingredient Category",
  "type": "Ingredient",
  "description": "For testing"
}
Response: ingredient_category_id = {id}
```

**5. Create an Ingredient**
```
POST /api/ingredients/
{
  "category_id": {ingredient_category_id},
  "name": "Test Ingredient",
  "supplier": "Test Supplier",
  "supplier_contact": "contact@test.com",
  "base_unit": "kg",
  "low_stock_threshold": "10.00"
}
Response: ingredient_id = {id}
```

**6. Create an Ingredient Batch**
```
POST /api/ingredient-batches/
{
  "ingredient_id": {ingredient_id},
  "quantity": "50.00",
  "cost_price": "5.00",
  "made_date": "2026-03-25",
  "expire_date": "2026-03-30"
}
Response: batch_id = {batch_id}
```

---

## 🧪 Test Cases

### Test Suite 1: Product Stock History Endpoints

#### Test 1.1: Retrieve Product Stock History
**Endpoint:** `GET /api/products/{product_id}/stock-history/`

**Description:** Retrieve all stock history records for a specific product

**Steps:**
1. Use product_id from earlier setup
2. Send GET request with Bearer token
3. Verify response structure

**Expected Response:**
```json
HTTP 200 OK
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "product_id": {product_id},
      "product_name": "Test Product",
      "transaction_type": "AddStock",
      "qty_before": "0.00",
      "qty_after": "100.00",
      "change_amount": "100.00",
      "performed_by": {user_id},
      "performed_by_name": "Test Manager",
      "reference_id": null,
      "notes": "Initial product creation",
      "created_at": "2026-03-25T10:00:00Z"
    }
  ]
}
```

**Success Criteria:**
- ✓ Status code is 200
- ✓ Contains stock history entries
- ✓ Transaction type is recorded
- ✓ qty_before and qty_after are accurate
- ✓ User information is included
- ✓ Timestamp is present

---

#### Test 1.2: Filter Product History by Transaction Type
**Endpoint:** `GET /api/products/{product_id}/stock-history/?transaction_type=UseStock`

**Description:** Filter product stock history by transaction type

**Steps:**
1. Create a sale to generate UseStock transaction
2. Query with transaction_type filter
3. Verify only matching transactions returned

**Expected Response:**
```json
HTTP 200 OK
{
  "count": 1,
  "results": [
    {
      "id": 2,
      "product_id": {product_id},
      "transaction_type": "UseStock",
      "qty_before": "100.00",
      "qty_after": "90.00",
      "change_amount": "-10.00",
      ...
    }
  ]
}
```

**Success Criteria:**
- ✓ Only UseStock transactions returned
- ✓ Filtering works correctly
- ✓ Count matches filtered results

---

#### Test 1.3: Date Range Filtering for Product History
**Endpoint:** `GET /api/products/{product_id}/stock-history/?created_after=2026-03-25`

**Description:** Filter product stock history by date range

**Steps:**
1. Query with date filters
2. Verify records within date range returned
3. Verify records outside date range excluded

**Expected Response:**
```json
HTTP 200 OK
{
  "count": 2,
  "results": [
    // Only records created on or after 2026-03-25
  ]
}
```

**Success Criteria:**
- ✓ Date filtering applied correctly
- ✓ Only matching date range returned
- ✓ Both created_after and created_before work

---

### Test Suite 2: Ingredient Stock History Endpoints

#### Test 2.1: Retrieve Ingredient Stock History
**Endpoint:** `GET /api/ingredients/{ingredient_id}/stock-history/`

**Description:** Retrieve all stock history records for a specific ingredient

**Steps:**
1. Use ingredient_id from earlier setup
2. Send GET request with Bearer token
3. Verify response contains batch creation entry

**Expected Response:**
```json
HTTP 200 OK
{
  "count": 1,
  "results": [
    {
      "id": 1,
      "ingredient_id": {ingredient_id},
      "ingredient_name": "Test Ingredient",
      "batch_id": {batch_id},
      "transaction_type": "AddStock",
      "qty_before": "0.00",
      "qty_after": "50.00",
      "change_amount": "50.00",
      "performed_by": {user_id},
      "performed_by_name": "Test Manager",
      "reference_id": {batch_id},
      "notes": null,
      "created_at": "2026-03-25T10:00:00Z"
    }
  ]
}
```

**Success Criteria:**
- ✓ Status code is 200
- ✓ Contains initial batch creation entry
- ✓ Transaction type is "AddStock"
- ✓ qty_after equals batch quantity (50.00)
- ✓ reference_id points to batch_id

---

#### Test 2.2: Filter Ingredient History by Transaction Type
**Endpoint:** `GET /api/ingredients/{ingredient_id}/stock-history/?transaction_type=AddStock`

**Description:** Filter ingredient stock history by transaction type

**Steps:**
1. Query with transaction_type=AddStock
2. Verify only AddStock entries returned
3. Create wastage and verify Wastage transactions available

**Expected Response:**
```json
HTTP 200 OK
{
  "count": 1,
  "results": [
    {
      "transaction_type": "AddStock",
      ...
    }
  ]
}
```

**Success Criteria:**
- ✓ Only AddStock transactions returned initially
- ✓ After creating wastage, Wastage type entries appear
- ✓ Filtering works correctly

---

#### Test 2.3: Ingredient History by Batch
**Endpoint:** `GET /api/ingredients/{ingredient_id}/stock-history/?batch_id={batch_id}`

**Description:** Retrieve stock history for specific ingredient batch

**Steps:**
1. Use batch_id from setup
2. Query with batch_id filter
3. Verify only records for that batch returned

**Expected Response:**
```json
HTTP 200 OK
{
  "count": 1,
  "results": [
    {
      "batch_id": {batch_id},
      "transaction_type": "AddStock",
      ...
    }
  ]
}
```

**Success Criteria:**
- ✓ Only related batch entries returned
- ✓ batch_id filter works correctly

---

### Test Suite 3: Stock History Search Endpoint

#### Test 3.1: Global Stock History Search
**Endpoint:** `GET /api/stock-history-search/?search_type=product&item_id={product_id}`

**Description:** Search and retrieve stock history records globally

**Steps:**
1. Send search request for product
2. Verify all transactions for product returned
3. Repeat for ingredient

**Expected Response:**
```json
HTTP 200 OK
{
  "count": 2,
  "results": [
    {
      "id": 1,
      "object_type": "product",
      "product_id": {product_id},
      "transaction_type": "AddStock",
      ...
    },
    {
      "id": 2,
      "object_type": "product",
      "product_id": {product_id},
      "transaction_type": "UseStock",
      ...
    }
  ]
}
```

**Success Criteria:**
- ✓ Status code is 200
- ✓ All transactions for item returned
- ✓ Object type correctly identified
- ✓ Multiple transactions returned in correct order

---

#### Test 3.2: Search by Transaction Type Globally
**Endpoint:** `GET /api/stock-history-search/?transaction_type=Wastage`

**Description:** Search all stock history records by transaction type

**Steps:**
1. Create some wastage records
2. Query with transaction_type=Wastage
3. Verify only wastage entries returned

**Expected Response:**
```json
HTTP 200 OK
{
  "count": 1,
  "results": [
    {
      "transaction_type": "Wastage",
      ...
    }
  ]
}
```

**Success Criteria:**
- ✓ Only Wastage type transactions returned
- ✓ Works for all transaction types

---

#### Test 3.3: Search by Date Range
**Endpoint:** `GET /api/stock-history-search/?created_after=2026-03-25&created_before=2026-03-26`

**Description:** Search stock history within date range

**Steps:**
1. Query with date range
2. Verify only records within range returned
3. Create records outside range and verify excluded

**Expected Response:**
```json
HTTP 200 OK
{
  "count": 2,
  "results": [
    // Only records created between dates
  ]
}
```

**Success Criteria:**
- ✓ Date range filtering works
- ✓ Records outside range excluded
- ✓ Boundaries correctly handled

---

### Test Suite 4: Signal-Based Automatic Entry Creation

#### Test 4.1: Auto-Create History on Product Batch Creation
**Endpoint:** `POST /api/product-batches/`

**Description:** Verify stock history entry created when product batch created

**Steps:**
1. Get initial stock history count for product
2. Create new product batch via API
3. Retrieve stock history again
4. Verify new AddStock entry created

**Request:**
```json
POST /api/product-batches/
{
  "product_id": {product_id},
  "quantity": "50.00",
  "made_date": "2026-03-25"
}
```

**Expected New History Entry:**
```json
{
  "product_id": {product_id},
  "transaction_type": "AddStock",
  "qty_before": "100.00",
  "qty_after": "150.00",
  "change_amount": "50.00",
  "performed_by": {user_id},
  "reference_id": {batch_id},
  "notes": "Product batch PROD-BATCH-1001 created"
}
```

**Success Criteria:**
- ✓ New history entry created automatically
- ✓ Transaction type is "AddStock"
- ✓ Change amount equals batch quantity
- ✓ qty_after is correct (qty_before + quantity)
- ✓ reference_id links to batch
- ✓ User is recorded correctly

---

#### Test 4.2: Auto-Create History on Sale Creation
**Endpoint:** `POST /api/sales/`

**Description:** Verify stock history entry created when sale created

**Steps:**
1. Get initial product stock
2. Create sale with product items
3. Retrieve product stock history
4. Verify UseStock entry created

**Request:**
```json
POST /api/sales/
{
  "cashier_id": {user_id},
  "payment_method": "Cash",
  "items": [
    {
      "product_id": {product_id},
      "quantity": "10.00",
      "unit_price": "20.00"
    }
  ]
}
```

**Expected New History Entry:**
```json
{
  "product_id": {product_id},
  "transaction_type": "UseStock",
  "qty_before": "150.00",
  "qty_after": "140.00",
  "change_amount": "-10.00",
  "performed_by": {user_id},
  "reference_id": {bill_number},
  "notes": "Sale BILL-1001 processed"
}
```

**Success Criteria:**
- ✓ New UseStock entry created automatically
- ✓ Change amount is negative (stock decrease)
- ✓ qty_after is correct (qty_before - quantity)
- ✓ reference_id is bill number
- ✓ Cashier recorded as performer

---

#### Test 4.3: Auto-Create History on Product Wastage
**Endpoint:** `POST /api/product-wastages/`

**Description:** Verify stock history entry created when product wastage reported

**Steps:**
1. Create wastage reason if not exists
2. Get initial product stock
3. Report product wastage
4. Verify Wastage history entry created

**Request:**
```json
POST /api/product-wastages/
{
  "product_id": {product_id},
  "quantity": "5.00",
  "unit_cost": "20.00",
  "reason_id": {reason_id},
  "notes": "Expired batch"
}
```

**Expected New History Entry:**
```json
{
  "product_id": {product_id},
  "transaction_type": "Wastage",
  "qty_before": "140.00",
  "qty_after": "135.00",
  "change_amount": "-5.00",
  "performed_by": {user_id},
  "reference_id": {wastage_id},
  "notes": "Product wastage PW-001 reported"
}
```

**Success Criteria:**
- ✓ New Wastage entry created automatically
- ✓ Transaction type is "Wastage"
- ✓ Change amount equals (quantity * -1)
- ✓ qty_after is correct
- ✓ reference_id is wastage_id

---

#### Test 4.4: Auto-Create History on Ingredient Batch Creation
**Endpoint:** `POST /api/ingredient-batches/`

**Description:** Verify stock history entry created when ingredient batch created

**Steps:**
1. Create new ingredient for testing
2. Get initial stock history count
3. Create ingredient batch
4. Verify AddStock entry created

**Request:**
```json
POST /api/ingredient-batches/
{
  "ingredient_id": {ingredient_id},
  "quantity": "75.00",
  "cost_price": "5.00",
  "made_date": "2026-03-25",
  "expire_date": "2026-04-30"
}
```

**Expected New History Entry:**
```json
{
  "ingredient_id": {ingredient_id},
  "transaction_type": "AddStock",
  "qty_before": "50.00",
  "qty_after": "125.00",
  "change_amount": "75.00",
  "performed_by": {user_id},
  "reference_id": {batch_id},
  "notes": "Ingredient batch BATCH-1002 created"
}
```

**Success Criteria:**
- ✓ New AddStock entry created automatically
- ✓ Change amount equals batch quantity
- ✓ qty_after is correct
- ✓ Batch relationship recorded in reference_id

---

#### Test 4.5: Auto-Create History on Ingredient Wastage
**Endpoint:** `POST /api/ingredient-wastages/`

**Description:** Verify stock history entry created when ingredient wastage reported

**Steps:**
1. Report ingredient wastage
2. Retrieve ingredient stock history
3. Verify Wastage entry created

**Request:**
```json
POST /api/ingredient-wastages/
{
  "ingredient_id": {ingredient_id},
  "quantity": "10.00",
  "unit_cost": "5.00",
  "reason_id": {reason_id},
  "batch_id": {batch_id},
  "notes": "Spoiled batch"
}
```

**Expected New History Entry:**
```json
{
  "ingredient_id": {ingredient_id},
  "transaction_type": "Wastage",
  "qty_before": "125.00",
  "qty_after": "115.00",
  "change_amount": "-10.00",
  "performed_by": {user_id},
  "reference_id": {wastage_id}
}
```

**Success Criteria:**
- ✓ New Wastage entry created automatically
- ✓ Change amount is negative
- ✓ qty_after is correct
- ✓ Batch information preserved in reference

---

### Test Suite 5: Pagination & Sorting

#### Test 5.1: Paginate Product Stock History
**Endpoint:** `GET /api/products/{product_id}/stock-history/?page=1&page_size=10`

**Description:** Verify pagination works on stock history

**Steps:**
1. Create multiple transactions
2. Query with pagination params
3. Verify correct page size and count

**Expected Response:**
```json
HTTP 200 OK
{
  "count": 25,
  "next": "http://api/products/1/stock-history/?page=2",
  "previous": null,
  "results": [
    // 10 results
  ]
}
```

**Success Criteria:**
- ✓ Page size respected
- ✓ Next/previous links correct
- ✓ Total count accurate
- ✓ Correct slice of results returned

---

#### Test 5.2: Sort Stock History by Date
**Endpoint:** `GET /api/products/{product_id}/stock-history/?ordering=-created_at`

**Description:** Verify sorting by timestamp works

**Steps:**
1. Query with ordering parameter
2. Verify results sorted newest to oldest
3. Test ascending order

**Expected Response:**
```json
HTTP 200 OK
{
  "results": [
    {
      "created_at": "2026-03-25T15:00:00Z",
      ...
    },
    {
      "created_at": "2026-03-25T10:00:00Z",
      ...
    }
  ]
}
```

**Success Criteria:**
- ✓ Results sorted correctly
- ✓ Newest to oldest (descending)
- ✓ Ascending order also works
- ✓ All results included in sort

---

### Test Suite 6: Permission & Authorization

#### Test 6.1: Unauthenticated Access Denied
**Endpoint:** `GET /api/products/{product_id}/stock-history/`

**Description:** Verify unauthenticated users cannot access stock history

**Steps:**
1. Send request WITHOUT Bearer token
2. Verify 401 error returned

**Expected Response:**
```json
HTTP 401 Unauthorized
{
  "detail": "Authentication credentials were not provided."
}
```

**Success Criteria:**
- ✓ Status code is 401
- ✓ Error message clear
- ✓ No data exposed

---

#### Test 6.2: Invalid Token Rejected
**Endpoint:** `GET /api/products/{product_id}/stock-history/`

**Description:** Verify invalid tokens are rejected

**Steps:**
1. Send request with invalid Bearer token
2. Verify 401 error returned

**Expected Response:**
```json
HTTP 401 Unauthorized
{
  "detail": "Invalid authentication credentials."
}
```

**Success Criteria:**
- ✓ Status code is 401
- ✓ Invalid token rejected
- ✓ No data accessed

---

#### Test 6.3: Valid Token Grants Access
**Endpoint:** `GET /api/products/{product_id}/stock-history/`

**Description:** Verify valid token grants access

**Steps:**
1. Send request with valid Bearer token
2. Verify 200 response and data returned

**Expected Response:**
```json
HTTP 200 OK
{
  "count": ...,
  "results": [...]
}
```

**Success Criteria:**
- ✓ Status code is 200
- ✓ Data returned
- ✓ User authenticated properly

---

### Test Suite 7: Error Handling

#### Test 7.1: Non-Existent Product ID
**Endpoint:** `GET /api/products/99999/stock-history/`

**Description:** Verify 404 error for non-existent product

**Steps:**
1. Use invalid product_id
2. Verify 404 response

**Expected Response:**
```json
HTTP 404 Not Found
{
  "detail": "Not found."
}
```

**Success Criteria:**
- ✓ Status code is 404
- ✓ Clear error message
- ✓ No data leakage

---

#### Test 7.2: Non-Existent Ingredient ID
**Endpoint:** `GET /api/ingredients/99999/stock-history/`

**Description:** Verify 404 error for non-existent ingredient

**Steps:**
1. Use invalid ingredient_id
2. Verify 404 response

**Expected Response:**
```json
HTTP 404 Not Found
{
  "detail": "Not found."
}
```

**Success Criteria:**
- ✓ Status code is 404
- ✓ Proper error handling

---

#### Test 7.3: Invalid Transaction Type Filter
**Endpoint:** `GET /api/products/{product_id}/stock-history/?transaction_type=InvalidType`

**Description:** Verify graceful handling of invalid filter values

**Steps:**
1. Use invalid transaction_type
2. Verify empty results (no error) or validation error

**Expected Response (Option 1 - Empty Results):**
```json
HTTP 200 OK
{
  "count": 0,
  "results": []
}
```

**Expected Response (Option 2 - Validation Error):**
```json
HTTP 400 Bad Request
{
  "transaction_type": ["Invalid transaction type"]
}
```

**Success Criteria:**
- ✓ Request handled gracefully
- ✓ No server error (500)
- ✓ Clear feedback to client

---

## 📝 Test Summary Checklist

Use this checklist to track completion of all test suites:

### Product Stock History Tests
- [ ] Test 1.1: Retrieve Product Stock History
- [ ] Test 1.2: Filter by Transaction Type
- [ ] Test 1.3: Date Range Filtering

### Ingredient Stock History Tests
- [ ] Test 2.1: Retrieve Ingredient Stock History
- [ ] Test 2.2: Filter by Transaction Type
- [ ] Test 2.3: History by Batch

### Search Endpoint Tests
- [ ] Test 3.1: Global Stock History Search
- [ ] Test 3.2: Search by Transaction Type
- [ ] Test 3.3: Search by Date Range

### Signal Auto-Creation Tests
- [ ] Test 4.1: Auto-create on Product Batch Creation
- [ ] Test 4.2: Auto-create on Sale Creation
- [ ] Test 4.3: Auto-create on Product Wastage
- [ ] Test 4.4: Auto-create on Ingredient Batch Creation
- [ ] Test 4.5: Auto-create on Ingredient Wastage

### Pagination & Sorting Tests
- [ ] Test 5.1: Paginate Stock History
- [ ] Test 5.2: Sort by Date

### Permission Tests
- [ ] Test 6.1: Unauthenticated Access Denied
- [ ] Test 6.2: Invalid Token Rejected
- [ ] Test 6.3: Valid Token Grants Access

### Error Handling Tests
- [ ] Test 7.1: Non-Existent Product ID
- [ ] Test 7.2: Non-Existent Ingredient ID
- [ ] Test 7.3: Invalid Filter Values

---

## 🔍 Key Points to Verify

**Data Integrity:**
- ✓ Stock quantities match actual product/ingredient stock
- ✓ Change amounts are calculated correctly
- ✓ Audit trails are complete and accurate
- ✓ No duplicate entries created

**Signal Handling:**
- ✓ Signals triggered for all stock-affecting operations
- ✓ History created automatically without manual entry
- ✓ Multiple operations all logged independently
- ✓ User information captured correctly

**API Usability:**
- ✓ Endpoints discoverable and documented
- ✓ Responses follow consistent format
- ✓ Error messages are helpful
- ✓ Filtering and search work intuitively

**Performance:**
- ✓ Queries execute quickly (< 500ms)
- ✓ Pagination works for large datasets
- ✓ No N+1 query problems
- ✓ Indexes on frequently queried fields

---

## 🚀 Post-Testing Steps

1. **Document Results:** Record test dates and outcomes
2. **Fix Issues:** Address any failing tests
3. **Run Automated Tests:** Execute `python manage.py test api.tests.test_stock_history`
4. **Update Status:** Mark Task 6.1 as COMPLETE in BACKEND_WORK_PLAN.md
5. **Integration:** Proceed to next phase tasks

---

## 📄 Related Files

- **Models:** [api/models.py](api/models.py)
- **Serializers:** [api/serializers.py](api/serializers.py)
- **ViewSets:** [api/views.py](api/views.py)
- **Signals:** [api/signals.py](api/signals.py)
- **Tests:** [api/tests/test_stock_history.py](api/tests/test_stock_history.py)
- **URLs:** [core/urls.py](core/urls.py)

---

**Testing Guide Version:** 1.0  
**Last Updated:** March 25, 2026
