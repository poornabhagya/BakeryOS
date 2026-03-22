# BakeryOS Backend - Technical Reference Guide

## 1. PROJECT STRUCTURE

```
Backend/
├── core/                          # Django project settings
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py               # ⭐ Update INSTALLED_APPS, CORS, REST_FRAMEWORK, JWT
│   ├── urls.py                   # ⭐ Include api.urls
│   └── wsgi.py
├── api/                           # Main application
│   ├── migrations/               # Django migrations
│   │   └── __init__.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── auth.py               # User model
│   │   ├── categories.py          # Category model
│   │   ├── inventory.py           # Ingredient, IngredientBatch
│   │   ├── products.py            # Product, ProductBatch, RecipeItem
│   │   ├── sales.py               # Sale, SaleItem, Discount
│   │   ├── wastage.py             # ProductWastage, IngredientWastage, WastageReason
│   │   ├── audit.py               # ProductStockHistory, IngredientStockHistory
│   │   └── notifications.py       # Notification, NotificationReceipt
│   ├── serializers/
│   │   ├── __init__.py
│   │   ├── auth.py                # LoginSerializer, TokenSerializer, UserSerializer
│   │   ├── categories.py          # CategorySerializer
│   │   ├── inventory.py           # IngredientSerializer, BatchSerializer
│   │   ├── products.py            # ProductSerializer, RecipeItemSerializer
│   │   ├── sales.py               # SaleSerializer, SaleItemSerializer, DiscountSerializer
│   │   ├── wastage.py             # WastageSerializer
│   │   └── notifications.py       # NotificationSerializer
│   ├── views/
│   │   ├── __init__.py
│   │   ├── auth.py                # AuthViewSet (login, refresh, logout, me)
│   │   ├── users.py               # UserViewSet (CRUD)
│   │   ├── categories.py          # CategoryViewSet
│   │   ├── inventory.py           # IngredientViewSet, BatchViewSet
│   │   ├── products.py            # ProductViewSet, RecipeViewSet
│   │   ├── sales.py               # SaleViewSet, DiscountViewSet
│   │   ├── wastage.py             # WastageViewSet
│   │   ├── analytics.py           # AnalyticsViewSet
│   │   └── notifications.py       # NotificationViewSet
│   ├── permissions/
│   │   ├── __init__.py
│   │   └── custom.py              # IsManager, IsCashier, IsBaker, IsStorekeeper, etc.
│   ├── filters/
│   │   ├── __init__.py
│   │   └── custom.py              # Custom filter classes
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── calculations.py        # profit_margin, discount_calc, etc.
│   │   ├── validators.py          # contact_validator, etc.
│   │   ├── generators.py          # auto_id generators (EMP, PROD, etc.)
│   │   └── notifications.py       # Notification helper functions
│   ├── signals.py                 # Django signals for stock sync, notifications
│   ├── admin.py                   # Register models in admin
│   ├── apps.py
│   ├── tests.py                   # OR create tests/ directory
│   ├── urls.py                    # ⭐ Define all API routes
│   └── __init__.py
├── tests/                         # Test directory (alternative to tests.py)
│   ├── test_auth.py
│   ├── test_users.py
│   ├── test_products.py
│   ├── test_sales.py
│   ├── test_ingredients.py
│   ├── test_wastage.py
│   └── test_analytics.py
├── manage.py
├── requirements.txt               # ⭐ All Python dependencies
├── .env                           # ⭐ Database credentials, SECRET_KEY
├── BACKEND_WORK_PLAN.md           # This detailed work plan
├── IMPLEMENTATION_CHECKLIST.md    # Quick reference checklist
└── TECHNICAL_REFERENCE.md         # This file

```

---

## 2. KEY DEPENDENCIES

```txt
Django==6.0.3                                # Web framework
djangorestframework==3.14.0                  # REST API
django-cors-headers==4.0.0                   # CORS support
djangorestframework-simplejwt==5.2.2         # JWT authentication
psycopg2-binary==2.9.6                       # PostgreSQL
python-decouple==3.8                         # Environment variables
Pillow==9.5.0                                # Image handling
celery==5.3.1                                # Async tasks
drf-spectacular==0.26.1                      # OpenAPI/Swagger docs
django-filter==23.1                          # Advanced filtering
pytest-django==4.5.2                         # Testing
```

---

## 3. DATABASE SCHEMA SUMMARY

### Core Tables (15 minimum)

