# BakeryOS Backend - Quick Reference Guide

**Last Updated:** March 23, 2026  
**API Status:** ✅ Task 3.1 & 3.2 Complete  
**Database:** SQLite (18 seeds loaded)

---

## 🚀 Quick Start

### 1. Activate Environment
```bash
cd Backend
.\venv\Scripts\activate
```

### 2. Start Django Server
```bash
python manage.py runserver
# Server: http://localhost:8000
```

### 3. Get Auth Token (First Time)
```bash
# Command not available yet - manually create in Django admin
python manage.py createsuperuser

# Then in Django shell:
python manage.py shell
>>> from rest_framework.authtoken.models import Token
>>> from auth.models import User
>>> user = User.objects.get(username='admin')
>>> token = Token.objects.create(user=user)
>>> print(token.key)
```

### 4. Make API Requests
```bash
# Export token for easy use
$TOKEN = "abc123def456..."

# List categories
curl -H "Authorization: Token $TOKEN" http://localhost:8000/api/categories/

# List ingredients
curl -H "Authorization: Token $TOKEN" http://localhost:8000/api/ingredients/
```

---

## 📚 Current API Endpoints

### Categories (7 endpoints)
```
GET     /api/categories/                    List all
POST    /api/categories/                    Create
GET     /api/categories/{id}/               Details
PUT     /api/categories/{id}/               Replace
PATCH   /api/categories/{id}/               Partial update
DELETE  /api/categories/{id}/               Delete (soft)
GET     /api/categories/by_type/            Group by type
```

### Ingredients (10 endpoints)
```
GET     /api/ingredients/                       List all
POST    /api/ingredients/                       Create
GET     /api/ingredients/{id}/                  Details
PUT     /api/ingredients/{id}/                  Replace
PATCH   /api/ingredients/{id}/                  Partial update
DELETE  /api/ingredients/{id}/                  Delete (soft)
GET     /api/ingredients/low_stock/             Low-stock items
GET     /api/ingredients/by_category/           Group by category
GET     /api/ingredients/out_of_stock/          Zero quantity items
GET     /api/ingredients/?search=QUERY          Search
```

### Batches (12 endpoints) ✨ NEW
```
GET     /api/batches/                           List all (FIFO order)
POST    /api/batches/                           Create new
GET     /api/batches/{id}/                      Details
PUT     /api/batches/{id}/                      Replace
PATCH   /api/batches/{id}/                      Partial update
DELETE  /api/batches/{id}/                      Delete
GET     /api/batches/expiring/                  Expiring within N days
GET     /api/batches/expired/                   All expired
GET     /api/batches/out-of-stock/              Zero quantity
GET     /api/batches/by-ingredient/{id}/        Batches for ingredient (FIFO)
POST    /api/batches/{id}/consume/              Consume from batch
POST    /api/batches/update-expiry-status/      Update all expirations
```

---

## 🔐 Authentication

### Header Format
```bash
-H "Authorization: Token YOUR_TOKEN_HERE"
```

### Role-Based Permissions

| Endpoint | View | Create | Update | Delete |
|----------|------|--------|--------|--------|
| Categories | ✓ | Manager/SK | Manager/SK | Manager |
| Ingredients | ✓ | Manager/SK | Manager/SK | Manager |

**Roles:**
- `Manager` - Full access to all endpoints
- `Storekeeper` - View & create/update (no delete)
- `Baker` - View only (for recipes/inventory)
- `Cashier` - Limited access (future)

---

## 📝 Common Tasks

### List with Filters
```bash
# Filter by category
?category_id=7

# Filter by active
?is_active=true

# Pagination
?page=2
?page=3&page_size=50

# Search
?search=flour

# Sort
?ordering=name
?ordering=-created_at
```

### Create New Ingredient
```bash
curl -X POST http://localhost:8000/api/ingredients/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Ingredient",
    "category_id": 7,
    "supplier": "ABC Corp",
    "supplier_contact": "0771234567",
    "tracking_type": "Weight",
    "base_unit": "kg",
    "low_stock_threshold": 50,
    "shelf_life": 180,
    "shelf_unit": "days"
  }'
```

### Update Ingredient
```bash
curl -X PATCH http://localhost:8000/api/ingredients/1/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "supplier": "New Supplier",
    "low_stock_threshold": 100
  }'
```

### Delete (Soft) Ingredient
```bash
curl -X DELETE http://localhost:8000/api/ingredients/1/ \
  -H "Authorization: Token $TOKEN"
```

### Create New Batch ✨ NEW
```bash
curl -X POST http://localhost:8000/api/batches/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "ingredient_id": 1,
    "quantity": "50.00",
    "current_qty": "50.00",
    "cost_price": "12.50",
    "made_date": "2026-03-23T10:00:00Z",
    "expire_date": "2026-05-23T10:00:00Z"
  }'
```

### Get Batches by Ingredient (FIFO) ✨ NEW
```bash
curl -H "Authorization: Token $TOKEN" \
  http://localhost:8000/api/batches/by-ingredient/1/
```

### Consume from Batch ✨ NEW
```bash
curl -X POST http://localhost:8000/api/batches/1/consume/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"amount": "15.00"}'
```

### Get Expiring Batches ✨ NEW
```bash
curl -H "Authorization: Token $TOKEN" \
  "http://localhost:8000/api/batches/expiring/?days=7"
```

## 🧪 Testing

### Run All Tests
```bash
python test_categories_endpoints.py
python test_ingredients_endpoints.py
python test_batches_endpoints.py
```

### Run Single Test
```bash
python -c "import test_categories_endpoints; test_categories_endpoints.TestCategoryAPI().test_list_categories()"
```

