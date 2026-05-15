# BakeryOS Backend API Specification

**Generated:** March 26, 2026  
**Source:** Django REST Framework API (Backend/api/)

## Overview

Complete API specification extracted from Django backend including serializers, models, field types, and response structures.

---

## Table of Contents

1. [User Management API](#user-management-api)
2. [Product Management API](#product-management-api)
3. [Category API](#category-api)
4. [Sale & Checkout API](#sale--checkout-api)
5. [Ingredient Management API](#ingredient-management-api)
6. [Batch Management API](#batch-management-api)
7. [Discount API](#discount-api)
8. [Data Type Reference](#data-type-reference)

---

## User Management API

### User Model Fields

| Field | Type | DB Type | Constraints | Notes |
|-------|------|---------|-------------|-------|
| `id` | Integer | AutoField | Primary Key | From AbstractUser |
| `username` | String | CharField(150) | Unique, Required | From AbstractUser |
| `email` | String | EmailField | Required | From AbstractUser |
| `password` | String | CharField(128) | Hashed, Write-only | From AbstractUser |
| `first_name` | String | CharField(150) | Optional | From AbstractUser |
| `last_name` | String | CharField(150) | Optional | From AbstractUser |
| `full_name` | String | CharField(255) | Required | Custom field |
| `employee_id` | String | CharField(50) | Unique, Optional | Auto-generated or manual |
| `nic` | String | CharField(50) | Optional | National ID |
| `contact` | String | CharField(20) | Optional | Phone number |
| `role` | String | CharField(50) | Choices | Manager, Cashier, Baker, Storekeeper |
| `status` | String | CharField(20) | Choices | active, inactive, suspended |
| `avatar_color` | String | CharField(20) | Default: 'blue' | UI indicator |
| `is_active` | Boolean | BooleanField | Default: True | From AbstractUser |
| `is_staff` | Boolean | BooleanField | Default: False | From AbstractUser |
| `is_superuser` | Boolean | BooleanField | Default: False | From AbstractUser |
| `last_login` | DateTime | DateTimeField | Nullable | From AbstractUser |
| `date_joined` | DateTime | DateTimeField | Auto | From AbstractUser |
| `created_at` | DateTime | DateTimeField(auto_now_add) | - | Custom field |
| `updated_at` | DateTime | DateTimeField(auto_now) | - | Custom field |

### Serializers

#### UserListSerializer
**Used for:** `GET /api/users/` (list view)

**Fields Returned (snake_case):**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@bakery.com",
  "full_name": "John Doe",
  "employee_id": "EMP001",
  "role": "Manager",
  "status": "active",
  "contact": "555-1234",
  "created_at": "2026-03-20T10:30:00Z",
  "updated_at": "2026-03-20T10:30:00Z"
}
```

**Read-only fields:** `id`, `employee_id`, `created_at`, `updated_at`  
**Excluded:** `password`, `is_staff`, `is_superuser`, `nic`, `avatar_color`, `last_login`

---

#### UserDetailSerializer
**Used for:** `GET /api/users/{id}/` (detail view)

**Fields Returned (snake_case):**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@bakery.com",
  "full_name": "John Doe",
  "employee_id": "EMP001",
  "nic": "123456789V",
  "contact": "555-1234",
  "role": "Manager",
  "status": "active",
  "avatar_color": "blue",
  "last_login": "2026-03-26T14:22:00Z",
  "is_active": true,
  "created_at": "2026-03-20T10:30:00Z",
  "updated_at": "2026-03-20T10:30:00Z"
}
```

**Read-only fields:** `id`, `employee_id`, `last_login`, `created_at`, `updated_at`  
**Excluded:** `password`, `is_staff`, `is_superuser`

---

#### UserCreateSerializer
**Used for:** `POST /api/users/` (create user - Manager only)

**Required Fields (POST body):**
```json
{
  "username": "jane_smith",
  "email": "jane@bakery.com",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!",
  "full_name": "Jane Smith",
  "contact": "555-5678",
  "nic": "987654321X",
  "role": "Cashier"
}
```

**Validation Rules:**
- `username`: Alphanumeric + underscore, 3-30 chars, unique
- `password`: Min 8 chars, must contain uppercase, lowercase, digits
- `password_confirm`: Must match `password`
- `email`: Valid format, unique
- `contact`: Valid phone number format
- `nic`: Format `9 digits + V/X` or `12 digits`
- `role`: One of (Manager, Cashier, Baker, Storekeeper)
- `full_name`: Min 2 chars

**Response:** 201 Created with UserDetailSerializer fields

---

#### UserUpdateSerializer
**Used for:** `PUT /api/users/{id}/`, `PATCH /api/users/{id}/`

**Updatable Fields:**
```json
{
  "email": "newemail@bakery.com",
  "full_name": "Jane Maria Smith",
  "nic": "987654321X",
  "contact": "555-9999",
  "avatar_color": "green"
}
```

**Notes:**
- Cannot update: `username`, `role`, `employee_id` (Manager only via special endpoint)
- Managers can update other users' fields
- Cashiers can only update their own profile

---

### User Endpoints

| Endpoint | Method | Permission | Pagination | Response |
|----------|--------|-----------|-----------|----------|
| `/api/users/` | GET | Manager | Yes (20/page) | UserListSerializer[] |
| `/api/users/` | POST | Manager | - | UserDetailSerializer |
| `/api/users/{id}/` | GET | Auth + Self/Manager | - | UserDetailSerializer |
| `/api/users/{id}/` | PUT | Auth + Self/Manager | - | UserDetailSerializer |
| `/api/users/{id}/` | PATCH | Auth + Self/Manager | - | UserDetailSerializer |
| `/api/users/{id}/` | DELETE | Manager | - | 204 No Content |

**Query Parameters (GET /api/users/):**
- `role`: Filter by role (Manager, Cashier, Baker, Storekeeper)
- `status`: Filter by status (active, inactive, suspended)
- `search`: Search by username, full_name, email, employee_id, contact
- `ordering`: Sort by id, username, created_at, full_name, employee_id
- `page`: Page number (default: 1)
- `page_size`: Results per page (default: 20, max: 100)

---

## Product Management API

### Product Model Fields

| Field | Type | DB Type | Constraints | Notes |
|-------|------|---------|-------------|-------|
| `id` | Integer | AutoField | Primary Key | - |
| `product_id` | String | CharField(50) | Unique, Indexed | Auto: #PROD-1001, #PROD-1002, etc. |
| `name` | String | CharField(100) | Required | Product name (e.g., "White Bread Loaf") |
| `description` | String | TextField | Optional | Product description |
| `image_url` | String | URLField | Optional | URL to product image |
| `category_id` | Integer | ForeignKey(Category) | Required | Reference to Product category |
| `cost_price` | Decimal | DecimalField(10,2) | Min 0.01 | Cost to produce per unit |
| `selling_price` | Decimal | DecimalField(10,2) | Min 0.01 | Selling price per unit |
| `current_stock` | Decimal | DecimalField(10,2) | Min 0 | Current quantity in stock |
| `shelf_life` | Integer | IntegerField | Min 1 | Duration until expiry |
| `shelf_unit` | String | CharField(20) | Choices | hours, days, weeks |
| `created_at` | DateTime | DateTimeField(auto_now_add) | - | - |
| `updated_at` | DateTime | DateTimeField(auto_now) | - | - |

### Serializers

#### ProductListSerializer
**Used for:** `GET /api/products/` (list view)

**Fields Returned (snake_case):**
```json
{
  "id": 1,
  "product_id": "#PROD-1001",
  "name": "White Bread Loaf",
  "category_id": 1,
  "category_name": "Bread",
  "cost_price": "2.50",
  "selling_price": "5.00",
  "profit_margin": 100.0,
  "current_stock": "15.50",
  "status": "in_stock",
  "shelf_life": 1,
  "shelf_unit": "days",
  "created_at": "2026-03-15T08:00:00Z"
}
```

**Type Notes:**
- `cost_price`, `selling_price`: Returned as **strings** (Decimal serialization)
- `profit_margin`: Float, calculated as `(selling_price - cost_price) / cost_price * 100`
- `current_stock`: String (Decimal)
- `status`: Computed property (in_stock, low_stock, out_of_stock)

**Read-only fields:** `product_id`, `created_at`

---

#### ProductDetailSerializer
**Used for:** `GET /api/products/{id}/` (detail view)

**Fields Returned (snake_case):**
```json
{
  "id": 1,
  "product_id": "#PROD-1001",
  "name": "White Bread Loaf",
  "description": "Fresh white bread loaf baked daily",
  "image_url": "https://example.com/products/bread.jpg",
  "category_id": 1,
  "category_name": "Bread",
  "category_type": "Product",
  "cost_price": "2.50",
  "selling_price": "5.00",
  "profit_margin": 100.0,
  "current_stock": "15.50",
  "status": "in_stock",
  "is_low_stock": false,
  "is_out_of_stock": false,
  "shelf_life": 1,
  "shelf_unit": "days",
  "created_at": "2026-03-15T08:00:00Z",
  "updated_at": "2026-03-15T08:00:00Z"
}
```

**Type Notes:**
- `profit_margin`: Float with 2 decimals
- `is_low_stock`, `is_out_of_stock`: Boolean (computed properties)
- All monetary fields: Strings (Decimal)

**Read-only fields:** `product_id`, `created_at`, `updated_at`

---

#### ProductCreateSerializer
**Used for:** `POST /api/products/` (create), `PUT/PATCH /api/products/{id}/` (update)

**Request Body:**
```json
{
  "category_id": 1,
  "name": "Chocolate Cake",
  "description": "Rich chocolate layer cake",
  "image_url": "https://example.com/cake.jpg",
  "cost_price": "8.00",
  "selling_price": "15.00",
  "current_stock": "5.00",
  "shelf_life": 2,
  "shelf_unit": "days"
}
```

**Validation Rules:**
- `name`: Non-empty, 2-255 chars, unique per category, sanitized HTML
- `cost_price`: Must be > 0, max 2 decimal places
- `selling_price`: Must be > cost_price, max 2 decimal places
- `current_stock`: Must be >= 0, max 2 decimal places
- `shelf_life`: Must be > 0
- `category_id`: Must be Product-type category

**Response:** 201 Created or 200 OK with ProductDetailSerializer fields

---

### Product Endpoints

| Endpoint | Method | Permission | Pagination | Response |
|----------|--------|-----------|-----------|----------|
| `/api/products/` | GET | Auth | Yes (20/page) | ProductListSerializer[] |
| `/api/products/` | POST | Manager | - | ProductDetailSerializer |
| `/api/products/{id}/` | GET | Auth | - | ProductDetailSerializer |
| `/api/products/{id}/` | PUT | Manager | - | ProductDetailSerializer |
| `/api/products/{id}/` | PATCH | Manager | - | ProductDetailSerializer |
| `/api/products/{id}/` | DELETE | Manager | - | 204 No Content |

**Query Parameters (GET /api/products/):**
- `category_id`: Filter by category (integer FK)
- `search`: Search by product_id, name, category__name
- `ordering`: Sort by selling_price, current_stock, name, created_at
- `page`: Page number
- `page_size`: Results per page (default: 20, max: 100)

---

## Category API

### Category Model Fields

| Field | Type | DB Type | Constraints | Notes |
|-------|------|---------|-------------|-------|
| `id` | Integer | AutoField | Primary Key | - |
| `category_id` | String | CharField(50) | Unique, Auto | CAT-P001 (Product) or CAT-I001 (Ingredient) |
| `name` | String | CharField(100) | Required | Category name |
| `type` | String | CharField(20) | Choices | Product or Ingredient |
| `description` | String | TextField | Optional | - |
| `created_at` | DateTime | DateTimeField(auto_now_add) | - | - |
| `updated_at` | DateTime | DateTimeField(auto_now) | - | - |

**Unique Constraint:** `(type, name)` - Cannot have duplicate names within same type

### Serializers

#### CategoryListSerializer
**Used for:** `GET /api/categories/`

**Fields Returned (snake_case):**
```json
{
  "id": 1,
  "category_id": "CAT-P001",
  "name": "Bread",
  "type": "Product",
  "description": "Bread products including loaves and rolls",
  "created_at": "2026-03-10T09:00:00Z",
  "updated_at": "2026-03-10T09:00:00Z"
}
```

**Read-only fields:** `id`, `category_id`, `created_at`, `updated_at`

---

#### CategoryDetailSerializer
**Used for:** `GET /api/categories/{id}/`

**Fields Returned (snake_case):**
```json
{
  "id": 1,
  "category_id": "CAT-P001",
  "name": "Bread",
  "type": "Product",
  "description": "Bread products including loaves and rolls",
  "item_count": 12,
  "created_at": "2026-03-10T09:00:00Z",
  "updated_at": "2026-03-10T09:00:00Z"
}
```

**Computed Fields:**
- `item_count`: Count of products/ingredients in this category

---

#### CategoryCreateSerializer
**Used for:** `POST /api/categories/`

**Request Body:**
```json
{
  "name": "Cakes",
  "type": "Product",
  "description": "Premium cakes and pastries"
}
```

**Validation Rules:**
- `name`: Non-empty, trim, not duplicate with same type
- `type`: Must be "Product" or "Ingredient"

---

### Category Endpoints

| Endpoint | Method | Permission | Response |
|----------|--------|-----------|----------|
| `/api/categories/` | GET | Auth | CategoryListSerializer[] |
| `/api/categories/` | POST | Manager | CategoryDetailSerializer |
| `/api/categories/{id}/` | GET | Auth | CategoryDetailSerializer |
| `/api/categories/{id}/` | PUT | Manager | CategoryDetailSerializer |
| `/api/categories/{id}/` | DELETE | Manager | 204 No Content |

---

## Sale & Checkout API

### Sale Model Fields

| Field | Type | DB Type | Constraints | Notes |
|-------|------|---------|-------------|-------|
| `id` | Integer | AutoField | Primary Key | - |
| `bill_number` | String | CharField(50) | Unique, Indexed | Auto: BILL-1001, BILL-1002 |
| `cashier_id` | Integer | ForeignKey(User) | Required | User who processed sale |
| `discount_id` | Integer | ForeignKey(Discount) | Nullable | Optional discount |
| `subtotal` | Decimal | DecimalField(12,2) | Min 0 | Sum of items (before discount) |
| `discount_amount` | Decimal | DecimalField(12,2) | Min 0 | Discount amount applied |
| `total_amount` | Decimal | DecimalField(12,2) | Min 0 | Final amount (after discount) |
| `payment_method` | String | CharField(20) | Choices | Cash, Card, Mobile, Cheque, Other |
| `notes` | String | TextField | Optional | Additional notes |
| `date_time` | DateTime | DateTimeField | Indexed | When sale was made |
| `created_at` | DateTime | DateTimeField(auto_now_add) | - | - |
| `updated_at` | DateTime | DateTimeField(auto_now) | - | - |

### SaleItem Model Fields

| Field | Type | DB Type | Constraints | Notes |
|-------|------|---------|-------------|-------|
| `id` | Integer | AutoField | Primary Key | - |
| `sale_id` | Integer | ForeignKey(Sale) | Required | Parent sale |
| `product_id` | Integer | ForeignKey(Product) | Required | Product sold |
| `quantity` | Decimal | DecimalField(10,2) | > 0 | Units sold |
| `unit_price` | Decimal | DecimalField(10,2) | > 0 | Price per unit (frozen) |
| `subtotal` | Decimal | DecimalField(12,2) | - | quantity × unit_price |
| `created_at` | DateTime | DateTimeField(auto_now_add) | - | - |

### Serializers

#### SaleListSerializer
**Used for:** `GET /api/sales/` (list view)

**Fields Returned (snake_case):**
```json
{
  "id": 1,
  "bill_number": "BILL-1001",
  "cashier_id": 5,
  "cashier_name": "John Smith",
  "subtotal": "45.50",
  "discount_id": 2,
  "discount_name": "Weekend 10%",
  "discount_amount": "4.55",
  "total_amount": "40.95",
  "payment_method": "Cash",
  "item_count": 3,
  "date_time": "2026-03-26T14:30:00Z",
  "created_at": "2026-03-26T14:30:00Z"
}
```

**Type Notes:**
- Monetary fields: Strings (Decimal)
- `item_count`: Integer (computed)
- All fields read-only

---

#### SaleDetailSerializer
**Used for:** `GET /api/sales/{id}/` (detail view with items)

**Fields Returned (snake_case):**
```json
{
  "id": 1,
  "bill_number": "BILL-1001",
  "cashier_id": 5,
  "cashier_name": "John Smith",
  "subtotal": "45.50",
  "discount_id": 2,
  "discount_name": "Weekend 10%",
  "discount_type": "percentage",
  "discount_value": "10.00",
  "discount_amount": "4.55",
  "total_amount": "40.95",
  "payment_method": "Cash",
  "notes": "VIP customer",
  "item_count": 3,
  "items": [
    {
      "id": 10,
      "product_id": 1,
      "product_id_val": 1,
      "product_name": "White Bread Loaf",
      "quantity": "2.00",
      "unit_price": "5.00",
      "subtotal": "10.00",
      "created_at": "2026-03-26T14:30:00Z"
    },
    {
      "id": 11,
      "product_id": 3,
      "product_id_val": 3,
      "product_name": "Chocolate Cake",
      "quantity": "1.00",
      "unit_price": "15.00",
      "subtotal": "15.00",
      "created_at": "2026-03-26T14:30:00Z"
    }
  ],
  "date_time": "2026-03-26T14:30:00Z",
  "created_at": "2026-03-26T14:30:00Z",
  "updated_at": "2026-03-26T14:30:00Z"
}
```

---

#### SaleCreateSerializer
**Used for:** `POST /api/sales/` (checkout endpoint)

**Request Body:**
```json
{
  "discount_id": 2,
  "items": [
    {
      "product_id": 1,
      "quantity": "2.00",
      "unit_price": "5.00"
    },
    {
      "product_id": 3,
      "quantity": "1.00",
      "unit_price": "15.00"
    }
  ],
  "payment_method": "Cash",
  "notes": "VIP customer"
}
```

**Validation Rules:**
- `items`: Non-empty array, max 100 items
- `quantity`: Must be > 0
- `unit_price`: Must be > 0
- `product_id`: Must exist
- `discount_id`: Must exist and be active (if provided)
- `payment_method`: One of (Cash, Card, Mobile, Cheque, Other)

**Response:** 201 Created with SaleDetailSerializer fields (including items)

---

#### SaleItemSerializer
**Used for:** Nested in SaleDetailSerializer

**Fields Returned (snake_case):**
```json
{
  "id": 10,
  "product_id": 1,
  "product_id_val": 1,
  "product_name": "White Bread Loaf",
  "quantity": "2.00",
  "unit_price": "5.00",
  "subtotal": "10.00",
  "created_at": "2026-03-26T14:30:00Z"
}
```

**Type Notes:**
- Monetary and quantity fields: Strings (Decimal)
- `product_id_val`: Integer (duplicate of product_id for clarity)
- `subtotal`: Read-only (auto-calculated)

---

### Sale Endpoints

| Endpoint | Method | Permission | Pagination | Response |
|----------|--------|-----------|-----------|----------|
| `/api/sales/` | GET | Cashier/Manager | Yes (20/page) | SaleListSerializer[] |
| `/api/sales/` | POST | Cashier/Manager | - | SaleDetailSerializer |
| `/api/sales/{id}/` | GET | Cashier/Manager | - | SaleDetailSerializer |

**Query Parameters (GET /api/sales/):**
- `start_date`: Filter by date (YYYY-MM-DD format)
- `end_date`: Filter by date (YYYY-MM-DD format)
- `payment_method`: Filter by payment method
- `cashier_id`: Filter by cashier (Manager only)
- `page`: Page number
- `page_size`: Results per page

**Notes:**
- Cashiers can only see their own sales
- Managers can see all sales

---

## Ingredient Management API

### Ingredient Model Fields

| Field | Type | DB Type | Constraints | Notes |
|-------|------|---------|-------------|-------|
| `id` | Integer | AutoField | Primary Key | - |
| `ingredient_id` | String | CharField(50) | Unique, Auto | Format: #I001, #I002 |
| `name` | String | CharField(100) | Required | Ingredient name |
| `category_id` | Integer | ForeignKey(Category) | Required | Ingredient-type category |
| `supplier` | String | CharField(100) | Optional | Supplier company name |
| `supplier_contact` | String | CharField(100) | Optional | Supplier phone/email |
| `tracking_type` | String | CharField(20) | Choices | Weight, Volume, Count |
| `base_unit` | String | CharField(20) | Required | e.g., kg, liters, pieces |
| `total_quantity` | Decimal | DecimalField(10,2) | Min 0 | Synced from batches (READ-ONLY) |
| `low_stock_threshold` | Decimal | DecimalField(10,2) | Default 10 | Alert threshold |
| `shelf_life` | Integer | IntegerField | - | How long ingredient lasts |
| `shelf_unit` | String | CharField(20) | Choices | days, weeks, months, years |
| `is_active` | Boolean | BooleanField | Default True | - |
| `created_at` | DateTime | DateTimeField(auto_now_add) | - | - |
| `updated_at` | DateTime | DateTimeField(auto_now) | - | - |

### Serializers

#### IngredientListSerializer
**Used for:** `GET /api/ingredients/`

**Fields Returned (snake_case):**
```json
{
  "id": 1,
  "ingredient_id": "#I001",
  "name": "All Purpose Flour",
  "category_id": 10,
  "category_name": "Flour",
  "tracking_type": "Weight",
  "base_unit": "kg",
  "total_quantity": "25.50",
  "low_stock_threshold": "10.00",
  "stock_status": "in_stock",
  "is_active": true,
  "created_at": "2026-03-01T08:00:00Z"
}
```

**Type Notes:**
- `total_quantity`, `low_stock_threshold`: Strings (Decimal)
- `stock_status`: Computed property string
- Read-only fields: `id`, `ingredient_id`, `total_quantity`, `stock_status`, `created_at`

---

#### IngredientDetailSerializer
**Used for:** `GET /api/ingredients/{id}/`

**Fields Returned (snake_case):**
```json
{
  "id": 1,
  "ingredient_id": "#I001",
  "name": "All Purpose Flour",
  "category_id": 10,
  "category_name": "Flour",
  "supplier": "Golden Grain Co.",
  "supplier_contact": "555-1111",
  "tracking_type": "Weight",
  "base_unit": "kg",
  "total_quantity": "25.50",
  "low_stock_threshold": "10.00",
  "shelf_life": 6,
  "shelf_unit": "months",
  "shelf_life_display": "6 months",
  "stock_status": "in_stock",
  "is_low_stock": false,
  "is_out_of_stock": false,
  "batch_count": 3,
  "is_active": true,
  "created_at": "2026-03-01T08:00:00Z",
  "updated_at": "2026-03-01T08:00:00Z"
}
```

**Computed Fields:**
- `is_low_stock`: Boolean
- `is_out_of_stock`: Boolean
- `batch_count`: Integer
- `shelf_life_display`: Formatted string

---

#### IngredientCreateSerializer
**Used for:** `POST /api/ingredients/`

**Request Body:**
```json
{
  "name": "Granulated Sugar",
  "category_id": 11,
  "supplier": "Sweet Suppliers Ltd",
  "supplier_contact": "555-2222",
  "tracking_type": "Weight",
  "base_unit": "kg",
  "low_stock_threshold": "5.00",
  "shelf_life": 12,
  "shelf_unit": "months"
}
```

**Validation Rules:**
- `name`: Non-empty, 2-100 chars, trimmed
- `category_id`: Must be Ingredient-type category
- `base_unit`: Non-empty
- `tracking_type`: One of (Weight, Volume, Count)
- `shelf_life`: Must be > 0 (if provided)

---

### Ingredient Endpoints

| Endpoint | Method | Permission | Pagination | Response |
|----------|--------|-----------|-----------|----------|
| `/api/ingredients/` | GET | Auth | Yes (20/page) | IngredientListSerializer[] |
| `/api/ingredients/` | POST | Manager | - | IngredientDetailSerializer |
| `/api/ingredients/{id}/` | GET | Auth | - | IngredientDetailSerializer |
| `/api/ingredients/{id}/` | PUT | Manager | - | IngredientDetailSerializer |
| `/api/ingredients/{id}/` | DELETE | Manager | - | 204 No Content |

---

## Batch Management API

### IngredientBatch Model Fields

| Field | Type | DB Type | Constraints | Notes |
|-------|------|---------|-------------|-------|
| `id` | Integer | AutoField | Primary Key | - |
| `batch_id` | String | CharField(50) | Unique, Auto | Format: BATCH-1001 |
| `ingredient_id` | Integer | ForeignKey(Ingredient) | Required | Source ingredient |
| `quantity` | Decimal | DecimalField(10,2) | > 0 | Total received |
| `current_qty` | Decimal | DecimalField(10,2) | >= 0 | Remaining in batch |
| `cost_price` | Decimal | DecimalField(10,2) | Optional | Cost per unit |
| `made_date` | DateTime | DateTimeField | Default now | Date batch received |
| `expire_date` | DateTime | DateTimeField | Required | Expiry date |
| `status` | String | CharField(20) | Choices | Active, Expired, Used |
| `created_at` | DateTime | DateTimeField(auto_now_add) | - | - |
| `updated_at` | DateTime | DateTimeField(auto_now) | - | - |

### Serializers

#### BatchListSerializer
**Used for:** `GET /api/batches/`

**Fields Returned (snake_case):**
```json
{
  "id": 1,
  "batch_id": "BATCH-1001",
  "ingredient_id": 1,
  "ingredient_name": "All Purpose Flour",
  "ingredient_unit": "kg",
  "quantity": "50.00",
  "current_qty": "45.00",
  "made_date": "2026-03-20T10:00:00Z",
  "expire_date": "2026-09-20T10:00:00Z",
  "status": "Active",
  "is_expired": false,
  "days_until_expiry": 178,
  "created_at": "2026-03-20T10:00:00Z"
}
```

**Type Notes:**
- `quantity`, `current_qty`: Strings (Decimal)
- `is_expired`: Boolean (computed)
- `days_until_expiry`: Integer (computed)

---

#### BatchDetailSerializer
**Used for:** `GET /api/batches/{id}/`

**Fields Returned (snake_case):**
```json
{
  "id": 1,
  "batch_id": "BATCH-1001",
  "ingredient_id": 1,
  "ingredient_name": "All Purpose Flour",
  "ingredient_unit": "kg",
  "ingredient_tracking": "Weight",
  "quantity": "50.00",
  "current_qty": "45.00",
  "remaining_qty": "45.00",
  "cost_price": "0.80",
  "total_cost": "40.00",
  "made_date": "2026-03-20T10:00:00Z",
  "expire_date": "2026-09-20T10:00:00Z",
  "status": "Active",
  "is_expired": false,
  "days_until_expiry": 178,
  "expiry_progress": 45.5,
  "created_at": "2026-03-20T10:00:00Z",
  "updated_at": "2026-03-20T10:00:00Z"
}
```

**Computed Fields:**
- `remaining_qty`: Alias for `current_qty`
- `total_cost`: Calculated from `cost_price × quantity`
- `expiry_progress`: Percentage (0-100)

---

#### BatchCreateSerializer
**Used for:** `POST /api/batches/`

**Request Body:**
```json
{
  "ingredient_id": 1,
  "quantity": "50.00",
  "current_qty": "50.00",
  "cost_price": "0.80",
  "made_date": "2026-03-20T10:00:00Z",
  "expire_date": "2026-09-20T10:00:00Z"
}
```

**Validation Rules:**
- `quantity`: Must be > 0
- `current_qty`: Must be >= 0 and <= quantity
- `cost_price`: Must be > 0 or null
- `expire_date`: Must be >= made_date
- If `current_qty` not provided, defaults to `quantity`

---

### Batch Endpoints

| Endpoint | Method | Permission | Pagination | Response |
|----------|--------|-----------|-----------|----------|
| `/api/batches/` | GET | Auth | Yes (20/page) | BatchListSerializer[] |
| `/api/batches/` | POST | Manager/Storekeeper | - | BatchDetailSerializer |
| `/api/batches/{id}/` | GET | Auth | - | BatchDetailSerializer |
| `/api/batches/{id}/` | PUT | Manager/Storekeeper | - | BatchDetailSerializer |
| `/api/batches/{id}/consume/` | POST | Storekeeper | - | BatchDetailSerializer |

---

## Discount API

### Discount Model Fields (Reference)

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `discount_id` | String | Unique, Auto | Format: DISC-001 |
| `name` | String | Required | Discount name |
| `discount_type` | String | Choices | percentage, fixed_amount |
| `value` | Decimal | > 0 | Discount % or amount |
| `applicable_to` | String | Choices | sale, category, product |
| `target_category_id` | Integer | Nullable FK | If applicable_to='category' |
| `target_product_id` | Integer | Nullable FK | If applicable_to='product' |
| `start_date` | DateTime | - | When discount starts |
| `end_date` | DateTime | - | When discount ends |
| `is_active` | Boolean | Default True | - |

### Serializers

#### DiscountListSerializer
**Used for:** `GET /api/discounts/`

**Fields Returned (snake_case):**
```json
{
  "id": 1,
  "discount_id": "DISC-001",
  "name": "Weekend 10%",
  "discount_type": "percentage",
  "value": "10.00",
  "applicable_to": "sale",
  "target_category_id": null,
  "target_category_name": null,
  "target_product_id": null,
  "target_product_name": null,
  "start_date": "2026-03-22T00:00:00Z",
  "end_date": "2026-03-28T23:59:59Z",
  "is_active": true,
  "created_at": "2026-03-15T08:00:00Z"
}
```

---

#### DiscountDetailSerializer
**Used for:** `GET /api/discounts/{id}/`

**Fields Returned (snake_case):**
```json
{
  "id": 1,
  "discount_id": "DISC-001",
  "name": "Weekend 10%",
  "description": "10% off all sales during weekends",
  "discount_type": "percentage",
  "value": "10.00",
  "applicable_to": "sale",
  "target_category_id": null,
  "target_category": null,
  "target_product_id": null,
  "target_product": null,
  "start_date": "2026-03-22T00:00:00Z",
  "end_date": "2026-03-28T23:59:59Z",
  "start_time": "00:00:00",
  "end_time": "23:59:59",
  "is_active": true,
  "is_applicable_now": true,
  "created_at": "2026-03-15T08:00:00Z",
  "updated_at": "2026-03-15T08:00:00Z"
}
```

**Nested Objects:**
```json
"target_category": {
  "id": 1,
  "category_id": "CAT-P001",
  "name": "Bread"
}

"target_product": {
  "id": 3,
  "product_id": "#PROD-1003",
  "name": "Chocolate Cake",
  "selling_price": "15.00"
}
```

---

## Data Type Reference

### Field Serialization Rules

#### DecimalField (monetary, quantities)
**Django Type:** `models.DecimalField(max_digits=N, decimal_places=2)`  
**Serialized As:** **String** in JSON  
**Example:** `"45.50"` (not `45.50`)

**Reason:** Prevents float precision issues with money  
**Frontend Handling:** Parse as string, convert to number for calculations, format for display

---

#### DateTimeField
**Django Type:** `models.DateTimeField`  
**Serialized As:** ISO 8601 string (with timezone)  
**Format:** `"2026-03-26T14:30:00Z"` (UTC)  
**Example:**
```json
"date_time": "2026-03-26T14:30:00Z",
"created_at": "2026-03-26T14:30:00Z",
"updated_at": "2026-03-26T14:30:00Z"
```

---

#### BooleanField
**Django Type:** `models.BooleanField`  
**Serialized As:** Boolean  
**Example:**
```json
"is_active": true,
"is_low_stock": false,
"is_expired": true
```

---

#### CharField / TextField
**Django Type:** `models.CharField()`, `models.TextField()`  
**Serialized As:** String  
**Example:**
```json
"username": "john_doe",
"description": "Product description text",
"status": "active"
```

---

#### IntegerField
**Django Type:** `models.IntegerField()`  
**Serialized As:** Integer (no quotes)  
**Example:**
```json
"id": 1,
"shelf_life": 2,
"batch_count": 3,
"days_until_expiry": 178
```

---

#### ForeignKey (to another model)
**Django Type:** `models.ForeignKey(OtherModel, ...)`  
**Serialized As:** Integer (primary key)  
**Example:**
```json
"product_id": 1,
"cashier_id": 5,
"category_id": 10
```

**Related Data:** If needed, use SerializerMethodField to embed details:
```json
"cashier_name": "John Smith",
"category_name": "Bread",
"product_name": "White Bread Loaf"
```

---

#### Computed/SerializerMethodField
**Serialized As:** Type depends on field implementation  
**Examples:**
```json
"profit_margin": 100.0,        // Float
"item_count": 3,                // Integer
"stock_status": "in_stock",    // String
"is_low_stock": false,         // Boolean
"total_cost": "40.00"          // String (Decimal)
```

---

### Pagination Structure

**Default Pagination:** `PageNumberPagination` with 20 items per page

**Response Format:**
```json
{
  "count": 150,
  "next": "http://api.example.com/api/users/?page=2",
  "previous": null,
  "results": [
    { /* item 1 */ },
    { /* item 2 */ }
  ]
}
```

**Query Parameters:**
- `page`: Page number (default: 1)
- `page_size`: Items per page (default: 20, max: 100)

---

### Error Response Format

**HTTP 400 Bad Request:**
```json
{
  "error": "Validation error message",
  "field_name": ["Error for this field", "Another error"]
}
```

**HTTP 401 Unauthorized:**
```json
{
  "detail": "Authentication credentials were not provided."
}
```

**HTTP 403 Forbidden:**
```json
{
  "detail": "You do not have permission to perform this action."
}
```

**HTTP 404 Not Found:**
```json
{
  "detail": "Not found."
}
```

---

## Summary

### Field Naming Convention
- **All fields use snake_case** (e.g., `full_name`, `product_id`, `created_at`)
- No camelCase in API responses
- Underscores for multi-word fields

### Key Serialization Points

1. **Decimal Fields (money/quantities):**
   - Always returned as **strings**
   - Prevent precision loss
   - Examples: `"45.50"`, `"2.00"`, `"10.00"`

2. **DateTime Fields:**
   - ISO 8601 format with Z (UTC)
   - Examples: `"2026-03-26T14:30:00Z"`

3. **Boolean Fields:**
   - True/false (lowercase)
   - Examples: `true`, `false`

4. **Computed Fields:**
   - Use `SerializerMethodField()`
   - Calculated at serialization time
   - Examples: `profit_margin`, `item_count`, `is_expired`

5. **Foreign Keys:**
   - Returned as integers (primary keys)
   - Related names embedded separately
   - Examples: `category_id: 1`, `category_name: "Bread"`

---

## Quick Reference: Field Mapping

| Django Field Type | JSON Type | Example | Notes |
|------------------|-----------|---------|-------|
| AutoField (id) | integer | `1` | Primary key |
| CharField | string | `"flour"` | Text |
| TextField | string | `"description"` | Long text |
| IntegerField | integer | `5` | Whole number |
| DecimalField | string | `"45.50"` | **Money/quantity** |
| BooleanField | boolean | `true` | True/false |
| DateTimeField | string (ISO) | `"2026-03-26T14:30:00Z"` | UTC datetime |
| ForeignKey | integer | `1` | Reference ID |
| SerializerMethodField | varies | varies | Computed value |
| Choice Field | string | `"active"` | From choices |

---

## Document Version

- **Generated:** March 26, 2026
- **Based on:** Backend/api/ Django structure
- **Serializers analyzed:** 18 files
- **Models analyzed:** 14 files
- **Views analyzed:** 15 files
- **Status:** Complete extraction