| Model Name | DB Table | Key Fields | FK Storage |
|---|---|---|---|
| User | auth_user / users | id, employee_id, username, role, status | - |
| Category | categories | id, category_id, name, type | - |
| Ingredient | ingredients | id, ingredient_id, category_id, total_quantity, low_stock_threshold | category_id |
| IngredientBatch | ingredient_batches | id, batch_id, ingredient_id, quantity, current_qty, expire_date | ingredient_id |
| Product | products | id, product_id, category_id, name, cost_price, selling_price, current_stock | category_id |
| RecipeItem | recipe_items | id, product_id, ingredient_id, quantity_required | product_id, ingredient_id |
| ProductBatch | product_batches | id, batch_id, product_id, quantity, expire_date | product_id |
| Sale | sales | id, bill_number, cashier_id, subtotal, discount_id, total_amount | cashier_id, discount_id |
| SaleItem | sale_items | id, sale_id, product_id, quantity, unit_price | sale_id, product_id |
| Discount | discounts | id, discount_id, type, value, applicable_to, target_category_id, target_product_id | category_id, product_id |
| ProductWastage | product_wastages | id, wastage_id, product_id, quantity, unit_cost, total_loss, reason_id, reported_by | product_id, reason_id, reported_by |
| IngredientWastage | ingredient_wastages | id, wastage_id, ingredient_id, batch_id, quantity, reason_id, reported_by | ingredient_id, batch_id, reason_id, reported_by |
| WastageReason | wastage_reasons | id, reason_id, reason | - |
| ProductStockHistory | product_stock_history | id, product_id, transaction_type, qty_before, qty_after, performed_by | product_id, performed_by |
| IngredientStockHistory | ingredient_stock_history | id, ingredient_id, transaction_type, qty_before, qty_after, performed_by | ingredient_id, performed_by |
| Notification | notifications | id, title, message, type, created_at | - |
| NotificationReceipt | notification_receipts | id, notification_id, user_id, is_read | notification_id, user_id |

---

## 4. API ENDPOINT OVERVIEW

### Authentication (5 endpoints)
```
POST   /api/auth/login/              # Login with username/password
POST   /api/auth/refresh/            # Refresh access token
POST   /api/auth/logout/             # Logout/blacklist token
GET    /api/auth/me/                 # Current user profile
GET    /api/auth/verify/             # Verify token validity
```

### User Management (6 endpoints)
```
GET    /api/users/                   # List all users (paginated, filtered by role/status)
POST   /api/users/                   # Create new user (Manager)
GET    /api/users/{id}/              # Get user details
PUT    /api/users/{id}/              # Update user
DELETE /api/users/{id}/              # Delete user
PATCH  /api/users/{id}/status/       # Change active/inactive
```

### Categories (3 endpoints)
```
GET    /api/categories/              # List categories (filtered by type)
POST   /api/categories/              # Create category (Manager)
GET    /api/categories/{id}/         # Get category details
```

### Ingredients (10 endpoints)
```
GET    /api/ingredients/             # List with pagination, filters
POST   /api/ingredients/             # Create (Manager/Storekeeper)
GET    /api/ingredients/{id}/        # Get details
PUT    /api/ingredients/{id}/        # Update
DELETE /api/ingredients/{id}/        # Delete
GET    /api/ingredients/low-stock/   # Low stock alert
GET    /api/ingredients/{id}/history/    # Stock history
GET    /api/ingredients/{id}/batches/    # All batches
GET    /api/ingredients/search/          # Search by name
PATCH  /api/ingredients/{id}/threshold/  # Update threshold
```

### Ingredient Batches (8 endpoints)
```
GET    /api/batches/                 # List all batches
POST   /api/batches/                 # Add batch (Storekeeper)
GET    /api/batches/{id}/            # Get details
PUT    /api/batches/{id}/            # Update (Storekeeper)
DELETE /api/batches/{id}/            # Delete
GET    /api/batches/expiring/        # Expiring within 2 days
GET    /api/batches/expired/         # Already expired
PATCH  /api/batches/{id}/status/     # Mark as Used/Expired
```

### Products (10 endpoints)
```
GET    /api/products/                # List with search, filter, sort
POST   /api/products/                # Create (Manager)
GET    /api/products/{id}/           # Get details with recipe
PUT    /api/products/{id}/           # Update
DELETE /api/products/{id}/           # Delete
GET    /api/products/low-stock/      # Low stock products
GET    /api/products/by-category/    # Filter by category ID
GET    /api/products/{id}/recipe/    # Get recipe/ingredients
GET    /api/products/{id}/profitability/  # Profit metrics
PATCH  /api/products/{id}/price/     # Update cost/selling prices
```

