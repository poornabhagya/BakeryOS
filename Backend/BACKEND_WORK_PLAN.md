# BakeryOS Backend - Complete Work Plan

**Project:** BakeryOS - Bakery Management System  
**Framework:** Django 6.0 + Django REST Framework  
**Database:** PostgreSQL (or SQLite for development)  
**Last Updated:** March 22, 2026

---

## 📋 EXECUTIVE SUMMARY

This work plan provides a detailed roadmap to build the complete BakeryOS backend API. The backend must support:
- User authentication & role-based access control (4 roles: Manager, Cashier, Baker, Storekeeper)
- Complete inventory management (products & ingredients)
- POS/Billing system with discounts
- Production & batch management
- Wastage tracking & reporting
- Sales analytics & audit trails
- Notifications system

**Estimated Timeline:** 4-5 weeks (full-stack development)

---

## 🏗️ PHASE 1: PROJECT SETUP & CONFIGURATION (Week 1)

### Task 1.1: Initialize Django REST Framework & Dependencies
**Status:** NOT STARTED  
**Complexity:** Low  
**Time Est:** 2 hours

- [ ] Create virtual environment
- [ ] Install dependencies:
  ```
  Django==6.0.3
  djangorestframework==3.14.0
  django-cors-headers==4.0.0
  psycopg2-binary (PostgreSQL adapter)
  python-decouple (environment variables)
  Pillow (image handling)
  celery (for async tasks)
  ```
