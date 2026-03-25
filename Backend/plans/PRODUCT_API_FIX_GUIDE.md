# TASK 3.4 - FIX & TEST GUIDE

## Issue Summary
- ❌ Getting 500 Internal Server Error on `GET http://localhost:8000/api/products/`
- ❌ Django showing "1 unapplied migration(s)" warning

## Root Cause
The Product model migration (0007_product.py) has not been applied to the SQLite database.

## FIX STEPS (Run these in order)

### Step 1: Stop the current server
```
Press CTRL-BREAK in the terminal where server is running
```

### Step 2: Apply migrations
```powershell
cd "c:\Projects\campus project\BakeryOS_Project\Backend"
.\venv\Scripts\activate.ps1
python manage.py migrate
```

**Expected Output:**
```
Running migrations:
  Applying api.0007_product... OK
```

### Step 3: Verify migration was applied
```powershell
python manage.py migrate --list
```

Look for this line (should have [X] checkmark):
```
[X] 0007_product
```

### Step 4: Start server again
```powershell
python manage.py runserver 8000
```

**Expected Output (NO migration warning):**
```
System check identified no issues (0 silenced).

March 23, 2026 - ...
Django version 6.0.3, using settings 'core.settings'
Starting development server at http://127.0.0.1:8000/
```

---

## MANUAL TEST IN POSTMAN

### 1️⃣ Test: List Products
**Method:** GET  
**URL:** `http://localhost:8000/api/products/`  
**Headers:**
```
Authorization: Token bd616d5e8bd9e45e61e40721c043b7f0edeb6b6d
Content-Type: application/json
```

**Expected Response (200 OK):**
```json
{
  "count": 0,
  "next": null,
  "previous": null,
  "results": []
}
```
*(Will show 0 products initially - that's OK, we'll create some below)*

---

### 2️⃣ Test: Create Product
**Method:** POST  
**URL:** `http://localhost:8000/api/products/`  
**Headers:**
```
Authorization: Token bd616d5e8bd9e45e61e40721c043b7f0edeb6b6d
Content-Type: application/json
```

**Body:**
```json
{
  "category_id": 1,
  "name": "Burger Bun",
  "cost_price": "15.00",
  "selling_price": "25.00",
  "current_stock": "50",
  "shelf_life": 2,
  "shelf_unit": "days"
}
```

**Expected Response (201 Created):**
```json
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
  "created_at": "2026-03-23T...",
  "updated_at": "2026-03-23T..."
}
```

---

### 3️⃣ Test: Get Product Details  
**Method:** GET  
**URL:** `http://localhost:8000/api/products/1/`  
**Headers:** (same as above)

**Expected Response (200 OK):**
```json
{
  "id": 1,
  "product_id": "#PROD-1001",
  "name": "Burger Bun",
  "category_name": "Buns",
  "cost_price": "15.00",
  "selling_price": "25.00",
  "profit_margin": 66.67,
  "current_stock": "50.00",
  "status": "available",
  "is_low_stock": false,
  "is_out_of_stock": false,
  "shelf_life": 2,
  "shelf_unit": "days"
}
```

---

### 4️⃣ Test: Update Product
**Method:** PATCH  
**URL:** `http://localhost:8000/api/products/1/`  
**Headers:** (same as above)

**Body:**
```json
{
  "current_stock": "75"
}
```

**Expected Response (200 OK):**
```json
{
  "id": 1,
  "product_id": "#PROD-1001",
  "current_stock": "75.00",
  ...
}
```

---

### 5️⃣ Test: Delete Product
**Method:** DELETE  
**URL:** `http://localhost:8000/api/products/1/`  
**Headers:** (same as above)

**Expected Response (204 No Content):**
```
(empty body)
```

---

### 6️⃣ Test: Low-Stock Products
**Method:** GET  
**URL:** `http://localhost:8000/api/products/low_stock/`  
**Headers:** (same as above)

**Expected Response (200 OK):**
```json
{
  "count": 0,
  "results": []
}
```

---

### 7️⃣ Test: Out-of-Stock Products
**Method:** GET  
**URL:** `http://localhost:8000/api/products/out_of_stock/`  
**Headers:** (same as above)

**Expected Response (200 OK):**
```json
{
  "count": 0,
  "results": []
}
```

---

## ✅ Success Checklist

- [ ] Migration applied (`python manage.py migrate` successful)
- [ ] Server starts without "unapplied migration" warning
- [ ] `GET /api/products/` returns 200 OK (not 500 error)
- [ ] Can create product with POST (returns 201 with auto-ID)
- [ ] Can get product details with GET
- [ ] Can update product with PATCH
- [ ] Can delete product with DELETE
- [ ] All custom endpoints return 200 OK

---

## Troubleshooting

### Still getting 500 error?
```bash
# Check if Product table exists
sqlite3 db.sqlite3 ".tables" | grep api_product

# If missing, force migrate
python manage.py migrate --fake-initial
python manage.py migrate
```

### Still seeing migration warning?
```bash
# Check migration status
python manage.py showmigrations api

# Should show:
# [X] 0007_product
```

### Permission denied error?
Make sure you're using Manager role token:
```bash
python manage.py shell
from api.models import User
user = User.objects.get(username='testuser')
print(user.role)  # Should print: Manager
```

---

**After these steps, all Product API endpoints should work perfectly!** ✅