### Recipes (6 endpoints)
```
GET    /api/recipes/{product_id}/                  # Get recipe
POST   /api/recipes/{product_id}/items/            # Add ingredient
PUT    /api/recipes/{product_id}/items/{ing_id}/   # Update qty
DELETE /api/recipes/{product_id}/items/{ing_id}/   # Remove
POST   /api/recipes/validate/{product_id}/         # Check if enough stock
POST   /api/recipes/batch-required/                # Calculate for batch qty
```

### Discounts (7 endpoints)
```
GET    /api/discounts/               # List all (Manager)
POST   /api/discounts/               # Create
GET    /api/discounts/{id}/          # Get details
PUT    /api/discounts/{id}/          # Update
DELETE /api/discounts/{id}/          # Delete
PATCH  /api/discounts/{id}/toggle/   # Toggle active
GET    /api/discounts/active/        # Get active only
```

### Sales (8 endpoints)
```
GET    /api/sales/                   # List (Manager all, Cashier own)
POST   /api/sales/                   # Process checkout (Cashier)
GET    /api/sales/{bill_number}/     # Get bill details
GET    /api/sales/date-range/        # Filter by date
GET    /api/sales/by-cashier/        # Filter by cashier
GET    /api/sales/by-method/         # Filter by payment method
GET    /api/sales/analytics/         # Daily/weekly/monthly totals
DELETE /api/sales/{id}/              # Void sale (Manager)
```

### Product Batches (5 endpoints)
```
GET    /api/product-batches/         # List production batches
POST   /api/product-batches/         # Create (Baker)
GET    /api/product-batches/{id}/    # Get details
GET    /api/product-batches/expiring/    # Expiring soon
PATCH  /api/product-batches/{id}/use/    # Use batch qty
```

### Wastage (10 endpoints)
```
GET    /api/product-wastages/        # List product wastage
POST   /api/product-wastages/        # Report wastage
GET    /api/product-wastages/{id}/   # Get details
DELETE /api/product-wastages/{id}/   # Delete/undo
GET    /api/product-wastages/analytics/   # Summary by reason

GET    /api/ingredient-wastages/     # List ingredient wastage
POST   /api/ingredient-wastages/     # Report wastage
GET    /api/ingredient-wastages/analytics/

GET    /api/wastage-reasons/         # List all reasons
```

### Analytics (8 endpoints)
```
GET    /api/analytics/sales/daily/       # Daily totals
GET    /api/analytics/sales/weekly/      # Weekly totals
GET    /api/analytics/sales/monthly/     # Monthly totals
GET    /api/analytics/sales/top-products/    # Top 10 products
GET    /api/analytics/inventory/stock-value/    # Total value
GET    /api/analytics/wastage/summary/   # Wastage by reason
GET    /api/analytics/revenue/           # Revenue analysis
GET    /api/dashboard/kpis/              # All KPIs
```

### Stock History (3 endpoints)
```
GET    /api/products/{id}/stock-history/      # Product transactions
GET    /api/ingredients/{id}/stock-history/   # Ingredient transactions
GET    /api/stock-history/search/             # Search by date/type
```

### Notifications (4 endpoints)
```
GET    /api/notifications/               # My notifications
PATCH  /api/notifications/{id}/read/     # Mark single as read
PATCH  /api/notifications/read-all/      # Mark all as read
GET    /api/notifications/unread/count/  # Unread count
```

---

## 5. AUTHENTICATION FLOW

### Login
```
POST /api/auth/login/
Content-Type: application/json

{
  "username": "cashier",
  "password": "123"
}

Response 200:
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user": {
    "id": 2,
    "username": "cashier",
    "full_name": "John Doe",
    "role": "Cashier",
    "employee_id": "EMP-002"
  }
}
```

### Using Token
```
GET /api/auth/me/
Authorization: Bearer {access_token}

Response 200:
{
  "id": 2,
  "username": "cashier",
  "full_name": "John Doe",
  "employee_id": "EMP-002",
  "role": "Cashier",
  "contact": "077-1234567",
  "status": "Active"
}
```

### Refresh Token
```
POST /api/auth/refresh/
Content-Type: application/json

{
  "refresh": "{refresh_token}"
}

Response 200:
{
  "access": "{new_access_token}"
}
```

---

## 6. COMMON API PATTERNS

