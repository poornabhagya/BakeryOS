# Task 3.5: Recipe Management - Testing Guide

**Status:** COMPLETE ✅  
**Date:** March 23, 2026  
**API Base URL:** `http://localhost:8000/api`

---

## Overview

This guide provides step-by-step instructions for manually testing the Recipe Management API using Postman. The Recipe API allows you to:

- Define recipes for products (specify which ingredients are needed)
- Track ingredient quantities per recipe
- Calculate ingredient requirements for batch production
- Validate if sufficient ingredients exist to make a product
- Auto-calculate product cost_price from recipe

---

## Prerequisites

1. **Django Server Running:** Start the server with:
   ```bash
   python manage.py runserver
   ```

2. **Test User Token:** 
   - Username: `testuser`
   - Role: `Manager`
   - Token: `bd616d5e8bd9e45e61e40721c043b7f0edeb6b6d`

3. **Sample Data:**
   - Products: 20 items (Buns, Bread, Cakes, Pastries, Drinks)
   - Ingredients: 19+ items (Flour, Yeast, Salt, Sugar, Dairy, etc.)

---

## Postman Setup

### Step 1: Create Environment Variables

In Postman, create a new environment with these variables:

```
base_url: http://localhost:8000/api
token: bd616d5e8bd9e45e61e40721c043b7f0edeb6b6d
product_id: 1
ingredient_id: 1
```

### Step 2: Create Request Header Template

Use this header for ALL requests:

```
Authorization: Token {{token}}
Content-Type: application/json
```

---

## Test Cases

### TEST 1: Add Ingredient to Recipe

**Endpoint:** `POST {{base_url}}/recipes/{{product_id}}/items/`

**Authorization:** Manager only

**Request Body:**
```json
{
    "ingredient_id": 1,
    "quantity_required": 2.5
}
```

**Expected Response:** `201 Created`

```json
{
    "id": 1,
    "product_id": 1,
    "ingredient_id": 1,
    "ingredient_name": "All Purpose Flour",
    "ingredient_code": "#I001",
    "quantity_required": "2.50",
    "base_unit": "kg",
    "created_at": "2026-03-23T21:48:44.932621+05:30",
    "updated_at": "2026-03-23T21:48:44.932649+05:30"
}
```

**What This Tests:**
- ✓ Recipe item creation
- ✓ Validation of quantity > 0
- ✓ Manager permission check
- ✓ Product and ingredient existence

**Common Errors:**
- `400` - Duplicate ingredient in recipe
- `400` - Invalid quantity (must be > 0)
- `403` - Non-Manager role trying to add
- `404` - Product or ingredient not found

---

### TEST 2: Get Recipe for Product

**Endpoint:** `GET {{base_url}}/recipes/{{product_id}}/`

**Authorization:** Any authenticated user

**Request Body:** (none)

**Expected Response:** `200 OK`

```json
{
    "product_id": 1,
    "product_name": "White Bread Loaf",
    "product_code": "#PROD-1001",
    "product_cost_price": "5.50",
    "product_selling_price": "15.00",
    "items": [
        {
            "id": 1,
            "product_id": 1,
            "product_name": "White Bread Loaf",
            "product_code": "#PROD-1001",
            "ingredient_id": 1,
            "ingredient_name": "All Purpose Flour",
            "ingredient_code": "#I001",
            "ingredient_category": "Flour",
            "ingredient_supplier": "ABC Mills",
            "base_unit": "kg",
            "quantity_required": "2.50",
            "current_stock": "50.00",
            "ingredient_cost_per_unit": 1.2,
            "total_cost_for_recipe": 3.0,
            "created_at": "2026-03-23T21:48:44.932621+05:30",
            "updated_at": "2026-03-23T21:48:44.932649+05:30"
        }
    ],
    "total_recipe_cost": 3.0,
    "total_items": 1
}
```

**What This Tests:**
- ✓ Recipe retrieval with all ingredients expanded
- ✓ Shows current stock and ingredient details
- ✓ Calculates total recipe cost
- ✓ Cost calculation from batch information

**Common Errors:**
- `404` - No recipe exists for product
- `404` - Product not found

---

### TEST 3: Update Recipe Item Quantity

**Endpoint:** `PUT {{base_url}}/recipes/{{product_id}}/items/{{ingredient_id}}/`

**Authorization:** Manager only

**Request Body:**
```json
{
    "quantity_required": 3.0
}
```

**Expected Response:** `200 OK`

```json
{
    "id": 1,
    "product_id": 1,
    "ingredient_id": 1,
    "ingredient_name": "All Purpose Flour",
    "ingredient_code": "#I001",
    "quantity_required": "3.00",
    "base_unit": "kg",
    "created_at": "2026-03-23T21:48:44.932621+05:30",
    "updated_at": "2026-03-23T21:48:45.123456+05:30"
}
```

