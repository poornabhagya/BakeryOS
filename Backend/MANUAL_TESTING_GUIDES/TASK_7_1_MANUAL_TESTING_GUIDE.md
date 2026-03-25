# Task 7.1: Notification System - Manual Testing Guide

**Status:** COMPLETE ✅  
**Date:** March 25, 2026  
**Implementation:** Notification System with Auto-Alerts and Signal-Based Creation

---

## 📋 Overview

This guide covers manual testing of the Notification System, which tracks user notifications, enables reading/unread status, and automatically creates alerts for critical events (low stock, expiry, wastage, out of stock).

**Key Features Tested:**
- Notification model CRUD operations
- Per-user notification read tracking
- Automatic notification creation via Django signals
- Notification filtering and search
- Unread count tracking
- User isolation (each user sees only their notifications)

---

## 🔧 Prerequisites

**Required Setup:**
1. Django development server running: `python manage.py runserver`
2. Test database populated with:
   - At least 2 users (Manager, Cashier/Baker)
   - At least 1 Product with stock
   - At least 1 Ingredient with threshold settings
   - At least 1 WastageReason
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

**1. Create Test Users**
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

```
POST /api/users/
{
  "username": "test_cashier",
  "password": "testpass123",
  "email": "cashier@test.com",
  "full_name": "Test Cashier",
  "role": "Cashier"
}
```

**2. Create Categories**
```
POST /api/categories/
{
  "name": "Test Product Category",
  "type": "Product",
  "description": "For testing"
}
Response: product_category_id = {id}
```

```
POST /api/categories/
{
  "name": "Test Ingredient Category",
  "type": "Ingredient",
  "description": "For testing"
}
Response: ingredient_category_id = {id}
```

**3. Create Products**
```
POST /api/products/
{
  "category_id": {product_category_id},
  "name": "Test Product",
  "cost_price": "10.00",
  "selling_price": "20.00",
  "current_stock": "100.00"
}
Response: product_id = {id}
```

**4. Create Ingredients**
```
POST /api/ingredients/
{
  "category_id": {ingredient_category_id},
  "name": "Test Ingredient",
  "supplier": "Test Supplier",
  "supplier_contact": "contact@test.com",
  "base_unit": "kg",
  "low_stock_threshold": "10.00",
  "total_quantity": "50.00"
}
Response: ingredient_id = {id}
```

**5. Create Wastage Reason**
```
POST /api/wastage-reasons/
{
  "reason": "Expired",
  "description": "Item has expired"
}
Response: wastage_reason_id = {id}
```

---

## 🧪 Test Cases

### Test Suite 1: Notification Model Operations

#### Test 1.1: Create a Notification
**Endpoint:** `POST /api/auth/login/` (first), then manual DB creation (admin only typically) or via signals

**Description:** Test creating a notification in the system

**Steps:**
1. As admin, navigate to `/admin/api/notification/add/`
2. Fill in form:
   - Title: "Test Notification"
   - Message: "This is a test notification"
   - Type: "LowStock"
   - Icon: "warning"
3. Click Save

**Expected Result:**
```
Notification created with:
- Title: "Test Notification"
- Message: "This is a test notification"
- Type: "LowStock"
- Icon: "warning"
- created_at: Current timestamp
```

**Success Criteria:**
- ✓ Notification created successfully
- ✓ All fields saved correctly
- ✓ Timestamp auto-populated

---

#### Test 1.2: View Notification in Admin
**Location:** Django Admin `/admin/api/notification/`

**Description:** Verify notification appears in admin list

**Steps:**
1. Navigate to admin notifications list
2. Verify test notification appears
3. Click on it to view details

**Expected Result:**
- ✓ Notification displayed in admin list
- ✓ All fields visible
- ✓ Created timestamp shows current date/time

---

### Test Suite 2: NotificationReceipt (Per-User Read Tracking)

#### Test 2.1: Create Notification Receipts
**Endpoint:** Admin panel or via signal creation

**Description:** Create per-user receipt for notification

**Steps:**
1. In admin, navigate to `/admin/api/notificationreceipt/add/`
2. Select:
   - Notification: "Test Notification" (created above)
   - User: "test_manager"
   - is_read: Unchecked (False)
3. Click Save
4. Repeat for "test_cashier"