### List Endpoint (Pagination, Filtering, Search)
```
GET /api/products/?page=1&page_size=20&category=CAT-P001&search=bread&sort=-selling_price

Response:
{
  "count": 150,
  "next": "http://localhost:8000/api/products/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "product_id": "#PROD-1001",
      "name": "White Bread",
      "category": "Bread",
      "selling_price": 250.00,
      "cost_price": 150.00,
      "current_stock": 25,
      "profit_margin": 66.67
    }
  ]
}
```

### Create Endpoint
```
POST /api/products/
Authorization: Bearer {token}
Content-Type: application/json

{
  "name": "Chocolate Cake",
  "category": "CAT-P003",
  "cost_price": 500.00,
  "selling_price": 1200.00,
  "shelf_life": 2,
  "shelf_unit": "Days",
  "image_url": "https://..."
}

Response 201:
{
  "id": 1,
  "product_id": "#PROD-1001",
  "name": "Chocolate Cake",
  "cost_price": 500.00,
  "selling_price": 1200.00,
  "profit_margin": 140.00,
  "created_at": "2026-03-22T14:30:00Z"
}
```

### Sale Creation (POST /api/sales/)
```
{
  "items": [
    {
      "product_id": 1,
      "quantity": 2,
      "unit_price": 250.00
    },
    {
      "product_id": 3,
      "quantity": 1,
      "unit_price": 80.00
    }
  ],
  "payment_method": "Cash",
  "discount_id": null
}

Response 201:
{
  "id": 142,
  "bill_number": "BILL-1042",
  "cashier": {
    "id": 2,
    "full_name": "John Doe",
    "employee_id": "EMP-002"
  },
  "subtotal": 580.00,
  "discount_amount": 0.00,
  "total_amount": 580.00,
  "payment_method": "Cash",
  "sale_items": [
    {
      "product_id": 1,
      "product_name": "White Bread",
      "quantity": 2,
      "unit_price": 250.00,
      "subtotal": 500.00
    }
  ],
  "date_time": "2026-03-22T14:30:00Z"
}
```

---

## 7. ERROR RESPONSE FORMAT

### Standard Error Response
```json
{
  "success": false,
  "error": "Validation Error",
  "details": {
    "contact": ["Invalid format. Expected: XXX-XXXXXXX"],
    "selling_price": ["Must be greater than cost_price"]
  }
}
```

### Common HTTP Status Codes
- **200 OK** - Success
- **201 Created** - Record created
- **204 No Content** - Delete success
- **400 Bad Request** - Validation error
- **401 Unauthorized** - Missing/invalid token
- **403 Forbidden** - Permission denied
- **404 Not Found** - Resource not found
- **500 Server Error** - Backend error

---

## 8. DJANGO SIGNALS TO IMPLEMENT

### When IngredientBatch is Modified
```python
@receiver([post_save, post_delete], sender=IngredientBatch)
def sync_ingredient_total_quantity(sender, instance, **kwargs):
    """Update ingredient.total_quantity whenever batch changes"""
```

### When ProductBatch is Created
```python
@receiver(post_save, sender=ProductBatch)
def update_product_stock_from_batch(sender, instance, created, **kwargs):
    """Add quantity to product.current_stock when batch created"""
```

### When Sale is Created
```python
@receiver(post_save, sender=Sale)
def create_stock_history_for_sale(sender, instance, created, **kwargs):
    """For each SaleItem, create ProductStockHistory entry and deduct stock"""
```

### When Wastage is Reported
```python
@receiver(post_save, sender=ProductWastage)
def deduct_wastage_stock(sender, instance, created, **kwargs):
    """Deduct from product.current_stock and create history"""

@receiver(post_save, sender=IngredientWastage)
def deduct_ingredient_wastage_stock(sender, instance, created, **kwargs):
    """Deduct from ingredient.total_quantity and create history"""
```

### Auto-Create Notifications
```python
@receiver(post_save, sender=Ingredient)
def create_low_stock_notification(sender, instance, **kwargs):
    """If total_quantity < low_stock_threshold, create notification"""
```

---

## 9. HELPER UTILITIES

### File: api/utils/generators.py
```python
def generate_employee_id():
    """Generate EMP-001, EMP-002, etc."""
    
def generate_product_id():
    """Generate #PROD-1001, #PROD-1002, etc."""
    
def generate_ingredient_id():
    """Generate #I001, #I002, etc."""
    
def generate_bill_number():
    """Generate BILL-1001, BILL-1002, etc."""
    
def generate_batch_id():
    """Generate BATCH-1001, BATCH-1002, etc."""
```