- [ ] Update `settings.py` with:
  - CORS configuration for frontend (http://localhost:5173)
  - REST_FRAMEWORK settings (pagination, authentication)
  - Database configuration (PostgreSQL)
  - Static/Media files
  - Timezone: `Asia/Colombo`
- [ ] Create `.env` file with database credentials

**Deliverables:**
- `requirements.txt` with all dependencies
- Configured `settings.py`
- `.env.example` file for reference

---

### Task 1.2: Setup Django Project Structure
**Status:** Finished 
**Complexity:** Low  
**Time Est:** 1 hour

- [ ] Create proper folder structure:
  ```
  Backend/
  ├── core/               (settings, urls, wsgi)
  ├── api/                (main app)
  │   ├── models/         (separate model files)
  │   ├── views/          (viewsets)
  │   ├── serializers/    (DRF serializers)
  │   ├── filters/        (filtering logic)
  │   ├── utils/          (helper functions)
  │   └── signals.py      (Django signals)
  ├── manage.py
  ├── requirements.txt
  └── .env
  ```
- [ ] Organize models into separate files (not one giant models.py)
- [ ] Create `__init__.py` files as needed

**Deliverables:**
- Organized project structure ready for development

---

### Task 1.3: Database Configuration & Migrations
**Status:** NOT STARTED  
**Complexity:** Low  
**Time Est:** 1 hour

- [ ] Configure PostgreSQL/SQLite in `settings.py`
- [ ] Run initial migrations:
  ```bash
  python manage.py migrate
  ```
- [ ] Create superuser for admin:
  ```bash
  python manage.py createsuperuser
  ```
- [ ] Test database connection

**Deliverables:**
- Working database connection
- Admin accessible at `/admin`

---

## 👥 PHASE 2: USER & AUTHENTICATION (Week 1)

### Task 2.1: Implement User Model & Authentication
**Status:** STARTED  
**Complexity:** Medium  
**Time Est:** 3 hours

**Models to Create:**
- `User` (extends AbstractUser)
  - Fields: employee_id, full_name, nic, contact, role, status, avatar_color, last_login, created_at, updated_at
  - Role choices: Manager, Cashier, Baker, Storekeeper

**Migrations:**
- Create "User" model
- Add default admin user

**Deliverables:**
- User model with all required fields
- Indexes on: employee_id, username, role, status
- Auto-generated employee_id (EMP-001, EMP-002, etc.)

---

### Task 2.2: Implement JWT/Token Authentication
**Status:** NOT STARTED  
**Complexity:** Medium  
**Time Est:** 3 hours

- [ ] Install `djangorestframework-simplejwt`:
  ```
  pip install djangorestframework-simplejwt
  ```
- [ ] Configure JWT in `settings.py`:
  - Token lifetime (access: 1 hour, refresh: 7 days)
  - Token serialization
  - Authentication classes
- [ ] Create authentication endpoints:
  - `POST /api/auth/login/` - Login with username/password
  - `POST /api/auth/refresh/` - Refresh access token
  - `POST /api/auth/logout/` - Logout/Blacklist token
  - `GET /api/auth/me/` - Get current user info

**Serializers:**
- LoginSerializer (username, password)
- TokenSerializer (access, refresh tokens)
- UserSerializer (profile info)

**Deliverables:**
- JWT authentication system
- Token endpoints working
- Role-based access control ready

---

### Task 2.3: User Management API (CRUD)
**Status:** NOT STARTED  
**Complexity:** Medium  
**Time Est:** 3 hours

**Endpoints:**
```
GET    /api/users/              - List all users (Manager only)
POST   /api/users/              - Create new user (Manager only)
GET    /api/users/{id}/         - Get user details
PUT    /api/users/{id}/         - Update user (Manager or self)
DELETE /api/users/{id}/         - Delete user (Manager only)
PATCH  /api/users/{id}/status/  - Change user status (Manager only)
```

**Serializers:**
- UserListSerializer (without password)
- UserDetailSerializer (all fields)
- UserCreateSerializer (with password validation)
- UserUpdateSerializer

**Permissions:**
- Only Manager can create/delete users
- Users can update own profile except role/status
- Manager can update anyone

**Deliverables:**
- Full user CRUD API
- Permission classes for role-based access
- Input validation & error handling

---

## 📦 PHASE 3: INVENTORY SETUP (Week 1-2)

### Task 3.1: Implement Category Models
**Status:** NOT STARTED  
**Complexity:** Low  
**Time Est:** 1.5 hours

**Models:**
- `Category` (unified)
  - Fields: category_id, name, type (Product/Ingredient), description, created_at, updated_at
  - Unique constraint: (type, name)
  - Auto-generate category_id: CAT-P001, CAT-I001, etc.

**Seed Data:**
Product Categories: Buns, Bread, Cakes, Drinks, Pastries  
Ingredient Categories: Flour, Sugar, Dairy, Spices, Additives, Others

**Deliverables:**
- Category model with migrations
- Seed data loaded
- Indexes on: category_id, type, name

---

### Task 3.2: Implement Ingredient Model & Management
**Status:** NOT STARTED  
**Complexity:** Medium  
**Time Est:** 4 hours

**Models:**
- `Ingredient`
  - Fields: ingredient_id, category_id (FK), name, supplier, supplier_contact, tracking_type, base_unit, total_quantity, low_stock_threshold, shelf_life, shelf_unit, created_at, updated_at
  - Auto-generate ingredient_id: #I001, #I002, etc.
  - total_quantity synced via Django signals (sum of active batches)

**Signals:**
- When IngredientBatch is created/updated/deleted → update Ingredient.total_quantity

**Endpoints:**
```
GET    /api/ingredients/           - List with filters (category, low_stock)
POST   /api/ingredients/           - Create ingredient (Manager, Storekeeper can suggest)
GET    /api/ingredients/{id}/      - Get ingredient details
PUT    /api/ingredients/{id}/      - Update ingredient
DELETE /api/ingredients/{id}/      - Delete ingredient (soft delete if batches exist)
GET    /api/ingredients/{id}/history/ - Stock history for ingredient
GET    /api/ingredients/low-stock/ - Get low stock ingredients
```

**Serializers:**
- IngredientListSerializer
- IngredientDetailSerializer (includes batches, recipes using it)
- IngredientCreateSerializer

**Permissions:**
- Manager: Full access
- Storekeeper: Read + create + update
- Baker: Read-only + view history
- Cashier: No access

**Deliverables:**
- Ingredient model with migrations
- Signal for total_quantity sync
- Full ingredient CRUD API
- Low-stock alert endpoint

---

### Task 3.3: Implement Ingredient Batch Management
**Status:** NOT STARTED  
**Complexity:** Medium  
**Time Est:** 4 hours

**Models:**
- `IngredientBatch`
  - Fields: batch_id, ingredient_id (FK), quantity, current_qty, cost_price, made_date, expire_date, status, created_at, updated_at
  - Auto-generate batch_id: BATCH-1001, BATCH-1002, etc.
  - Status: Active, Expired, Used

**Validation:**
- expire_date > made_date
- current_qty ≤ quantity
- Auto-mark as Expired if expire_date < now()

**Endpoints:**
```
GET    /api/batches/               - List batches (with filters)
POST   /api/batches/               - Add new batch (Storekeeper)
GET    /api/batches/{id}/          - Get batch details
PUT    /api/batches/{id}/          - Update batch (Storekeeper)
DELETE /api/batches/{id}/          - Delete batch (Mark as Used/delete if unused)
GET    /api/batches/expiring/      - Get batches expiring within 2 days
GET    /api/ingredients/{id}/batches/ - Get all batches for ingredient
```

**Serializers:**
- BatchListSerializer
- BatchDetailSerializer (includes ingredient details)
- BatchCreateSerializer

**Permissions:**
- Storekeeper: Full access
- Manager: Read-only
- Baker: Read-only
- Cashier: No access

**Deliverables:**
- IngredientBatch model with migrations
- Batch CRUD API
- Expiry alert endpoint
- Signal integration for total_quantity sync

---

### Task 3.4: Implement Product Model
**Status:** NOT STARTED  
**Complexity:** Medium  
**Time Est:** 3 hours

**Models:**
- `Product`
  - Fields: product_id, category_id (FK), name, cost_price, selling_price, current_stock, shelf_life, shelf_unit, image_url, description, created_at, updated_at
  - Auto-generate product_id: #PROD-1001, #PROD-1002, etc.
  - profit_margin calculated: (selling_price - cost_price) / cost_price * 100

**Endpoints:**
```
GET    /api/products/              - List products (with filters, search)
POST   /api/products/              - Create product (Manager only)
GET    /api/products/{id}/         - Get product details with recipe
PUT    /api/products/{id}/         - Update product (Manager only)
DELETE /api/products/{id}/         - Delete product (Manager only)
GET    /api/products/{id}/recipe/  - Get recipe (ingredients needed)
GET    /api/products/category/{cat}/ - Filter by category
GET    /api/products/low-stock/    - Get low-stock products
```

**Serializers:**
- ProductListSerializer (with category name, profit_margin)
- ProductDetailSerializer (includes recipe items)
- ProductCreateSerializer
- ProductSearchSerializer

**Filters:**
- By category
- By status (available, low_stock, out_of_stock)
- Search by name
- Sort by price, margin, stock

**Permissions:**
- Manager: Full CRUD
- Baker: Read-only
- Storekeeper: Read-only
- Cashier: Read-only (for billing)

**Deliverables:**
- Product model with migrations
- Full product CRUD API
- Dynamic profit margin calculation
- Search & filter endpoints

---

### Task 3.5: Implement Recipe Management
**Status:** COMPLETE ✅  
**Complexity:** Medium  
**Time Est:** 4 hours | **Actual:** Completed
**Completion Date:** March 23, 2026

**Models:** ✅
- `RecipeItem` - Fully implemented
  - Fields: product_id (FK), ingredient_id (FK), quantity_required, created_at, updated_at
  - Unique constraint: (product_id, ingredient_id)
  - Validation: quantity_required > 0

**Endpoints:** ✅ ALL WORKING
```
GET    /api/recipes/{id}/                  - Get recipe for product ✓
POST   /api/recipes/{id}/items/            - Add ingredient to recipe (Manager) ✓
PUT    /api/recipes/{id}/items/{ing_id}/   - Update recipe item qty ✓
DELETE /api/recipes/{id}/items/{ing_id}/   - Remove ingredient from recipe ✓
GET    /api/recipes/{id}/validate/         - Check if can make product ✓
GET    /api/recipes/{id}/batch_required/   - Calculate ingredients for batch ✓
```

**Serializers:** ✅ 5 SERIALIZERS
- RecipeItemSerializer - CRUD operations with validation
- RecipeDetailSerializer - Expanded ingredient info with costs
- RecipeListSerializer - Aggregated recipe view
- RecipeValidationSerializer - Validation result format
- BatchCalculationSerializer - Batch requirements response

**Business Logic:** ✅ ALL IMPLEMENTED
- Prevent duplicate ingredients in same recipe (unique constraint + validation)
- Calculate cost_price automatically from recipe when saved
- Validate quantity_required is positive (model.save())
- Endpoint to calculate ingredient needs for batch production
- Auto-recalculate when recipe items modified

**Permissions:** ✅ ENFORCED
- Manager: Full CRUD on recipes
- Baker: Read-only + validation
- Others: No access (403 Forbidden)

**Database:** ✅ MIGRATED
- Migration 0008_recipeitem_and_more.py applied successfully
- RecipeItem table with proper indexes
- Unique constraint on (product_id, ingredient_id)

**URL Routing:** ✅ FIXED
- Changed from detail=False with complex regex to detail=True
- All URLs now clean: /api/recipes/{id}/{action}/
- No more 301 redirects

**Testing & Documentation:** ✅ COMPLETE
- TASK_3_5_TESTING_GUIDE.md - Comprehensive manual testing guide
- TASK_3_5_COMPLETION_REPORT.md - Full implementation details
- 6 test cases with expected responses
- Business logic validations documented
- Error scenarios covered

**Deliverables:** ✅ ALL COMPLETE
- [✓] RecipeItem model with migrations
- [✓] Full recipe CRUD API (6 endpoints)
- [✓] Validation & batch calculation endpoints  
- [✓] Automatic cost_price calculation
- [✓] Comprehensive testing documentation

---

## 💳 PHASE 4: POS & SALES (Week 2-3)

### Task 4.1: Implement Discount Model
**Status:** ✅ COMPLETE  
**Complexity:** Medium  
**Time Est:** 3 hours

**Models:**
- `Discount`
  - Fields: discount_id, name, type (Percentage/FixedAmount), value, applicable_to (All/Category/Product), target_category_id (FK, nullable), target_product_id (FK, nullable), start_date, end_date, start_time, end_time, is_active, created_at, updated_at
  - Auto-generate discount_id: DISC-001, DISC-002, etc.

**Check Constraints:**
- Ensure only one target is set based on applicable_to
- start_date ≤ end_date
- start_time < end_time

**Endpoints:**
```
GET    /api/discounts/                       - List all discounts (Manager only)
POST   /api/discounts/                       - Create discount (Manager only)
GET    /api/discounts/{id}/                  - Get discount details
PUT    /api/discounts/{id}/                  - Update discount (Manager only)
DELETE /api/discounts/{id}/                  - Delete discount (Manager only)
PATCH  /api/discounts/{id}/toggle/           - Toggle active/inactive
GET    /api/discounts/active/                - Get active discounts (for billing)
POST   /api/discounts/validate/              - Check if discount applicable to product
```

**Serializers:**
- DiscountListSerializer
- DiscountDetailSerializer
- DiscountCreateSerializer

**Permissions:**
- Manager: Full CRUD + activate/deactivate
- Others: No access

**Helper Function:**
```python
def is_discount_applicable(discount, product, current_datetime):
    """Check if discount can be applied to product at given time"""
    if not discount.is_active:
        return False
    
    # Date validation
    if discount.start_date and current_datetime.date() < discount.start_date:
        return False
    if discount.end_date and current_datetime.date() > discount.end_date:
        return False
    
    # Time validation
    if discount.start_time and current_datetime.time() < discount.start_time:
        return False
    if discount.end_time and current_datetime.time() > discount.end_time:
        return False
    
    # Applicability validation
    if discount.applicable_to == 'Category':
        return product.category_id == discount.target_category_id
    elif discount.applicable_to == 'Product':
        return product.id == discount.target_product_id
    elif discount.applicable_to == 'All':
        return True
    
    return False
```

**Deliverables:**
- Discount model with migrations
- Full discount CRUD API
- Active discounts endpoint
- Validation helper function

---

### Task 4.2: Implement Sales & Sale Items Models
**Status:** NOT STARTED  
**Complexity:** Medium  
**Time Est:** 4 hours

**Models:**
- `Sale` (Bill Header)
  - Fields: bill_number, cashier_id (FK), subtotal, discount_id (FK, nullable), discount_amount, total_amount, payment_method, date_time, created_at, updated_at
  - Auto-generate bill_number: BILL-1001, BILL-1002, etc.

- `SaleItem` (Bill Line Items)
  - Fields: sale_id (FK), product_id (FK), quantity, unit_price (frozen at checkout time), subtotal, created_at

**Endpoints:**
```
GET    /api/sales/                           - List all sales (Manager, Cashier can see own)
POST   /api/sales/                           - Create sale (Cashier - process checkout)
GET    /api/sales/{bill_number}/             - Get sale details with items
GET    /api/sales/date-range/                - Sales by date range (with filters)
GET    /api/sales/cashier/{cashier_id}/      - Sales by cashier
GET    /api/sales/payment-method/{method}/   - Sales by payment method
GET    /api/sales/analytics/                 - Daily/weekly/monthly totals
```

**Serializers:**
- SaleListSerializer
- SaleDetailSerializer (includes items with product names)
- SaleItemSerializer
- SaleCreateSerializer

**Permissions:**
- Manager: Read all sales
- Cashier: Create sale + read own sales
- Others: No access

**Business Logic:**
```python
def create_sale(data):
    """
    1. Validate all products exist and have stock
    2. Calculate subtotal = sum(qty * unit_price)
    3. If discount_id provided:
       - Check if applicable
       - Calculate discount_amount
    4. total_amount = subtotal - discount_amount
    5. Create Sale record
    6. Create SaleItem records
    7. Deduct from product stock
    8. Create product_stock_history entries
    9. Return success response
    """
```

**Deliverables:**
- Sale & SaleItem models with migrations
- Full sales CRUD API
- Sales analytics endpoints
- Stock deduction logic
- Audit trail creation

---

### Task 4.3: Implement Production & Product Batches
**Status:** NOT STARTED  
**Complexity:** Medium  
**Time Est:** 3 hours

**Models:**
- `ProductBatch`
  - Fields: batch_id, product_id (FK), quantity, made_date, expire_date, notes, created_at, updated_at
  - Auto-generate batch_id: PROD-BATCH-1001, etc.
  - expire_date calculated from product.shelf_life

**Endpoints:**
```
GET    /api/product-batches/                 - List product batches
POST   /api/product-batches/                 - Create batch (Baker only)
GET    /api/product-batches/{id}/            - Get batch details
PUT    /api/product-batches/{id}/            - Update batch
DELETE /api/product-batches/{id}/            - Delete batch
GET    /api/product-batches/expiring/        - Get expiring soon
GET    /api/products/{id}/batches/           - Batches for product
POST   /api/product-batches/{id}/use/        - Use batch quantity (for production)
```

**Serializers:**
- ProductBatchListSerializer
- ProductBatchDetailSerializer
- ProductBatchCreateSerializer

**Permissions:**
- Baker: Create batches + use batches
- Storekeeper: Read-only
- Manager: Full access
- Cashier: No access

**Business Logic:**
- When batch created: add quantity to product.current_stock
- When batch used/deleted: deduct from product.current_stock
- Auto-calculate expire_date from product.shelf_life
- Create product_stock_history for audit trail

**Deliverables:**
- ProductBatch model with migrations
- Full production batch API
- Stock management endpoints
- Audit trail creation

---

## 🗑️ PHASE 5: WASTAGE TRACKING (Week 3)

### Task 5.1: Implement Wastage Reason Model
**Status:** NOT STARTED  
**Complexity:** Low  
**Time Est:** 1 hour

**Models:**
- `WastageReason`
  - Fields: reason_id, reason (unique), description, created_at
  - Auto-generate reason_id: WR-001, WR-002, etc.

**Seed Data:**
- Expired, Damaged, Spilled, Theft, Spoiled, Pest Damage, Burn, Other

**Endpoints:**
```
GET /api/wastage-reasons/ - List all reasons
```

**Deliverables:**
- WastageReason model with migrations
- Seed data loaded

---

### Task 5.2: Implement Product Wastage Tracking
**Status:** NOT STARTED  
**Complexity:** Medium  
**Time Est:** 3 hours

**Models:**
- `ProductWastage`
  - Fields: wastage_id, product_id (FK), quantity, unit_cost, total_loss, reason_id (FK), reported_by (FK), notes, created_at, updated_at
  - Auto-generate wastage_id: PW-001, PW-002, etc.

**Endpoints:**
```
GET    /api/product-wastages/                - List wastages (with filters)
POST   /api/product-wastages/                - Report product wastage (Baker, Cashier, Manager)
GET    /api/product-wastages/{id}/           - Get wastage details
DELETE /api/product-wastages/{id}/           - Delete/undo wastage (Manager only)
GET    /api/product-wastages/analytics/      - Wastage by reason/product/date
GET    /api/products/{id}/wastage-history/   - Wastage history for product
```

**Serializers:**
- ProductWastageListSerializer
- ProductWastageDetailSerializer (includes product, reason, user info)
- ProductWastageCreateSerializer

**Permissions:**
- Baker: Report wastage on products
- Cashier: Report wastage during sales
- Manager: Full access + delete wastage
- Others: Read-only

**Business Logic:**
- Deduct quantity from product.current_stock
- total_loss = quantity * unit_cost
- Create product_stock_history entry
- Trigger notification for high wastage (>5% of daily production)

**Deliverables:**
- ProductWastage model with migrations
- Full wastage CRUD API
- Analytics endpoints
- Notifications integration

---

### Task 5.3: Implement Ingredient Wastage Tracking
**Status:** NOT STARTED  
**Complexity:** Medium  
**Time Est:** 3 hours

**Models:**
- `IngredientWastage`
  - Fields: wastage_id, ingredient_id (FK), batch_id (FK, nullable), quantity, unit_cost, total_loss, reason_id (FK), reported_by (FK), notes, created_at, updated_at
  - Auto-generate wastage_id: IW-001, IW-002, etc.

**Endpoints:**
```
GET    /api/ingredient-wastages/             - List wastages
POST   /api/ingredient-wastages/             - Report ingredient wastage (Storekeeper)
GET    /api/ingredient-wastages/{id}/        - Get wastage details
DELETE /api/ingredient-wastages/{id}/        - Delete wastage (Manager)
GET    /api/ingredient-wastages/analytics/   - Analytics by reason/ingredient/date
GET    /api/ingredients/{id}/wastage-history/ - Wastage for ingredient
```

**Serializers:**
- IngredientWastageListSerializer
- IngredientWastageDetailSerializer
- IngredientWastageCreateSerializer

**Permissions:**
- Storekeeper: Report wastage on ingredients
- Manager: Full access + delete
- Others: Read-only

**Deliverables:**
- IngredientWastage model with migrations
- Full wastage CRUD API
- Analytics endpoints

---

## 📊 PHASE 6: AUDIT TRAILS & STOCK HISTORY (Week 3)

### Task 6.1: Implement Stock History Models
**Status:** NOT STARTED  
**Complexity:** Medium  
**Time Est:** 3 hours

**Models:**
- `ProductStockHistory`
  - Fields: product_id (FK), transaction_type (AddStock/UseStock/Wastage/Adjustment), qty_before, qty_after, change_amount, performed_by (FK), reference_id, notes, created_at

- `IngredientStockHistory`
  - Fields: ingredient_id (FK), transaction_type, qty_before, qty_after, change_amount, performed_by (FK), reference_id, notes, created_at

**Endpoints:**
```
GET /api/products/{id}/stock-history/        - Stock history for product
GET /api/ingredients/{id}/stock-history/     - Stock history for ingredient
GET /api/stock-history/search/               - Search transactions by date/type
```

**Serializers:**
- StockHistoryListSerializer (with user, product/ingredient names)

**Automated Creation:**
Use Django signals to auto-create history entries when:
- Sale created (UseStock)
- ProductBatch created (AddStock)
- ProductWastage created (Wastage)
- IngredientBatch operations (AddStock/UseStock)
- Manual stock adjustments

**Deliverables:**
- Stock history models with migrations
- Audit trail endpoints
- Signal handlers for auto-logging

---

## 🔔 PHASE 7: NOTIFICATIONS (Week 4)

### Task 7.1: Implement Notification System
**Status:** NOT STARTED  
**Complexity:** Medium  
**Time Est:** 4 hours

**Models:**
- `Notification`
  - Fields: title, message, type (LowStock/Expiry/System/Warning), icon, created_at

- `NotificationReceipt` (Per-user read tracking)
  - Fields: notification_id (FK), user_id (FK), is_read, read_at, created_at
  - Unique constraint: (notification_id, user_id)

**Endpoints:**
```
GET    /api/notifications/                   - Get my notifications
PATCH  /api/notifications/{id}/read/         - Mark as read
PATCH  /api/notifications/read-all/          - Mark all as read
DELETE /api/notifications/{id}/              - Delete notification
GET    /api/notifications/unread/count/      - Unread count
```

**Serializers:**
- NotificationListSerializer
- NotificationReceiptSerializer

**Automated Notifications:**
Create notification when:
1. **Low Stock Alert** - Ingredient below threshold
2. **Expiry Alert** - Batch expiring within 2 days
3. **High Wastage** - Daily wastage > 5%
4. **Out of Stock** - Product becomes unavailable
5. **System Alert** - Errors, maintenance notifications

**Worker Tasks (Celery):**
```python
# Check and create notifications every hour
@periodic_task(run_every=crontab(minute=0))
def check_low_stock_alerts():
    low_ingredients = Ingredient.objects.filter(
        total_quantity__lt=F('low_stock_threshold')
    )
    for ingredient in low_ingredients:
        create_notification_for_users(
            type='LowStock',
            title=f'Low Stock: {ingredient.name}',
            message=f'{ingredient.name} ({ingredient.total_quantity} {ingredient.base_unit}) is below threshold',
            roles=['Manager', 'Storekeeper', 'Baker']
        )

@periodic_task(run_every=crontab(minute=0))
def check_expiry_alerts():
    expiring_batches = IngredientBatch.objects.filter(
        expire_date__lte=now() + timedelta(days=2),
        status='Active'
    )
    for batch in expiring_batches:
        create_notification_for_users(
            type='Expiry',
            title=f'Expiring Soon: {batch.ingredient.name}',
            message=f'Batch {batch.batch_id} expires on {batch.expire_date}',
            roles=['Storekeeper', 'Manager']
        )
```

**Deliverables:**
- Notification models with migrations
- Notification endpoints
- Celery tasks for auto-alerts
- Signal handlers for manual alerts

---

## 📈 PHASE 8: ANALYTICS & REPORTING (Week 4)

### Task 8.1: Sales Analytics Endpoints
**Status:** NOT STARTED  
**Complexity:** Medium  
**Time Est:** 3 hours

**Endpoints:**
```
GET /api/analytics/sales/daily/          - Daily sales totals
GET /api/analytics/sales/weekly/         - Weekly sales
GET /api/analytics/sales/monthly/        - Monthly sales
GET /api/analytics/sales/top-products/   - Top-selling products
GET /api/analytics/sales/by-category/    - Sales by category
GET /api/analytics/sales/by-cashier/     - Sales by cashier
GET /api/analytics/revenue/              - Revenue vs cost analysis
```

**Response Format:**
```json
{
  "period": "2026-03-22",
  "total_sales": 45000,
  "total_discount": 3000,
  "revenue": 42000,
  "transaction_count": 52,
  "items_sold": 125
}
```

**Deliverables:**
- Sales analytics endpoints
- Date range filtering
- CSV export option

---

### Task 8.2: Inventory Analytics
**Status:** NOT STARTED  
**Complexity:** Medium  
**Time Est:** 3 hours

**Endpoints:**
```
GET /api/analytics/inventory/stock-value/    - Total inventory value
GET /api/analytics/inventory/turnover/       - Stock turnover rate
GET /api/analytics/inventory/expired/        - Expired items value
GET /api/analytics/wastage/summary/          - Total wastage by reason
GET /api/analytics/wastage/trend/            - Wastage trend over time
GET /api/analytics/ingredients/usage/        - Ingredient usage rates
```

**Calculations:**
- Stock value = sum(current_quantity * cost_price)
- Turnover rate = (Total sold in period) / (Avg inventory)
- Wastage % = (Total wastage loss) / (Total revenue)

**Deliverables:**
- Inventory analytics endpoints
- Financial impact calculations
- Trend analysis

---

### Task 8.3: KPI Dashboard Data
**Status:** NOT STARTED  
**Complexity:** Low  
**Time Est:** 2 hours

**Endpoints:**
```
GET /api/dashboard/kpis/                  - All KPIs
  - Total Users
  - Total Revenue (today/week/month)
  - Total Transactions (today/week/month)
  - Active Discounts Count
  - Low Stock Items Count
  - Expiring Items Count (within 2 days)
  - High Wastage Alert Count
```

**Deliverables:**
- KPI aggregation endpoint
- Real-time calculations
- Role-specific KPIs

---

## 🔒 PHASE 9: PERMISSIONS & SECURITY (Week 4)

### Task 9.1: Implement Permission Classes
**Status:** NOT STARTED  
**Complexity:** Medium  
**Time Est:** 3 hours

**Permission Classes to Create:**
```python
# api/permissions.py

class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'Manager'

class IsManagerOrStorekeeper(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role in ['Manager', 'Storekeeper']

# Similar for other combinations...
```

**Apply Permissions:**
- User CRUD: IsManager
- Product CRUD: IsManager only
- Ingredient CRUD: IsManager or IsStorekeeper
- Batch CRUD: IsStorekeeper mainly
- Sales: IsCashier create, IsManager read
- Wastage Report: Based on item type
- Discount CRUD: IsManager only

**Deliverables:**
- Custom permission classes
- Applied to all ViewSets
- Tested authorization

---

### Task 9.2: Input Validation & Error Handling
**Status:** NOT STARTED  
**Complexity:** Medium  
**Time Est:** 2 hours

**Implement:**
- Serializer validation for all inputs
- Custom validators (contact format, etc.)
- Standardized error responses
- 404, 400, 403 error handling
- Request data sanitization

**Error Response Format:**
```json
{
  "success": false,
  "error": "Validation Error",
  "details": {
    "contact": ["Invalid contact format. Expected: XXX-XXXXXXX"]
  }
}
```

**Deliverables:**
- Comprehensive input validation
- Standardized error handling
- Security best practices

---

### Task 9.3: API Documentation (Swagger/OpenAPI)
**Status:** NOT STARTED  
**Complexity:** Low  
**Time Est:** 2 hours

- [ ] Install `drf-spectacular`:
  ```
  pip install drf-spectacular
  ```
- [ ] Configure Swagger in settings.py
- [ ] Generate auto-documentation from docstrings
- [ ] Add to `/api/docs/` endpoint

**Deliverables:**
- Auto-generated API documentation
- Swagger UI accessible
- All endpoints documented

---

## 🧪 PHASE 10: TESTING & DEPLOYMENT (Week 5)

### Task 10.1: Unit & Integration Tests
**Status:** NOT STARTED  
**Complexity:** High  
**Time Est:** 8 hours

**Test Coverage:**
- User authentication & permissions (90%+)
- Product/Ingredient CRUD (90%+)
- Sales creation & calculation (95%+)
- Wastage tracking accuracy (95%+)
- Stock history audit trail (90%+)

**Test Files:**
```
Backend/
├── tests/
│   ├── test_auth.py
│   ├── test_users.py
│   ├── test_products.py
│   ├── test_ingredients.py
│   ├── test_sales.py
│   ├── test_wastage.py
│   └── test_analytics.py
```

**Deliverables:**
- Test suite for all models & APIs
- Minimum 80% code coverage
- All tests passing

---

### Task 10.2: Performance Optimization
**Status:** NOT STARTED  
**Complexity:** Medium  
**Time Est:** 4 hours

**Optimize:**
- Database query optimization (select_related, prefetch_related)
- Pagination on list endpoints
- Caching for admin dashboards
- Indexes verification
- Query count optimization

**Deliverables:**
- Query optimization applied
- Pagination configured
- Cache layer implemented

---

### Task 10.3: Deployment Setup
**Status:** NOT STARTED  
**Complexity:** Medium  
**Time Est:** 3 hours

**Prepare:**
- Production settings.py
- Environment variables
- Database backup strategy
- Static files collection
- Media files handling
- HTTPS configuration
- CORS security hardening

**Deploy To:**
- Local: SQLite or PostgreSQL
- Staging: PostgreSQL with backups
- Production: PostgreSQL RDS or managed
- Server: Docker + Gunicorn + Nginx

**Deliverables:**
- Docker configuration
- Deployment documentation
- Production checklist

---

## 📋 SUMMARY OF DELIVERABLES

| Phase | Main Components | Estimated Hours |
|-------|-----------------|-----------------|
| 1. Setup | Django config, folder structure, DB | 6 |
| 2. Auth | User model, JWT, user CRUD | 9 |
| 3. Inventory | Categories, Ingredients, Products, Recipes | 16 |
| 4. Sales | Discounts, Sales, Production batches | 10 |
| 5. Wastage | Wastage tracking (product & ingredient) | 6 |
| 6. Audit | Stock history, audit trails | 3 |
| 7. Notifications | Notification system, alerts | 4 |
| 8. Analytics | Sales, inventory, KPI dashboards | 8 |
| 9. Security | Permissions, validation, documentation | 7 |
| 10. Testing | Unit tests, performance, deployment | 15 |
| **TOTAL** | **All backend features** | **~84 hours** |

---

## 🎯 COMPLETION CHECKLIST

### Database & Models
- [ ] All 15+ models implemented
- [ ] All migrations created & applied
- [ ] Indexes created on foreign keys & frequently queried fields
- [ ] Check constraints implemented
- [ ] Django signals for stock sync working

### APIs
- [ ] 50+ REST endpoints implemented
- [ ] Pagination, filtering, search working
- [ ] Sorting on key fields
- [ ] All CRUD operations complete

### Authentication & Security
- [ ] JWT authentication implemented
- [ ] All permission classes applied
- [ ] Input validation on all endpoints
- [ ] SQL injection prevention
- [ ] CORS configured properly

### Business Logic
- [ ] Stock calculations accurate
- [ ] Discount calculation verified
- [ ] Profit margin calculations correct
- [ ] Expiry date logic working
- [ ] Wastage tracking accurate

### Testing
- [ ] 80%+ code coverage
- [ ] All critical paths tested
- [ ] Error scenarios tested
- [ ] Integration tests passing

### Documentation
- [ ] API documentation (Swagger)
- [ ] Code comments on complex logic
- [ ] Database schema documented
- [ ] Deployment guide

### Frontend Integration Ready
- [ ] All endpoints return correct JSON format
- [ ] Timestamps in ISO 8601 format
- [ ] Error responses standardized
- [ ] CORS headers configured
- [ ] Sample API calls documented

---

## 🚀 NEXT STEPS

1. **Start Phase 1** immediately - Setup & configuration
2. **Complete Phase 2** - User authentication is critical
3. **Proceed sequentially** - Each phase depends on previous
4. **Test incrementally** - Don't leave testing for the end
5. **Document as you go** - Keep API documentation updated

---

## 📞 SUPPORT & RESOURCES

**Django Documentation:** https://docs.djangoproject.com/  
**DRF Serializers:** https://www.django-rest-framework.org/api-guide/serializers/  
**PostgreSQL:** https://www.postgresql.org/docs/  
**JWT Auth:** https://django-rest-framework-simplejwt.readthedocs.io/  

---

**Document Created:** March 22, 2026  
**Version:** 1.0  
**Status:** Ready for Implementation
