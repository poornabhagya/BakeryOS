# BakeryOS Backend - Quick Reference Implementation Checklist

## Phase 1: Project Setup ✅ / 🔄 / ❌

### 1.1 Dependencies & Virtual Environment
- [ ] Create Python virtual environment: `python -m venv venv`
- [ ] Activate venv: `venv\Scripts\activate` (Windows)
- [ ] Create `requirements.txt` with:
  - Django==6.0.3
  - djangorestframework==3.14.0
  - django-cors-headers==4.0.0
  - djangorestframework-simplejwt==5.2.2
  - psycopg2-binary==2.9.6
  - python-decouple==3.8
  - Pillow==9.5.0
  - celery==5.3.1
  - drf-spectacular==0.26.1
  - django-filter==23.1
  - pytest-django==4.5.2
- [ ] Install: `pip install -r requirements.txt`

### 1.2 Settings Configuration
- [ ] Update `INSTALLED_APPS`: api, rest_framework, corsheaders, drf_spectacular, django_filters
- [ ] Configure CORS_ALLOWED_ORIGINS: http://localhost:5173, http://localhost:3000
- [ ] Set REST_FRAMEWORK auth: TokenAuthentication, JWTAuthentication
- [ ] Set TIME_ZONE: 'Asia/Colombo'
- [ ] Create `.env` file with DATABASE credentials
- [ ] Configure static/media files

### 1.3 Project Structure
- [ ] Create `api/models/` directory with separate model files
- [ ] Create `api/views/` directory with viewsets
- [ ] Create `api/serializers/` directory with serializers
- [ ] Create `api/permissions/` with custom permission classes
- [ ] Create `api/utils/` with helper functions
- [ ] Create `tests/` directory with test files

### 1.4 Database Setup
- [ ] Configure PostgreSQL or SQLite in settings.py
- [ ] Run: `python manage.py migrate`
- [ ] Create superuser: `python manage.py createsuperuser`
- [ ] Verify admin: http://localhost:8000/admin

---

## Phase 2: Authentication & Users 👤

### 2.1 User Model
- [ ] Extend AbstractUser with fields:
  - employee_id (unique, auto-generated: EMP-001)
  - full_name
  - nic (national ID)
  - contact (phone validation)
  - role (Manager/Cashier/Baker/Storekeeper)
  - status (Active/Inactive)
  - avatar_color
  - last_login
  - created_at, updated_at
- [ ] Add indexes on: employee_id, username, role, status
- [ ] Run migration: `python manage.py makemigrations && migrate`
- [ ] Register in admin.py

### 2.2 JWT Authentication
- [ ] Install: `pip install djangorestframework-simplejwt`
- [ ] Add to settings: SIMPLE_JWT configuration
- [ ] Create serializers:
  - LoginSerializer
  - TokenSerializer
  - UserSerializer
- [ ] Create viewsets: AuthViewSet with login/refresh/logout
- [ ] Add routes in urls.py
- [ ] Test endpoints with Postman/curl

### 2.3 User Management API
- [ ] Viewset: UserViewSet with CRUD
- [ ] Serializers: UserList, UserDetail, UserCreate, UserUpdate
- [ ] Permissions: IsManager, IsManagerOrSelf
- [ ] Endpoints:
  - GET/POST /api/users/
  - GET/PUT/DELETE /api/users/{id}/
  - PATCH /api/users/{id}/status/
- [ ] Add search/filter by role, status
- [ ] Auto-generate employee_id

---

## Phase 3: Inventory 📦

### 3.1 Categories
- [ ] Model: Category (unified for Product/Ingredient)
  - category_id (auto: CAT-P001, CAT-I001)
  - name, type (Product/Ingredient)
  - created_at, updated_at
- [ ] Seed categories (Products: Buns, Bread, Cakes, etc.)
- [ ] Seed categories (Ingredients: Flour, Sugar, Dairy, etc.)
- [ ] Endpoint: GET /api/categories/ with type filter

