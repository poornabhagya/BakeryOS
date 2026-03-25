# Task 3.4 - Product Model - Complete Testing Guide

**Status:** ✅ All Endpoints Implemented & Ready for Testing  
**Last Updated:** March 23, 2026  
**Database:** 20 seed products loaded (4 per category × 5 categories)  
**Auto-ID Format:** #PROD-1001, #PROD-1002, etc.

---

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [API Overview](#api-overview)
3. [Product Model Details](#product-model-details)
4. [Endpoint Testing Guide](#endpoint-testing-guide)
5. [Test Cases](#test-cases)
6. [Database Verification](#database-verification)
7. [Profit Margin Calculation](#profit-margin-calculation)
8. [Troubleshooting](#troubleshooting)

---

## Quick Start

### Prerequisites
- Django server running on `http://localhost:8000`
- Category seed data loaded (Task 3.1) ✅
- Ingredient seed data loaded (Task 3.2) ✅
- Batch seed data loaded (Task 3.3) ✅
- Product seed data loaded (this task)
- Valid authentication token (Manager has full access, others read-only)

### Load Seed Products
```bash
cd Backend
.\venv\Scripts\activate
python manage.py seed_products
```

**Expected Output:**
```
Starting product seed data load...
  #PROD-1001: Burger Bun          - Cost: Rs.15.00, Sell: Rs.25.00, Margin: 66.7%, Stock: 50
  #PROD-1002: Hot Dog Bun         - Cost: Rs.12.00, Sell: Rs.20.00, Margin: 66.7%, Stock: 45
  ...
  
✓ Successfully created 20 products

Product Summary:
  Buns: 4 products
  Bread: 4 products
  Cakes: 4 products
  Pastries: 4 products
  Drinks: 4 products

Stock Summary:
  Total Stock Value: 650 units
  Low Stock Items (<10): 0
  Out of Stock: 0
```

### Run All Tests
```bash
python test_products_endpoints.py
```

**Expected Results:** ✅ All 15+ tests pass

---

## API Overview

### Base URL
```
http://localhost:8000/api
```

### Available Endpoints

| # | Method | Endpoint | Purpose | Auth | Permissions |
|---|--------|----------|---------|------|-------------|
| 1 | GET | `/products/` | List products (paginated, filtered) | Yes | Any |
| 2 | POST | `/products/` | Create new product | Yes | Manager |
| 3 | GET | `/products/{id}/` | Get product details | Yes | Any |
| 4 | PUT | `/products/{id}/` | Full update | Yes | Manager |
| 5 | PATCH | `/products/{id}/` | Partial update | Yes | Manager |
| 6 | DELETE | `/products/{id}/` | Delete product | Yes | Manager |
| 7 | GET | `/products/low-stock/` | Products with <10 units | Yes | Any |
| 8 | GET | `/products/out-of-stock/` | Products with 0 quantity | Yes | Any |
| 9 | GET | `/products/by-category/{id}/` | Products in category | Yes | Any |
| 10 | GET | `/products/{id}/recipe/` | Product recipe (future) | Yes | Any |

---

## Product Model Details

### Fields

| Field | Type | Required | Notes |
|-------|------|----------|-------|
| **product_id** | CharField | Auto | #PROD-1001, #PROD-1002 format |
| **category_id** | FK → Category | Yes | Must reference Product category |
| **name** | CharField | Yes | Unique per category |
| **description** | TextField | No | Product details for display |
| **image_url** | URLField | No | Product image URL |
| **cost_price** | DecimalField | Yes | Production cost per unit, > 0 |
| **selling_price** | DecimalField | Yes | Retail price, must be > cost_price |
| **current_stock** | DecimalField | Yes | Quantity in stock (0-∞) |
| **shelf_life** | IntegerField | Yes | How long product lasts (≥ 1) |
| **shelf_unit** | Choice | Yes | hours, days, weeks |
| **created_at** | DateTime | Auto | Creation timestamp |
| **updated_at** | DateTime | Auto | Last update timestamp |

### Status Values (Computed Property)
```
available  → current_stock >= 10
low_stock  → 0 < current_stock < 10
out_of_stock → current_stock <= 0
```

### Computed Properties

| Property | Description | Returns |
|----------|-------------|---------|
| `profit_margin` | % profit from retail price | decimal (%) |
| `is_low_stock` | Stock below 10 units | boolean |
| `is_out_of_stock` | No stock remaining | boolean |
| `status` | Stock status string | 'available', 'low_stock', 'out_of_stock' |

**Profit Margin Formula:**
```
profit_margin = (selling_price - cost_price) / cost_price × 100
```

Example: Burger Bun
- Cost: Rs. 15.00
- Selling: Rs. 25.00
- Margin: (25 - 15) / 15 × 100 = **66.67%**

---

## Endpoint Testing Guide

### ✅ TEST 1: List All Products
**Endpoint:** `GET /api/products/`  
**Auth:** Required  
**Response:** Paginated list with products ordered by creation date (newest first)

**Using curl:**
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/products/
```

**Expected Response (200 OK):**
```json
{
  "count": 20,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "product_id": "#PROD-1001",
      "name": "Burger Bun",
      "category_id": 1,
      "category_name": "Buns",
      "cost_price": "15.00",
      "selling_price": "25.00",
      "profit_margin": 66.67,
      "current_stock": "50.00",
      "status": "available",
      "shelf_life": 2,
      "shelf_unit": "days",
      "created_at": "2026-03-23T10:00:00Z"
    },
    ...
  ]
}
```

**Query Parameters:**
```bash
# Filter by category
?category_id=1

# Filter by status
?status=available
?status=low_stock
?status=out_of_stock

# Search by name or product_id
?search=Bread
?search=#PROD-1001

# Sort by price (ascending)
?ordering=selling_price

# Sort by price (descending)
?ordering=-selling_price

# Sort by margin
?ordering=profit_margin,-profit_margin

# Pagination
?page=1
?page_size=10
```

**Test Status:** ✅ PASSED (Retrieved 20 products)

---

### ✅ TEST 2: Get Product Details
**Endpoint:** `GET /api/products/{id}/`  
**Auth:** Required  
**Parameter:** product ID (numeric pk, not product_id)

**Using curl:**
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/products/1/
```

**Expected Response (200 OK):**
```json
{
  "id": 1,
  "product_id": "#PROD-1001",
  "name": "Burger Bun",
  "description": "Classic burger buns, fresh daily",
  "image_url": null,
  "category_id": 1,
  "category_name": "Buns",
  "category_type": "Product",
  "cost_price": "15.00",
  "selling_price": "25.00",
  "profit_margin": 66.67,
  "current_stock": "50.00",
  "status": "available",
  "is_low_stock": false,
  "is_out_of_stock": false,
  "shelf_life": 2,
  "shelf_unit": "days",
  "created_at": "2026-03-23T10:00:00Z",
  "updated_at": "2026-03-23T10:00:00Z"
}
```

**Calculated Fields:**
- `profit_margin` - Percentage profit
- `status` - Stock status (available/low_stock/out_of_stock)
- `is_low_stock` - Boolean flag
- `is_out_of_stock` - Boolean flag
- `category_name` - Category name (from FK)

**Test Status:** ✅ PASSED

---

### ✅ TEST 3: Create New Product
**Endpoint:** `POST /api/products/`  
**Auth:** Required  
**Permission:** Manager only  
**Method:** HTTP POST with JSON body

**Using curl:**
```bash
curl -X POST http://localhost:8000/api/products/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "category_id": 1,
    "name": "Sesame Bun",
    "description": "Burger bun with sesame seeds",
    "cost_price": "16.00",
    "selling_price": "28.00",
    "current_stock": "30",
    "shelf_life": 2,
    "shelf_unit": "days"
  }'
```

**Request Fields:**
```json
{
  "category_id": 1,              // Required, FK to Product category
  "name": "Sesame Bun",          // Required, unique per category
  "description": "...",          // Optional
  "image_url": "https://...",    // Optional, must be valid URL
  "cost_price": "16.00",         // Required, > 0
  "selling_price": "28.00",      // Required, > cost_price
  "current_stock": "30",         // Optional, defaults to 0, ≥ 0
  "shelf_life": 2,               // Required, ≥ 1
  "shelf_unit": "days"           // Required, one of: hours, days, weeks
}
```

**Expected Response (201 Created):**
```json
{
  "id": 21,
  "product_id": "#PROD-1021",
  "name": "Sesame Bun",
  "description": "Burger bun with sesame seeds",
  "image_url": null,
  "category_id": 1,
  "category_name": "Buns",
  "cost_price": "16.00",
  "selling_price": "28.00",
  "profit_margin": 75.0,
  "current_stock": "30.00",
  "status": "available",
  "is_low_stock": false,
  "is_out_of_stock": false,
  "shelf_life": 2,
  "shelf_unit": "days",
  "created_at": "2026-03-23T11:00:00Z",
  "updated_at": "2026-03-23T11:00:00Z"
}
```

**Test Status:** ✅ PASSED (Product created with auto-ID)

**Validation Rules:**
```
✓ category_id: Must reference Product-type category, required
✓ name: Max 100 chars, required, unique with category
✓ cost_price: > 0, required
✓ selling_price: > cost_price, required
✓ shelf_life: ≥ 1, required
✓ current_stock: ≥ 0, optional (defaults to 0)
```

---

### ✅ TEST 4: Update Product
**Endpoint:** `PATCH /api/products/{id}/`  
**Auth:** Required  
**Permission:** Manager only  
**Method:** HTTP PATCH for partial update, PUT for full update

**Using curl (PATCH):**
```bash
curl -X PATCH http://localhost:8000/api/products/1/ \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "current_stock": "60",
    "selling_price": "26.00"
  }'
```

**Expected Response (200 OK):**
```json
{
  "id": 1,
  "product_id": "#PROD-1001",
  "name": "Burger Bun",
  "category_id": 1,
  "cost_price": "15.00",
  "selling_price": "26.00",
  "profit_margin": 73.33,
  "current_stock": "60.00",
  "status": "available",
  ...
}
```

**Test Status:** ✅ PASSED

---

### ✅ TEST 5: Delete Product
**Endpoint:** `DELETE /api/products/{id}/`  
**Auth:** Required  
**Permission:** Manager only  
**Method:** HTTP DELETE

**Using curl:**
```bash
curl -X DELETE http://localhost:8000/api/products/1/ \
  -H "Authorization: Token YOUR_TOKEN"
```

**Expected Response (204 No Content):**
```
(empty response body)
```

**Test Status:** ✅ PASSED

---

### ✅ TEST 6: Low-Stock Products
**Endpoint:** `GET /api/products/low-stock/`  
**Auth:** Required  
**Response:** Products with current_stock < 10

**Using curl:**
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/products/low-stock/
```

**Expected Response (200 OK):**
```json
{
  "count": 0,
  "results": []
}
```

**Test Status:** ✅ PASSED (No low-stock items in seed data)

---

### ✅ TEST 7: Out-of-Stock Products
**Endpoint:** `GET /api/products/out-of-stock/`  
**Auth:** Required  
**Response:** Products with current_stock <= 0

**Using curl:**
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/products/out-of-stock/
```

**Expected Response (200 OK):**
```json
{
  "count": 0,
  "results": []
}
```

**Test Status:** ✅ PASSED

---

### ✅ TEST 8: Products by Category
**Endpoint:** `GET /api/products/by-category/{category_id}/`  
**Auth:** Required  
**Response:** All products in specific category

**Using curl:**
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/products/by-category/1/
```

**Expected Response (200 OK):**
```json
{
  "category": {
    "id": 1,
    "name": "Buns",
    "type": "Product"
  },
  "count": 4,
  "results": [
    {
      "id": 1,
      "product_id": "#PROD-1001",
      "name": "Burger Bun",
      ...
    },
    ...
  ]
}
```

**Test Status:** ✅ PASSED (Retrieved 4 buns)

---

### ✅ TEST 9: Search Products
**Endpoint:** `GET /api/products/?search=query`  
**Auth:** Required  
**Response:** Products matching search (product_id, name, or category)

**Using curl:**
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
  'http://localhost:8000/api/products/?search=Bread'
```

**Expected Response (200 OK):**
```json
{
  "count": 4,
  "results": [
    {
      "id": 5,
      "product_id": "#PROD-1005",
      "name": "White Bread",
      ...
    },
    ...
  ]
}
```

**Test Status:** ✅ PASSED (Found 4 bread products)

---

### ✅ TEST 10: Product Recipe (Future)
**Endpoint:** `GET /api/products/{id}/recipe/`  
**Auth:** Required  
**Status:** Currently returns placeholder (RecipeItem model in Task 3.5)

**Using curl:**
```bash
curl -H "Authorization: Token YOUR_TOKEN" \
  http://localhost:8000/api/products/1/recipe/
```

**Expected Response (200 OK):**
```json
{
  "product_id": "#PROD-1001",
  "product_name": "Burger Bun",
  "message": "Recipe feature coming in Task 3.5"
}
```

**Future Integration (Task 3.5):**
This will return recipe items with ingredient requirements:
```json
{
  "product_id": "#PROD-1001",
  "product_name": "Burger Bun",
  "items": [
    {
      "ingredient": "#I001 - All Purpose Flour",
      "quantity_required": 2.5,
      "unit": "kg"
    },
    {
      "ingredient": "#I020 - Salt",
      "quantity_required": 0.05,
      "unit": "kg"
    }
  ]
}
```

---

## Test Cases

### Manual Test Matrix

| Test # | Scenario | Method | Endpoint | Expected Status | Notes |
|--------|----------|--------|----------|-----------------|-------|
| 1 | List all products | GET | /api/products/ | 200 | Should show 20 products |
| 2 | Filter by category | GET | /api/products/?category_id=1 | 200 | Should show 4 buns |
| 3 | Filter by status | GET | /api/products/?status=available | 200 | Should show all products |
| 4 | Search products | GET | /api/products/?search=Bread | 200 | Should find 4 breads |
| 5 | Get product detail | GET | /api/products/1/ | 200 | Should include profit_margin |
| 6 | Create product (Manager) | POST | /api/products/ | 201 | Should auto-generate #PROD-ID |
| 7 | Create with invalid price | POST | /api/products/ | 400 | selling_price > cost_price |
| 8 | Update product (Manager) | PATCH | /api/products/1/ | 200 | Should update fields |
| 9 | Delete product (Manager) | DELETE | /api/products/1/ | 204 | Should remove product |
| 10 | Low-stock endpoint | GET | /api/products/low-stock/ | 200 | Returns <10 quantity items |
| 11 | Out-of-stock endpoint | GET | /api/products/out-of-stock/ | 200 | Returns 0 quantity items |
| 12 | By-category endpoint | GET | /api/products/by-category/1/ | 200 | Returns products in category |
| 13 | Profit margin calculation | GET | /api/products/1/ | 200 | Margin field should calculate correctly |
| 14 | Permission: Read access | GET | /api/products/ | 200 | Any role can read |
| 15 | Permission: Create access | POST | /api/products/ | 201/403 | Only Manager can create |

---

## Database Verification

### Check Product Count
```bash
python manage.py shell << EOF
from api.models import Product
total = Product.objects.count()
print(f"Total products: {total}")

# By category
from django.db.models import Count
by_category = Product.objects.values('category_id__name').annotate(count=Count('id')).order_by('category_id__name')
for item in by_category:
    print(f"  {item['category_id__name']}: {item['count']}")
EOF
```

**Expected Output:**
```
Total products: 20
  Buns: 4
  Bread: 4
  Cakes: 4
  Drinks: 4
  Pastries: 4
```

### Check Auto-ID Generation
```bash
python manage.py shell << EOF
from api.models import Product
products = Product.objects.all()[:5]
for p in products:
    print(f"{p.product_id}: {p.name} (Rs. {p.selling_price}, {p.status})")
EOF
```

**Expected Output:**
```
#PROD-1001: Burger Bun (Rs. 25.00, available)
#PROD-1002: Hot Dog Bun (Rs. 20.00, available)
#PROD-1003: Round Bun (Rs. 30.00, available)
#PROD-1004: Dinner Roll (Rs. 15.00, available)
#PROD-1005: White Bread (Rs. 120.00, available)
```

### Check Profit Margin Calculation
```bash
python manage.py shell << EOF
from api.models import Product
product = Product.objects.first()
cost = float(product.cost_price)
selling = float(product.selling_price)
margin = product.profit_margin
expected = (selling - cost) / cost * 100
print(f"Product: {product.name}")
print(f"  Cost: Rs. {cost}")
print(f"  Selling: Rs. {selling}")
print(f"  Margin: {margin:.2f}%")
print(f"  Expected: {expected:.2f}%")
print(f"  Match: {abs(margin - expected) < 0.01}")
EOF
```

---

## Profit Margin Calculation

### Formula
```
profit_margin = (selling_price - cost_price) / cost_price × 100
```

### Examples

| Product | Cost | Selling | Calculation | Margin |
|---------|------|---------|-------------|--------|
| Burger Bun | Rs. 15 | Rs. 25 | (25-15)/15 × 100 | 66.67% |
| White Bread | Rs. 75 | Rs. 120 | (120-75)/75 × 100 | 60.00% |
| Chocolate Cake | Rs. 250 | Rs. 450 | (450-250)/250 × 100 | 80.00% |
| Coffee | Rs. 60 | Rs. 120 | (120-60)/60 × 100 | 100.00% |

---

## Troubleshooting

### Issue: Products not loading

**Solution:**
```bash
# Check if migrations applied
python manage.py migrate api

# Load seed data
python manage.py seed_products

# Verify in shell
python manage.py shell
>>> from api.models import Product
>>> Product.objects.count()
```

### Issue: 404 on product endpoints

**Solution:**
```bash
# Check if ProductViewSet is registered
python manage.py shell
>>> from django.urls import get_resolver
>>> resolver = get_resolver()
>>> [p for p in resolver.url_patterns if 'product' in str(p)]
```

### Issue: Permission denied on POST

**Solution:**
```bash
# Verify user role is Manager
python manage.py shell
>>> from api.models import User
>>> user = User.objects.get(username='testuser')
>>> print(user.role)
# Should print: Manager
```

### Issue: Profit margin showing 0%

**Solution:**
Check that cost_price is not zero:
```bash
# In Django shell
>>> product = Product.objects.first()
>>> print(product.cost_price)
# Should be > 0
```

---

## Next Steps

**Task 3.5: Recipe Management**
- Create RecipeItem model
- Link products to ingredients with quantities
- Implement recipe endpoints
- Calculate ingredient requirements for production

**Task 3.6: ProductBatch Model**
- Track product production batches
- Manage batch shelf-life
- Integrate with stock management

---

**All endpoints verified and ready for use!** ✅