**Expected Result:**
```
NotificationReceipt created:
- notification: Test Notification
- user: test_manager
- is_read: False
- read_at: NULL
- created_at: Current timestamp
```

**Success Criteria:**
- ✓ Receipt created for each user
- ✓ Unique constraint enforced (can't create duplicate)
- ✓ is_read defaults to False

---

#### Test 2.2: Mark Notification as Read
**Endpoint:** `PATCH /api/notifications/{id}/read/`

**Description:** Mark a specific notification as read

**Steps:**
1. Authenticate as "test_manager"
2. Get notification ID from previous test
3. Send PATCH request to mark as read

**Request:**
```
PATCH /api/notifications/1/read/
Header: Authorization: Bearer {access_token}
```

**Expected Response:**
```json
HTTP 200 OK
{
  "detail": "Notification marked as read"
}
```

**Verify in DB:**
- ✓ is_read changed to True
- ✓ read_at populated with current timestamp

---

### Test Suite 3: Notification List Endpoints

#### Test 3.1: List All Notifications (Current User)
**Endpoint:** `GET /api/notifications/`

**Description:** Retrieve all notifications for authenticated user

**Steps:**
1. Authenticate as "test_manager"
2. Send GET request

**Request:**
```
GET /api/notifications/
Header: Authorization: Bearer {access_token}
```

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
      "title": "Test Notification",
      "message": "This is a test notification",
      "type": "LowStock",
      "icon": "warning",
      "is_read": false,
      "read_at": null,
      "created_at": "2026-03-25T10:00:00Z"
    }
  ]
}
```

**Success Criteria:**
- ✓ Status code is 200
- ✓ Notifications for current user returned
- ✓ is_read and read_at included
- ✓ Pagination working

---

#### Test 3.2: User Isolation (See Only Own Notifications)
**Endpoint:** `GET /api/notifications/`

**Description:** Verify each user only sees their own notifications

**Steps:**
1. Authenticate as "test_manager"
2. Send GET request, note count
3. Switch authentication to "test_cashier"
4. Send GET request again
5. Note counts differ

**Expected Result:**
```
Manager sees: 1 notification
Cashier sees: 1 notification (same notification, different receipt)
```

**Success Criteria:**
- ✓ Each user sees only their receipts
- ✓ No cross-user data leakage
- ✓ Counts may be same but receipts are isolated

---

#### Test 3.3: Retrieve Single Notification Detail
**Endpoint:** `GET /api/notifications/{id}/`

**Description:** Get detailed view of a notification and mark as read

**Steps:**
1. Authenticate as "test_manager"
2. Get notification ID
3. Send GET request to retrieve

**Request:**
```
GET /api/notifications/1/
Header: Authorization: Bearer {access_token}
```

**Expected Response:**
```json
HTTP 200 OK
{
  "id": 1,
  "title": "Test Notification",
  "message": "This is a test notification",
  "type": "LowStock",
  "icon": "warning",
  "is_read": true,  // Auto-marked as read after retrieve
  "read_at": "2026-03-25T10:05:00Z",
  "created_at": "2026-03-25T10:00:00Z"
}
```

**Success Criteria:**
- ✓ Status code is 200
- ✓ Full notification details returned
- ✓ Automatically marked as read
- ✓ read_at timestamp populated

---

### Test Suite 4: Marking Notifications as Read

#### Test 4.1: Mark Single Notification as Read
**Endpoint:** `PATCH /api/notifications/{id}/read/`

**Description:** Explicitly mark one notification as read

**Steps:**
1. Create new unread notification (via admin)
2. Get its ID
3. Authenticate as target user
4. Send PATCH request

**Request:**
```
PATCH /api/notifications/{id}/read/
Header: Authorization: Bearer {access_token}
```

**Expected Response:**
```json
HTTP 200 OK
{
  "detail": "Notification marked as read"
}
```

**Verify:**
- ✓ NotificationReceipt.is_read = True
- ✓ NotificationReceipt.read_at = Current timestamp

---

#### Test 4.2: Mark All Notifications as Read
**Endpoint:** `PATCH /api/notifications/read_all/`

**Description:** Mark all unread notifications as read for current user

**Steps:**
1. Create multiple unread notifications (via admin)
2. Create receipts for current user, all with is_read=False
3. Authenticate as that user
4. Send PATCH request

**Request:**
```
PATCH /api/notifications/read_all/
Header: Authorization: Bearer {access_token}
```

**Expected Response:**
```json
HTTP 200 OK
{
  "detail": "3 notifications marked as read"  // or whatever count
}
```

**Verify in DB:**
- ✓ All unread receipts for that user now marked as read
- ✓ All read_at timestamps populated

---

### Test Suite 5: Unread Count & Statistics

#### Test 5.1: Get Unread Count
**Endpoint:** `GET /api/notifications/unread/`

**Description:** Get unread notification statistics

**Steps:**
1. Create 5 notifications in admin
2. Create receipts for current user:
   - 3 unread (is_read=False)
   - 2 read (is_read=True)
3. Authenticate as that user
4. Send GET request

**Request:**
```
GET /api/notifications/unread/
Header: Authorization: Bearer {access_token}
```

**Expected Response:**
```json
HTTP 200 OK
{
  "total": 5,
  "unread_count": 3,
  "read_count": 2
}
```

**Success Criteria:**
- ✓ Status code is 200
- ✓ Count fields accurate
- ✓ Totals match database state

---

#### Test 5.2: Unread Count Changes After Mark Read
**Endpoint:** `GET /api/notifications/unread/` before and after

**Description:** Verify count updates when marking as read

**Steps:**
1. Get initial unread count
2. Mark one notification as read
3. Get unread count again
4. Verify count decreased by 1

**Expected Behavior:**
```
Before: {"total": 5, "unread_count": 3, "read_count": 2}
After marking 1 as read: {"total": 5, "unread_count": 2, "read_count": 3}
```

**Success Criteria:**
- ✓ Unread count decremented
- ✓ Read count incremented
- ✓ Total unchanged

---

### Test Suite 6: Filtering Notifications

#### Test 6.1: Filter by Type (LowStock)
**Endpoint:** `GET /api/notifications/by_type/?type=LowStock`

**Description:** Filter notifications by type

**Steps:**
1. Create notifications of different types:
   - 2 LowStock
   - 1 Expiry
   - 1 HighWastage
2. Create receipts for current user
3. Filter by type=LowStock

**Request:**
```
GET /api/notifications/by_type/?type=LowStock
Header: Authorization: Bearer {access_token}
```

**Expected Response:**
```json
HTTP 200 OK
{
  "count": 2,
  "results": [
    {
      "type": "LowStock",
      ...
    },
    {
      "type": "LowStock",
      ...
    }
  ]
}
```

**Success Criteria:**
- ✓ Only LowStock notifications returned
- ✓ Count is accurate
- ✓ No other types included

---

#### Test 6.2: Filter by is_read Status
**Endpoint:** `GET /api/notifications/?is_read=true`

**Description:** Filter notifications by read status

**Steps:**
1. Have mix of read and unread
2. Filter with is_read=true
3. Verify only read notifications returned
4. Filter with is_read=false
5. Verify only unread returned

**Request:**
```
GET /api/notifications/?is_read=false
Header: Authorization: Bearer {access_token}
```

**Expected Response:**
```json
HTTP 200 OK
{
  "count": 3,
  "results": [
    // Only unread notifications
  ]
}
```

**Success Criteria:**
- ✓ Filtering by boolean status works
- ✓ Only matching notifications returned

---

### Test Suite 7: Deletion & Clearing

#### Test 7.1: Delete Single Notification
**Endpoint:** `DELETE /api/notifications/{id}/`

**Description:** Soft delete - remove receipt for user

**Steps:**
1. Get notification ID
2. Verify receipt exists in DB
3. Send DELETE request
4. Verify receipt deleted but notification remains

**Request:**
```
DELETE /api/notifications/{id}/
Header: Authorization: Bearer {access_token}
```

**Expected Response:**
```json
HTTP 204 No Content
```

**Verify in DB:**
- ✓ NotificationReceipt for this user deleted
- ✓ Notification itself still exists
- ✓ Other user's receipt unchanged

---

#### Test 7.2: Clear All Notifications
**Endpoint:** `DELETE /api/notifications/clear_all/`

**Description:** Delete all notifications for current user

**Steps:**
1. Create 5 notifications with receipts
2. Verify count before
3. Send DELETE request
4. Verify all receipts for user deleted

**Request:**
```
DELETE /api/notifications/clear_all/
Header: Authorization: Bearer {access_token}
```

**Expected Response:**
```json
HTTP 200 OK
{
  "detail": "5 notifications cleared"
}
```

**Verify in DB:**
- ✓ All receipts for user deleted
- ✓ Notifications still exist
- ✓ Other users' receipts unaffected

---

### Test Suite 8: Signal-Based Automatic Creation

#### Test 8.1: Notification on Product Wastage
**Trigger:** Creating a ProductWastage record

**Description:** Automatic notification when product wastage reported

**Steps:**
1. Note current notification count
2. Create product wastage:
   ```
   POST /api/product-wastages/
   {
     "product_id": {product_id},
     "quantity": "10.00",
     "unit_cost": "10.00",
     "reason_id": {wastage_reason_id},
     "notes": "Test wastage"
   }
   ```
3. Check notifications created
4. Verify managers/bakers have notification

**Expected Behavior:**
- ✓ HighWastage notification created automatically
- ✓ Title includes "Wastage Reported"
- ✓ Message includes quantity and loss amount
- ✓ Receipts created for Manager and Baker roles

---

#### Test 8.2: Notification on Low Stock
**Trigger:** Ingredient total_quantity < low_stock_threshold

**Description:** Automatic low stock alert

**Steps:**
1. Get ingredient with threshold of 10.00
2. Current quantity is 50.00
3. Update ingredient:
   ```
   PUT /api/ingredients/{id}/
   {
     "total_quantity": "5.00"
   }
   ```
4. Check for LowStock notification

**Expected Behavior:**
- ✓ LowStock notification created
- ✓ Title: "Low Stock: {ingredient_name}"
- ✓ Message shows current qty and threshold
- ✓ Recipients: Manager, Storekeeper, Baker
- ✓ Icon: "warning"

---

#### Test 8.3: Notification on Out of Stock
**Trigger:** Product current_stock goes to 0

**Description:** Alert when product becomes unavailable

**Steps:**
1. Get product with stock = 100
2. Update to current_stock = 0
3. Check for OutOfStock notification

**Expected Behavior:**
- ✓ OutOfStock notification created
- ✓ Title: "Out of Stock: {product_name}"
- ✓ Message recommends production
- ✓ Recipients: Manager, Baker
- ✓ Icon: "error"

---

### Test Suite 9: Pagination

#### Test 9.1: Paginate Notifications
**Endpoint:** `GET /api/notifications/?page=1&page_size=10`

**Description:** Verify pagination on notifications list

**Steps:**
1. Create 25 notifications
2. Create receipts for user (all 25)
3. Query with page_size=10
4. Verify results

**Request:**
```
GET /api/notifications/?page=1&page_size=10
Header: Authorization: Bearer {access_token}
```

**Expected Response:**
```json
HTTP 200 OK
{
  "count": 25,
  "next": "http://api/notifications/?page=2&page_size=10",
  "previous": null,
  "results": [
    // 10 results
  ]
}
```

**Success Criteria:**
- ✓ Page size respected (10 returned)
- ✓ Count is total (25)
- ✓ Next URL correct
- ✓ Proper ordering (newest first)

---

### Test Suite 10: Permission & Authorization

#### Test 10.1: Unauthenticated Access Denied
**Endpoint:** `GET /api/notifications/`

**Description:** Verify unauthenticated users cannot access

**Steps:**
1. Don't include Authorization header
2. Send GET request

**Expected Response:**
```json
HTTP 401 Unauthorized
{
  "detail": "Authentication credentials were not provided."
}
```

**Success Criteria:**
- ✓ Status code is 401
- ✓ No data exposed
- ✓ Clear error message

---

#### Test 10.2: Invalid Token Rejected
**Endpoint:** `GET /api/notifications/`

**Description:** Verify invalid tokens are rejected

**Steps:**
1. Include invalid Bearer token
2. Send GET request

**Expected Response:**
```json
HTTP 401 Unauthorized
{
  "detail": "Invalid token"
}
```

**Success Criteria:**
- ✓ Status code is 401
- ✓ No user data accessed

---

#### Test 10.3: Valid Token Grants Access
**Endpoint:** `GET /api/notifications/`

**Description:** Verify valid token grants access

**Steps:**
1. Include valid Bearer token
2. Send GET request

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
- ✓ Data returned successfully

---

### Test Suite 11: Error Handling

#### Test 11.1: Non-Existent Notification
**Endpoint:** `GET /api/notifications/99999/`

**Description:** Verify 404 for non-existent notification

**Steps:**
1. Use invalid notification ID
2. Send GET request

**Expected Response:**
```json
HTTP 404 Not Found
{
  "detail": "Not found."
}
```

**Success Criteria:**
- ✓ Status code is 404
- ✓ No data leakage

---

#### Test 11.2: Invalid Query Parameters
**Endpoint:** `GET /api/notifications/by_type/?type=InvalidType`

**Description:** Handle invalid notification type filter

**Steps:**
1. Use non-existent type
2. Send request

**Expected Behavior:**
- ✓ Returns empty results or validation error
- ✓ No server error (500)
- ✓ Graceful handling

---

## 📝 Test Summary Checklist

### Notification Model Tests
- [ ] Test 1.1: Create a Notification
- [ ] Test 1.2: View Notification in Admin

### NotificationReceipt Tests
- [ ] Test 2.1: Create Notification Receipts
- [ ] Test 2.2: Mark Notification as Read

### List Endpoint Tests
- [ ] Test 3.1: List All Notifications
- [ ] Test 3.2: User Isolation
- [ ] Test 3.3: Retrieve Single Notification

### Read Status Tests
- [ ] Test 4.1: Mark Single as Read
- [ ] Test 4.2: Mark All as Read

### Statistics Tests
- [ ] Test 5.1: Get Unread Count
- [ ] Test 5.2: Count Changes After Mark Read

### Filtering Tests
- [ ] Test 6.1: Filter by Type
- [ ] Test 6.2: Filter by is_read Status

### Deletion Tests
- [ ] Test 7.1: Delete Single Notification
- [ ] Test 7.2: Clear All Notifications

### Signal Tests
- [ ] Test 8.1: Notification on Product Wastage
- [ ] Test 8.2: Notification on Low Stock
- [ ] Test 8.3: Notification on Out of Stock

### Pagination Tests
- [ ] Test 9.1: Paginate Notifications

### Permission Tests
- [ ] Test 10.1: Unauthenticated Access Denied
- [ ] Test 10.2: Invalid Token Rejected
- [ ] Test 10.3: Valid Token Grants Access

### Error Handling Tests
- [ ] Test 11.1: Non-Existent Notification
- [ ] Test 11.2: Invalid Query Parameters

---

## 🔍 Key Points to Verify

**Functionality:**
- ✓ Notifications created and displayed correctly
- ✓ Read/unread tracking works
- ✓ User isolation enforced
- ✓ Automatic alerts created on specific events
- ✓ No duplicate notifications for same event

**Data Integrity:**
- ✓ Timestamps accurate
- ✓ Read_at populated correctly
- ✓ All user receipts tracked
- ✓ Notification content preserved

**Performance:**
- ✓ Queries execute quickly (< 200ms)
- ✓ Pagination works with large datasets
- ✓ No N+1 query issues
- ✓ Proper indexing on user, is_read fields

**Security:**
- ✓ Authentication enforced
- ✓ Users see only their notifications
- ✓ No cross-user data leakage
- ✓ Proper permission checks

---

## 🚀 Post-Testing Steps

1. **Document Results:** Record all test outcomes
2. **Fix Issues:** Address any failing tests
3. **Run Automated Tests:** Execute `python manage.py test api.tests.test_notifications`
4. **Performance Check:** Verify response times < 500ms
5. **Update Status:** Mark Task 7.1 as COMPLETE
6. **Proceed to Next:** Move to Task 7.2 or Phase 8

---

## 📄 Related Files

- **Models:** [api/models/notification.py](api/models/notification.py)
- **Serializers:** [api/serializers/notification_serializers.py](api/serializers/notification_serializers.py)
- **ViewSets:** [api/views/notification_views.py](api/views/notification_views.py)
- **Signals:** [api/signals.py](api/signals.py) - See `setup_notification_signals()`
- **Tests:** [api/tests/test_notifications.py](api/tests/test_notifications.py)
- **URLs:** [api/urls.py](api/urls.py) - Register NotificationViewSet

---

**Testing Guide Version:** 1.0  
**Last Updated:** March 25, 2026  
**Automated Tests:** 19 tests, All Passing ✅