### 3.2 Ingredients
- [ ] Model: Ingredient
  - ingredient_id (auto: #I001)
  - category_id (FK)
  - name, supplier, supplier_contact
  - tracking_type (Weight/Volume/Count)
  - base_unit (g/ml/nos)
  - total_quantity, low_stock_threshold
  - shelf_life, shelf_unit
  - created_at, updated_at
- [ ] Create indexes on: ingredient_id, category_id, name, supplier
- [ ] Serializers: IngredientList, IngredientDetail, IngredientCreate
- [ ] Permissions: Manager/Storekeeper write, Baker read-only
- [ ] Endpoints:
  - GET /api/ingredients/ (with filters)
  - POST /api/ingredients/
  - GET /api/ingredients/{id}/
  - PUT /api/ingredients/{id}/
  - GET /api/ingredients/low-stock/

### 3.3 Ingredient Batches
- [ ] Model: IngredientBatch
  - batch_id (auto: BATCH-1001)
  - ingredient_id (FK)
  - quantity, current_qty
  - cost_price, made_date, expire_date
  - status (Active/Expired/Used)
- [ ] Validation: expire_date > made_date, current_qty ≤ quantity
- [ ] Signal: Update ingredient.total_quantity on batch changes
- [ ] Endpoints:
  - GET /api/batches/
  - POST /api/batches/
  - GET /api/batches/expiring/
  - GET /api/ingredients/{id}/batches/

### 3.4 Products
- [ ] Model: Product
  - product_id (auto: #PROD-1001)
  - category_id (FK)
  - name, cost_price, selling_price
  - current_stock, shelf_life, shelf_unit
  - image_url, description
  - profit_margin (calculated)
- [ ] Serializers with profit_margin calculation
- [ ] Permissions: Manager full, others read-only
- [ ] Endpoints:
  - GET /api/products/ (search, filter by category)
  - POST /api/products/
  - GET /api/products/{id}/
  - PUT /api/products/{id}/
  - GET /api/products/low-stock/

### 3.5 Recipes
- [ ] Model: RecipeItem
  - product_id (FK), ingredient_id (FK)
  - quantity_required (in ingredient's base_unit)
  - Unique: (product_id, ingredient_id)
- [ ] Endpoints:
  - GET /api/recipes/{product_id}/
  - POST /api/recipes/{product_id}/items/
  - PUT /api/recipes/{product_id}/items/{ingredient_id}/
  - DELETE /api/recipes/{product_id}/items/{ingredient_id}/
  - POST /api/recipes/validate/{product_id}/
  - POST /api/recipes/batch-required/{product_id}/
- [ ] Auto-calculate product.cost_price from recipe

---

## Phase 4: Sales & POS 💳

### 4.1 Discounts
- [ ] Model: Discount
  - discount_id (auto: DISC-001)
  - name, type (Percentage/FixedAmount)
  - value, applicable_to (All/Category/Product)
  - target_category_id, target_product_id
  - start_date, end_date, start_time, end_time
  - is_active
- [ ] Check constraints on targets & dates
- [ ] Helper: is_discount_applicable(discount, product, datetime)
- [ ] Endpoints:
  - GET /api/discounts/ (Manager only)
  - POST /api/discounts/
  - PATCH /api/discounts/{id}/toggle/
  - GET /api/discounts/active/ (for billing)
  - POST /api/discounts/validate/

### 4.2 Sales & Sale Items
- [ ] Model: Sale
  - bill_number (auto: BILL-1001)
  - cashier_id (FK)
  - subtotal, discount_id (FK), discount_amount
  - total_amount, payment_method
  - date_time, created_at, updated_at
- [ ] Model: SaleItem
  - sale_id (FK), product_id (FK)
  - quantity, unit_price (frozen), subtotal
- [ ] Business logic:
  - Validate stock before creating
  - Calculate subtotal
  - Apply discount if applicable
  - Deduct from product stock
  - Create stock history entry
- [ ] Endpoints:
  - GET /api/sales/
  - POST /api/sales/ (checkout)
  - GET /api/sales/{bill_number}/
  - GET /api/sales/date-range/
  - GET /api/sales/analytics/

### 4.3 Product Batches
- [ ] Model: ProductBatch
  - batch_id (auto: PROD-BATCH-1001)
  - product_id (FK), quantity
  - made_date, expire_date (auto-calculated)
  - notes
- [ ] Signal: Update product.current_stock on batch changes
- [ ] Endpoints:
  - GET /api/product-batches/
  - POST /api/product-batches/ (Baker)
  - GET /api/product-batches/expiring/
  - POST /api/product-batches/{id}/use/

---

## Phase 5: Wastage 🗑️

### 5.1 Wastage Reasons
- [ ] Model: WastageReason
  - reason_id (auto: WR-001)
  - reason (unique)
  - description
- [ ] Seed data: Expired, Damaged, Spilled, Theft, Spoiled, Pest Damage, Burn, Other

### 5.2 Product Wastage
- [ ] Model: ProductWastage
  - wastage_id (auto: PW-001)
  - product_id (FK), quantity, unit_cost, total_loss
  - reason_id (FK), reported_by (FK)
  - notes, created_at, updated_at
- [ ] Signal: Deduct from product.current_stock
- [ ] Trigger notification if wastage > 5%
- [ ] Endpoints:
  - GET /api/product-wastages/
  - POST /api/product-wastages/
  - GET /api/product-wastages/analytics/
  - GET /api/products/{id}/wastage-history/

### 5.3 Ingredient Wastage
- [ ] Model: IngredientWastage
  - wastage_id (auto: IW-001)
  - ingredient_id (FK), batch_id (FK, nullable)
  - quantity, unit_cost, total_loss
  - reason_id (FK), reported_by (FK)
- [ ] Signal: Deduct from ingredient.total_quantity
- [ ] Endpoints:
  - GET /api/ingredient-wastages/
  - POST /api/ingredient-wastages/
  - GET /api/ingredient-wastages/analytics/

---

## Phase 6: Audit Trails 📝

### 6.1 Stock History
- [ ] Model: ProductStockHistory
  - product_id (FK), transaction_type (AddStock/UseStock/Wastage/Adjustment)
  - qty_before, qty_after, change_amount
  - performed_by (FK), reference_id, notes
  - created_at
- [ ] Model: IngredientStockHistory
  - ingredient_id (FK), transaction_type
  - qty_before, qty_after, change_amount
  - performed_by (FK), reference_id, notes
- [ ] Signals: Auto-create entries for all stock changes
- [ ] Endpoints:
  - GET /api/products/{id}/stock-history/
  - GET /api/ingredients/{id}/stock-history/

---

## Phase 7: Notifications 🔔

### 7.1 Notification Models
- [ ] Model: Notification
  - title, message, type (LowStock/Expiry/System/Warning)
  - icon, created_at
- [ ] Model: NotificationReceipt
  - notification_id (FK), user_id (FK)
  - is_read, read_at, created_at
  - Unique: (notification_id, user_id)
- [ ] Endpoints:
  - GET /api/notifications/
  - PATCH /api/notifications/{id}/read/
  - GET /api/notifications/unread/count/

### 7.2 Celery Tasks
- [ ] Task: check_low_stock_alerts (hourly)
- [ ] Task: check_expiry_alerts (hourly)
- [ ] Task: high_wastage_alert (daily)
- [ ] Function: create_notification_for_users(type, title, message, roles)

---

## Phase 8: Analytics 📊

### 8.1 Sales Analytics
- [ ] Endpoint: GET /api/analytics/sales/daily/
- [ ] Endpoint: GET /api/analytics/sales/weekly/
- [ ] Endpoint: GET /api/analytics/sales/monthly/
- [ ] Endpoint: GET /api/analytics/sales/top-products/
- [ ] Endpoint: GET /api/analytics/revenue/

### 8.2 Inventory Analytics
- [ ] Endpoint: GET /api/analytics/inventory/stock-value/
- [ ] Endpoint: GET /api/analytics/inventory/expired/
- [ ] Endpoint: GET /api/analytics/wastage/summary/

### 8.3 Dashboard KPIs
- [ ] Endpoint: GET /api/dashboard/kpis/
- [ ] Returns: Total users, revenue, transactions, low stock count, expiring count

---

## Phase 9: Permissions & Security 🔐

### 9.1 Permission Classes
- [ ] IsManager
- [ ] IsCashier
- [ ] IsBaker
- [ ] IsStorekeeper
- [ ] IsManagerOrStorekeeper
- [ ] IsManagerOrSelf
- [ ] Combinations as needed

### 9.2 Input Validation
- [ ] Contact format validation (XXX-XXXXXXX)
- [ ] Quantity ≥ 0 validation
- [ ] Price ≥ 0 validation
- [ ] Date logic validation
- [ ] Serializer field validators
- [ ] Custom validators for business rules

### 9.3 API Documentation
- [ ] Install drf-spectacular
- [ ] Configure Swagger in settings
- [ ] Swagger UI at /api/schema/swagger-ui/
- [ ] OpenAPI schema at /api/schema/

---

## Phase 10: Testing & Deployment 🚀

### 10.1 Unit Tests
- [ ] test_auth.py: Login, token refresh, logout
- [ ] test_users.py: User CRUD, permissions
- [ ] test_products.py: Product CRUD, profit calc
- [ ] test_sales.py: Sale creation, stock deduction
- [ ] test_ingredients.py: Ingredient CRUD, batches
- [ ] test_wastage.py: Wastage tracking, notifications
- [ ] test_analytics.py: KPI calculations

### 10.2 Performance
- [ ] Add select_related for ForeignKeys
- [ ] Add prefetch_related for reverse relations
- [ ] Configure pagination (default 20, max 100)
- [ ] Add query count logging in development
- [ ] Test with 10k+ records

### 10.3 Deployment
- [ ] Create Docker configuration
- [ ] Create docker-compose.yml (Django + PostgreSQL)
- [ ] Gunicorn setup
- [ ] Nginx configuration
- [ ] SSL/HTTPS setup
- [ ] Environment variables for production
- [ ] Backup/restore automation

---

## 📊 MODEL CHECKLIST (15+ Models)

- [ ] User (extends AbstractUser)
- [ ] Category
- [ ] Ingredient
- [ ] IngredientBatch
- [ ] Product
- [ ] RecipeItem
- [ ] Sale
- [ ] SaleItem
- [ ] Discount
- [ ] ProductBatch
- [ ] ProductWastage
- [ ] IngredientWastage
- [ ] WastageReason
- [ ] ProductStockHistory
- [ ] IngredientStockHistory
- [ ] Notification
- [ ] NotificationReceipt

---

## ✅ ENDPOINTS CHECKLIST (50+ Endpoints)

**Authentication (5)**
- [ ] POST /api/auth/login/
- [ ] POST /api/auth/refresh/
- [ ] POST /api/auth/logout/
- [ ] GET /api/auth/me/
- [ ] GET /api/auth/verify/

**Users (5)**
- [ ] GET/POST /api/users/
- [ ] GET/PUT/DELETE /api/users/{id}/
- [ ] PATCH /api/users/{id}/status/

**Categories (2)**
- [ ] GET /api/categories/
- [ ] GET /api/categories/{id}/

**Ingredients (8)**
- [ ] GET/POST /api/ingredients/
- [ ] GET/PUT/DELETE /api/ingredients/{id}/
- [ ] GET /api/ingredients/low-stock/
- [ ] GET /api/ingredients/{id}/history/
- [ ] GET /api/ingredients/{id}/batches/

**Batches - Ingredient (5)**
- [ ] GET/POST /api/batches/
- [ ] GET/PUT/DELETE /api/batches/{id}/
- [ ] GET /api/batches/expiring/

**Products (6)**
- [ ] GET/POST /api/products/
- [ ] GET/PUT/DELETE /api/products/{id}/
- [ ] GET /api/products/low-stock/
- [ ] GET /api/products/{id}/recipe/

**Recipes (6)**
- [ ] GET /api/recipes/{product_id}/
- [ ] POST /api/recipes/{product_id}/items/
- [ ] PUT /api/recipes/{product_id}/items/{ingredient_id}/
- [ ] DELETE /api/recipes/{product_id}/items/{ingredient_id}/
- [ ] POST /api/recipes/validate/{product_id}/
- [ ] POST /api/recipes/batch-required/

**Discounts (5)**
- [ ] GET/POST /api/discounts/
- [ ] GET/PUT/DELETE /api/discounts/{id}/
- [ ] PATCH /api/discounts/{id}/toggle/
- [ ] GET /api/discounts/active/

**Sales (6)**
- [ ] GET/POST /api/sales/
- [ ] GET /api/sales/{bill_number}/
- [ ] GET /api/sales/date-range/
- [ ] GET /api/sales/analytics/
- [ ] GET /api/sales/by-cashier/

**Product Batches (4)**
- [ ] GET/POST /api/product-batches/
- [ ] GET/DELETE /api/product-batches/{id}/
- [ ] GET /api/product-batches/expiring/
- [ ] POST /api/product-batches/{id}/use/

**Wastage (8)**
- [ ] GET/POST /api/product-wastages/
- [ ] GET/DELETE /api/product-wastages/{id}/
- [ ] GET /api/product-wastages/analytics/
- [ ] GET/POST /api/ingredient-wastages/
- [ ] GET /api/ingredient-wastages/analytics/
- [ ] GET /api/wastage-reasons/

**Analytics (7)**
- [ ] GET /api/analytics/sales/daily/
- [ ] GET /api/analytics/sales/weekly/
- [ ] GET /api/analytics/sales/top-products/
- [ ] GET /api/analytics/inventory/stock-value/
- [ ] GET /api/analytics/wastage/summary/
- [ ] GET /api/dashboard/kpis/

**Notifications (3)**
- [ ] GET /api/notifications/
- [ ] PATCH /api/notifications/{id}/read/
- [ ] GET /api/notifications/unread/count/

---

## 🎯 ESTIMATED COMPLETION

| Phase | Component | Hours | Status |
|-------|-----------|-------|--------|
| 1 | Setup | 6 | Not Started |
| 2 | Auth | 9 | Not Started |
| 3 | Inventory | 16 | Not Started |
| 4 | Sales | 10 | Not Started |
| 5 | Wastage | 6 | Not Started |
| 6 | Audit | 3 | Not Started |
| 7 | Notifications | 4 | Not Started |
| 8 | Analytics | 8 | Not Started |
| 9 | Security | 7 | Not Started |
| 10 | Testing | 15 | Not Started |
| **TOTAL** | | **84 hours** | |

**Target Date:** 5-6 weeks from start

---

Last Updated: March 22, 2026