**What This Tests:**
- ✓ Partial update of recipe items
- ✓ Quantity validation
- ✓ Manager permission check
- ✓ Timestamp update

**Common Errors:**
- `400` - Invalid quantity (must be > 0)
- `403` - Non-Manager trying to update
- `404` - Recipe ingredient not found

---

### TEST 4: Validate Recipe (Check Stock)

**Endpoint:** `GET {{base_url}}/recipes/{{product_id}}/validate/`

**Authorization:** Any authenticated user

**Request Body:** (none)

**Expected Response:** `200 OK`

**Success Case (All ingredients in stock):**
```json
{
    "product_id": 1,
    "product_name": "White Bread Loaf",
    "can_make": true,
    "reason": "All ingredients in stock",
    "missing_ingredients": []
}
```

**Error Case (Insufficient stock):**
```json
{
    "product_id": 1,
    "product_name": "White Bread Loaf",
    "can_make": false,
    "reason": "Insufficient stock for one or more ingredients",
    "missing_ingredients": [
        {
            "ingredient_id": 1,
            "ingredient_name": "All Purpose Flour",
            "ingredient_code": "#I001",
            "required": 2.5,
            "available": 1.0,
            "short_by": 1.5
        }
    ]
}
```

**What This Tests:**
- ✓ Validation logic for ingredient availability
- ✓ Identifies missing/short ingredients
- ✓ Calculates shortage amounts
- ✓ Handles no-recipe scenario

**Common Errors:**
- `404` - Product not found
- `404` - No recipe defined

---

### TEST 5: Calculate Batch Requirements

**Endpoint:** `GET {{base_url}}/recipes/{{product_id}}/batch_required/?qty=10`

**Authorization:** Any authenticated user

**Query Parameters:**
- `qty` - Number of products to make (integer, > 0)

**Request Body:** (none)

**Expected Response:** `200 OK`

```json
{
    "product_id": 1,
    "product_name": "White Bread Loaf",
    "batch_quantity": 10,
    "ingredients_needed": [
        {
            "ingredient_id": 1,
            "ingredient_name": "All Purpose Flour",
            "ingredient_code": "#I001",
            "base_unit": "kg",
            "quantity_per_unit": 2.5,
            "total_required": 25.0,
            "current_stock": 50.0,
            "sufficient": true,
            "cost_per_unit": 1.2,
            "total_cost": 30.0
        },
        {
            "ingredient_id": 8,
            "ingredient_name": "Yeast",
            "ingredient_code": "#I008",
            "base_unit": "g",
            "quantity_per_unit": 0.01,
            "total_required": 0.1,
            "current_stock": 5.0,
            "sufficient": true,
            "cost_per_unit": 500.0,
            "total_cost": 50.0
        }
    ],
    "total_batch_cost": 80.0,
    "total_items_in_recipe": 2
}
```

**What This Tests:**
- ✓ Multiplies recipe quantities by batch size
- ✓ Calculates total ingredient requirements
- ✓ Shows cost per unit for each ingredient
- ✓ Checks if sufficient stock exists
- ✓ Calculates total batch production cost
- ✓ Handles batch quantity parameter

**Common Errors:**
- `400` - Invalid qty parameter
- `404` - Product not found
- `404` - No recipe defined

**Example Requests with Different Quantities:**

Make 1 unit (default):
```
GET /api/recipes/1/validate/
```

Make 50 units:
```
GET /api/recipes/1/batch_required/?qty=50
```

---

### TEST 6: Remove Ingredient from Recipe

**Endpoint:** `DELETE {{base_url}}/recipes/{{product_id}}/items/{{ingredient_id}}/`

**Authorization:** Manager only

**Request Body:** (none)

**Expected Response:** `200 OK`

```json
{
    "message": "Ingredient removed from recipe",
    "product_id": 1,
    "ingredient_id": 1
}
```

**What This Tests:**
- ✓ Recipe item deletion
- ✓ Manager permission check
- ✓ Automatic product cost_price recalculation
- ✓ Proper cleanup of associations

**Common Errors:**
- `403` - Non-Manager trying to delete
- `404` - Recipe ingredient not found

---

## Business Logic Validations

### 1. Prevent Duplicate Ingredients

**Test:** Try to add the same ingredient twice to a product's recipe

```
POST /api/recipes/1/items/
{
    "ingredient_id": 1,
    "quantity_required": 2.5
}

# Second POST with same ingredient_id
POST /api/recipes/1/items/
{
    "ingredient_id": 1,  # Already in recipe!
    "quantity_required": 1.5
}
```