### File: api/utils/calculations.py
```python
def calculate_profit_margin(cost_price, selling_price):
    """Calculate (selling - cost) / cost * 100"""
    
def calculate_discount_amount(subtotal, discount_type, discount_value):
    """If Percentage: subtotal * value / 100, If FixedAmount: value"""
    
def calculate_inventory_value(products, ingredients):
    """Sum of (qty * cost_price) for all items"""
    
def is_discount_applicable(discount, product, current_datetime):
    """Check date, time, and applicability"""
```

### File: api/utils/validators.py
```python
def validate_contact_format(value):
    """Validate: XXX-XXXXXXX"""
    
def validate_dates(start_date, end_date):
    """Ensure start <= end"""
    
def validate_times(start_time, end_time):
    """Ensure start < end"""
    
def validate_positive_decimal(value):
    """Ensure value >= 0"""
```

---

## 10. SETTINGS.PY CONFIGURATION

### INSTALLED_APPS
```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'corsheaders',
    'drf_spectacular',
    'django_filters',
    'api',
]
```

### MIDDLEWARE
```python
MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
]
```

### REST_FRAMEWORK
```python
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'DEFAULT_FILTER_BACKENDS': ['django_filters.rest_framework.DjangoFilterBackend'],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
}
```

### CORS
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
]
```

---

## 11. CELERY TASKS

```python
# api/tasks.py
from celery import shared_task
from django.utils.timezone import now
from datetime import timedelta

@shared_task
def check_low_stock_alerts():
    """Run hourly to check low stock ingredients"""
    low_ingredients = Ingredient.objects.filter(
        total_quantity__lt=F('low_stock_threshold')
    )
    # Create notifications
    
@shared_task
def check_expiry_alerts():
    """Run hourly to check expiring batches"""
    expiring = IngredientBatch.objects.filter(
        expire_date__lte=now() + timedelta(days=2)
    )
    # Create notifications
    
@shared_task
def check_daily_wastage_alerts():
    """Run daily to check high wastage"""
    # Calculate daily wastage % and alert if > 5%
```

---

## 12. TESTING STRUCTURE

### test_auth.py
```python
class AuthTestCase(TestCase):
    def test_login_success(self): ...
    def test_invalid_credentials(self): ...
    def test_token_refresh(self): ...
    def test_me_endpoint(self): ...

class PermissionTestCase(TestCase):
    def test_manager_access(self): ...
    def test_cashier_restricted_access(self): ...
    def test_unauthorized_user(self): ...
```

### test_sales.py
```python
class SaleCreationTestCase(TestCase):
    def test_sale_creation_valid(self): ...
    def test_insufficient_stock(self): ...
    def test_discount_calculation(self): ...
    def test_stock_deduction(self): ...
    def test_stock_history_created(self): ...
```

---

## 13. DEPLOYMENT CHECKLIST

### Pre-Deployment
- [ ] All migrations applied
- [ ] Tests passing (80%+ coverage)
- [ ] No hardcoded credentials
- [ ] Environment variables configured
- [ ] Database backed up
- [ ] Static files collected
- [ ] CORS configured for production
- [ ] DEBUG = False

### Docker Setup
- [ ] Dockerfile created
- [ ] docker-compose.yml created
- [ ] Gunicorn configured
- [ ] Nginx configuration
- [ ] SSL certificate setup

### Post-Deployment
- [ ] Test all endpoints
- [ ] Monitor logs
- [ ] Verify database connection
- [ ] Check API responses
- [ ] Smoke tests on critical paths

---

## 14. USEFUL DJANGO COMMANDS

```bash
# Create new app
python manage.py startapp myapp

# Make migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver

# Load fixture data
python manage.py loaddata fixture.json

# Dump data
python manage.py dumpdata > backup.json

# Shell
python manage.py shell

# Run tests
python manage.py test
pytest
pytest --cov=api
```

---

## 15. QUICK TROUBLESHOOTING

| Issue | Solution |
|-------|----------|
| CORS error | Check CORS_ALLOWED_ORIGINS in settings |
| 401 Unauthorized | Verify JWT token in Authorization header |
| 403 Forbidden | Check user role/permissions |
| 404 Not Found | Verify URL and check urls.py routing |
| Validation error | Check serializer fields and validators |
| Migration fails | Drop table and re-migrate, or create new migration |
| Signal not firing | Check signal is connected and imports are correct |
| Pagination not working | Verify DEFAULT_PAGINATION_CLASS in settings |
| Search not working | Check DjangoFilterBackend in filters |

---

**Last Updated:** March 22, 2026  
**Version:** 1.0