### Django Test Suite
```bash
python manage.py test api.tests
```

---

## 🔍 Debugging

### Django Shell
```bash
python manage.py shell
```

**Common Commands:**
```python
# Check categories
from api.models import Category
categories = Category.objects.all()
for c in categories:
    print(f"{c.category_id}: {c.name}")

# Check ingredients
from api.models import Ingredient
ingredients = Ingredient.objects.filter(is_active=True)
for i in ingredients:
    print(f"{i.ingredient_id}: {i.name} ({i.stock_status})")

# Count by status
from django.db.models import Q, F
low_stock = Ingredient.objects.filter(
    total_quantity__lt=F('low_stock_threshold')
).count()
print(f"Low stock items: {low_stock}")
```

### Check Database
```bash
# SQLite CLI
sqlite3 db.sqlite3

# In SQLite:
.tables                           # List all tables
SELECT * FROM api_category;      # View categories
SELECT * FROM api_ingredient;    # View ingredients
.schema api_ingredient            # View table schema
```

---

## 📊 Data Status

### Categories (6 seeded)
| ID | Name | Type | Count |
|----|------|------|-------|
| 7 | Flour | Ingredient | 3 |
| 8 | Sugar | Ingredient | 3 |
| 9 | Dairy | Ingredient | 3 |
| 10 | Spices | Ingredient | 3 |
| 11 | Additives | Ingredient | 3 |
| 12 | Others | Ingredient | 3 |

### Ingredients (18 seeded)
All ingredients loaded with 0 quantity (waiting for batches)

### Batches (54 seeded) ✨ NEW
- 3 batches per ingredient
- Active: 36 batches
- Expired: 18 batches
- Total available quantity: ~3,600 units

---

## 🛠️ File Structure

### Backend Folder
```
Backend/
├── manage.py                      # Django management
├── .env                           # Environment variables
├── db.sqlite3                     # Database
├── core/
│   ├── settings.py               # Django config
│   ├── urls.py                   # URL routing
│   ├── asgi.py
│   └── wsgi.py
├── api/
│   ├── models.py                 # Category, Ingredient models
│   ├── serializers.py            # API serializers
│   ├── views.py                  # ViewSets & API logic
│   ├── urls.py                   # API routing
│   ├── permissions.py            # Permission classes
│   ├── management/
│   │   └── commands/
│   │       ├── seed_categories.py
│   │       └── seed_ingredients.py
│   └── migrations/
├── test_*.py                      # Test files
├── TESTING_GUIDE_TASK_3_1.md     # Category testing guide
├── TESTING_GUIDE_TASK_3_2.md     # Ingredient testing guide
├── PROJECT_SUMMARY_PHASE_3.md    # Phase 3 summary
└── VENV/                         # Virtual environment
```

---

## 🔧 Environment Setup

### Windows PowerShell
```powershell
# Create venv
python -m venv venv

# Activate
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start server
python manage.py runserver
```

### macOS/Linux
```bash
# Create venv
python3 -m venv venv

# Activate
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Start server
python manage.py runserver
```

---

## 📝 Log Format

### API Response Structure
```json
{
  "count": 18,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "ingredient_id": "#I001",
      "name": "All Purpose Flour",
      "category_id": 7,
      "tracking_type": "Weight",
      "base_unit": "kg",
      "total_quantity": "0.00",
      "low_stock_threshold": "50.00",
      "stock_status": "OUT_OF_STOCK",
      "is_active": true,
      "created_at": "2024-03-23T10:00:00Z",
      "updated_at": "2024-03-23T10:00:00Z"
    }
  ]
}
```

### Error Response
```json
{
  "detail": "Not found."
}
```

---

## ⚠️ Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| `401 Unauthorized` | Missing token | Add `-H "Authorization: Token TOKEN"` |
| `403 Forbidden` | Wrong role | Use Manager account for create/delete |
| `404 Not Found` | Wrong ID | Use numeric `id`, not `ingredient_id` |
| `400 Bad Request` | Duplicate name | Check name is unique in category |
| `Server Error 500` | ? | Check `python manage.py migrate` was run |
| Import Error | Missing install | Run `pip install -r requirements.txt` |

---

## 📅 Next Milestone

**Task 3.3 - Ingredient Batches** (4 hours)

New endpoints coming:
```
POST   /api/batches/                Create batch
GET    /api/batches/                List batches
GET    /api/batches/{id}/           Batch details
PATCH  /api/batches/{id}/           Update quantity
DELETE /api/batches/{id}/           Expire batch
```

Features:
- Batch tracking with expiry dates
- Auto-update ingredient quantities
- FIFO expiry management
- Batch history & audit trail

---

## 📞 Useful Resources

### Documentation
- [TESTING_GUIDE_TASK_3_1.md](TESTING_GUIDE_TASK_3_1.md) - Category API docs
- [TESTING_GUIDE_TASK_3_2.md](TESTING_GUIDE_TASK_3_2.md) - Ingredient API docs
- [TESTING_GUIDE_TASK_3_3.md](TESTING_GUIDE_TASK_3_3.md) - Batch API docs ✨ NEW
- [PROJECT_SUMMARY_PHASE_3.md](PROJECT_SUMMARY_PHASE_3.md) - Overall status

### Command Reference
- `python manage.py shell` - Database shell
- `python manage.py createsuperuser` - Create admin
- `python manage.py migrate` - Apply migrations
- `python manage.py seed_categories` - Load categories
- `python manage.py seed_ingredients` - Load ingredients

### API Testing Tools
- **curl** - Command line HTTP client
- **Postman** - GUI API tester
- **VS Code REST Client** - Inline request testing
- **Thunder Client** - VS Code extension

---

**Bookmark this file for quick reference during development!**