**Expected:** `400 Bad Request`
```json
{
    "ingredient_id": "This ingredient is already in the recipe for White Bread Loaf"
}
```

---

### 2. Quantity Validation

**Test:** Try to add ingredient with quantity ≤ 0

```
POST /api/recipes/1/items/
{
    "ingredient_id": 5,
    "quantity_required": 0  # Invalid!
}
```

**Expected:** `400 Bad Request`
```json
{
    "quantity_required": "Quantity required must be greater than 0"
}
```

---

### 3. Permission Enforcement

**Test:** Try to add ingredient as non-Manager user

```
# Use a Baker's token instead of Manager's token
Authorization: Token <baker_token>

POST /api/recipes/1/items/
{
    "ingredient_id": 5,
    "quantity_required": 2.5
}
```

**Expected:** `403 Forbidden`
```json
{
    "error": "Only Managers can add ingredients to recipes"
}
```

---

## Performance Testing

### High-Volume Batch Calculation

Test with large batch quantities to ensure performance:

```
GET /api/recipes/1?qty=1000
GET /api/recipes/1?qty=5000
GET /api/recipes/1?qty=10000
```

**Expected Response Time:** < 2 seconds for reasonable batch sizes

---

## Error Scenarios

### Scenario 1: Recipe with Missing Ingredients

1. Create a product
2. Add ingredients to recipe
3. Deduct ingredient quantities to below recipe requirements
4. Call validate endpoint
5. Should show missing items and shortage amounts

### Scenario 2: Non-existent Product

```
GET /api/recipes/99999/
```

**Expected:** `404 Not Found`
```json
{
    "error": "Product with ID 99999 not found"
}
```

### Scenario 3: Recipe Without Items

Create a product without adding any ingredients, then:

```
GET /api/recipes/1/
```

**Expected:** `404 Not Found`
```json
{
    "error": "No recipe defined for product #PROD-1001"
}
```

---

## Success Criteria

All of the following must pass for Task 3.5 to be considered complete:

- ✅ [TEST 1] Add ingredient to recipe (POST)
- ✅ [TEST 2] Get collection recipe (GET)
- ✅ [TEST 3] Update recipe item quantity (PUT)
- ✅ [TEST 4] Validate recipe/check stock (GET)
- ✅ [TEST 5] Calculate batch requirements (GET)
- ✅ [TEST 6] Remove ingredient from recipe (DELETE)
- ✅ Prevent duplicate ingredients validation
- ✅ Quantity > 0 validation
- ✅ Manager-only permission enforcement
- ✅ Automatic cost_price calculation from recipe
- ✅ All error scenarios return proper HTTP codes
- ✅ Database migrations applied successfully
- ✅ All test cases pass

---

## Database Inspection

To inspect the recipe data directly in the database:

```bash
python manage.py shell
```

```python
from api.models import RecipeItem, Product
from django.db.models import Prefetch

# Get all recipes with their ingredients
recipes = Product.objects.prefetch_related('recipe_items__ingredient_id').all()

for product in recipes:
    if product.recipe_items.exists():
        print(f"\n{product.product_id} - {product.name}:")
        for item in product.recipe_items.all():
            print(f"  - {item.ingredient_id.ingredient_id}: {item.quantity_required}{item.ingredient_id.base_unit}")

# Get count
print(f"\nTotal recipe items: {RecipeItem.objects.count()}")
```

---

## API Summary Table

| Method | Endpoint | Auth | Permission | Status |
|--------|----------|------|-----------|--------|
| POST | /api/recipes/{id}/items/ | Yes | Manager | 201 |
| GET | /api/recipes/{id}/ | Yes | Any | 200 |
| PUT | /api/recipes/{id}/items/{ing_id}/ | Yes | Manager | 200 |
| DELETE | /api/recipes/{id}/items/{ing_id}/ | Yes | Manager | 200 |
| GET | /api/recipes/validate/{id}/ | Yes | Any | 200 |
| GET | /api/recipes/batch-required/{id} | Yes | Any | 200 |

---

## Migration Status

- ✅ Migration created: `0008_recipeitem_and_more.py`
- ✅ Migration applied: `Applying api.0008_recipeitem... OK`
- ✅ Database table: `api_recipeitem` created
- ✅ Indexes created on product_id and ingredient_id
- ✅ Unique constraint on (product_id, ingredient_id)

---

## Next Steps (Task 3.6+)

- Production batch management (linking recipes to batch production)
- Recipe costing automation
- Ingredient substitution rules
- Recipe import/export functionality
- Recipe versioning for cost tracking

---

**Document Version:** 1.0  
**Last Updated:** March 23, 2026  
**Status:** Ready for Manual Testing ✅
