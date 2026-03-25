# 🗄️ BakeryOS - Complete Corrected Database Schema

## Overview
This is the **final production-ready database schema** for BakeryOS, incorporating all corrections and suggestions. Built for Django ORM + PostgreSQL.

---

## 1. 🔐 User & Authentication

### Table: `users` (extends Django AbstractUser)

| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique user identifier |
| `employee_id` | VARCHAR(50) | UNIQUE, NOT NULL | e.g., `EMP-001` |
| `full_name` | VARCHAR(255) | NOT NULL | Employee's full name |
| `username` | VARCHAR(150) | UNIQUE, NOT NULL | Login username |
| `password_hash` | VARCHAR(255) | NOT NULL | Django's bcrypt hash |
| `nic` | VARCHAR(20) | UNIQUE, NULL | National ID (optional) |
| `contact` | VARCHAR(20) | NOT NULL | Phone number, validated format |
| `role` | ENUM | NOT NULL | `Manager` / `Cashier` / `Baker` / `Storekeeper` |
| `status` | ENUM | NOT NULL DEFAULT `Active` | `Active` / `Inactive` |
| `avatar_color` | VARCHAR(50) | NULL | e.g., `bg-purple-600` |
| `last_login` | DATETIME | NULL, AUTO_UPDATE | Last successful login |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Record creation |
| `updated_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP, AUTO_UPDATE | Last modification |
| `is_active` | BOOLEAN | DEFAULT TRUE | Django built-in soft delete flag |

**Indexes:**
```sql
CREATE UNIQUE INDEX idx_users_employee_id ON users(employee_id);
CREATE UNIQUE INDEX idx_users_username ON users(username);
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_status ON users(status);
```

**Check Constraints:**
```sql
ALTER TABLE users ADD CHECK (contact ~ '^\d{3}-\d{7}$'); -- Sri Lankan format
ALTER TABLE users ADD CHECK (role IN ('Manager', 'Cashier', 'Baker', 'Storekeeper'));
```

---

## 2. 🗂️ Categories

### Table: `categories`

| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique identifier |
| `category_id` | VARCHAR(50) | UNIQUE, NOT NULL | e.g., `CAT-P001` (Product) or `CAT-I001` (Ingredient) |
| `name` | VARCHAR(255) | NOT NULL | Category name (e.g., `Buns`, `Flour`) |
| `type` | ENUM | NOT NULL | `Product` / `Ingredient` |
| `description` | TEXT | NULL | Optional description |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | |
| `updated_at` | DATETIME | NOT NULL, AUTO_UPDATE | |

**Indexes:**
```sql
CREATE UNIQUE INDEX idx_categories_category_id ON categories(category_id);
CREATE UNIQUE INDEX idx_categories_type_name ON categories(type, name);
CREATE INDEX idx_categories_type ON categories(type);
```

---

## 3. 📦 Inventory (Raw Materials & Stocks)

### Table: `ingredients`

| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique identifier |
| `ingredient_id` | VARCHAR(50) | UNIQUE, NOT NULL | e.g., `#I001` |
| `category_id` | INTEGER | FOREIGN KEY → categories | Ingredient category |
| `name` | VARCHAR(255) | NOT NULL | Ingredient name |
| `supplier` | VARCHAR(255) | NOT NULL | Supplier name |
| `supplier_contact` | VARCHAR(20) | NULL | Supplier phone |
| `tracking_type` | ENUM | NOT NULL | `Weight` / `Volume` / `Count` |
| `base_unit` | VARCHAR(20) | NOT NULL | `g` / `ml` / `nos` (ALL values stored in this unit) |
| `total_quantity` | DECIMAL(14,3) | NOT NULL, DEFAULT 0 | Running total (in base_unit). **Synced via Django Signals** |
| `low_stock_threshold` | DECIMAL(14,3) | NOT NULL CHECK (>= 0) | Alert trigger (in base_unit) |
| `shelf_life` | INTEGER | NULL | Duration value |
| `shelf_unit` | VARCHAR(20) | NULL | `Days` / `Hours` / `Months` |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | |
| `updated_at` | DATETIME | NOT NULL, AUTO_UPDATE | |

**Indexes:**
```sql
CREATE UNIQUE INDEX idx_ingredients_ingredient_id ON ingredients(ingredient_id);
CREATE INDEX idx_ingredients_category_id ON ingredients(category_id);
CREATE INDEX idx_ingredients_name ON ingredients(name);
CREATE INDEX idx_ingredients_supplier ON ingredients(supplier);
```

**Rational for `base_unit` & `total_quantity`:**
- All ingredient amounts are stored in a single base unit (e.g., all flour in grams, not sometimes kg, sometimes g).
- Conversion happens at API layer only → no calculation errors in database.
- `total_quantity` is denormalized for dashboard speed; kept in sync via Django Signal when batches are added/removed.

---

### Table: `ingredient_batches` (GRN - Goods Received Notes)

| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Auto-incremented internal PK |
| `batch_id` | VARCHAR(50) | UNIQUE, NOT NULL | e.g., `BATCH-1001` (business identifier) |
| `ingredient_id` | INTEGER | FOREIGN KEY → ingredients | Received ingredient |
| `quantity` | DECIMAL(14,3) | NOT NULL, CHECK (> 0) | Total received (in base_unit) |
| `current_qty` | DECIMAL(14,3) | NOT NULL, CHECK (>= 0) | Remaining quantity (in base_unit) |
| `cost_price` | DECIMAL(12,2) | NOT NULL, CHECK (>= 0) | Cost per single base unit |
| `made_date` | DATETIME | NOT NULL | Manufactured date |
| `expire_date` | DATETIME | NOT NULL | Expiry date |
| `status` | ENUM | NOT NULL DEFAULT `Active` | `Active` / `Expired` / `Used` |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | |
| `updated_at` | DATETIME | NOT NULL, AUTO_UPDATE | |

**Indexes:**
```sql
CREATE UNIQUE INDEX idx_ingredient_batches_batch_id ON ingredient_batches(batch_id);
CREATE INDEX idx_ingredient_batches_ingredient_id ON ingredient_batches(ingredient_id);
CREATE INDEX idx_ingredient_batches_expire_date ON ingredient_batches(expire_date);
CREATE INDEX idx_ingredient_batches_status ON ingredient_batches(status);
```

**Check Constraints:**
```sql
ALTER TABLE ingredient_batches ADD CHECK (current_qty <= quantity);
ALTER TABLE ingredient_batches ADD CHECK (made_date <= expire_date);
```

---

## 4. 🥐 Production (Finished Goods & Recipes)

### Table: `products`

| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique identifier |
| `product_id` | VARCHAR(50) | UNIQUE, NOT NULL | e.g., `#PROD-1001` |
| `category_id` | INTEGER | FOREIGN KEY → categories | Product category |
| `name` | VARCHAR(255) | NOT NULL | Product name |
| `cost_price` | DECIMAL(12,2) | NOT NULL, CHECK (>= 0) | Cost to produce (calculated from recipe) |
| `selling_price` | DECIMAL(12,2) | NOT NULL, CHECK (>= 0) | Selling price |
| `current_stock` | INTEGER | NOT NULL DEFAULT 0, CHECK (>= 0) | Available for sale (pieces) |
| `shelf_life` | INTEGER | NULL | Duration value |
| `shelf_unit` | VARCHAR(20) | NULL | `Days` / `Hours` / `Months` |
| `image_url` | VARCHAR(500) | NULL | Product image URL |
| `description` | TEXT | NULL | Product description |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | |
| `updated_at` | DATETIME | NOT NULL, AUTO_UPDATE | |

**Indexes:**
```sql
CREATE UNIQUE INDEX idx_products_product_id ON products(product_id);
CREATE INDEX idx_products_category_id ON products(category_id);
CREATE INDEX idx_products_name ON products(name);
```

---

### Table: `recipe_items` (Product Recipe Composition)

| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique identifier |
| `product_id` | INTEGER | FOREIGN KEY → products | Which product |
| `ingredient_id` | INTEGER | FOREIGN KEY → ingredients | Which ingredient |
| `quantity_required` | DECIMAL(14,3) | NOT NULL, CHECK (> 0) | Required amount (in base_unit) |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | |
| `updated_at` | DATETIME | NOT NULL, AUTO_UPDATE | |

**Indexes & Constraints:**
```sql
CREATE UNIQUE INDEX idx_recipe_items_product_ingredient ON recipe_items(product_id, ingredient_id);
CREATE INDEX idx_recipe_items_ingredient_id ON recipe_items(ingredient_id);
```

**Rationale:**
- Unique constraint ensures no duplicate ingredient in same recipe.
- quantity_required is in ingredient's base_unit → no conversion errors.

---

### Table: `product_batches` (Baker Production)

| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Auto-incremented internal PK |
| `batch_id` | VARCHAR(50) | UNIQUE, NOT NULL | e.g., `PROD-BATCH-1001` |
| `product_id` | INTEGER | FOREIGN KEY → products | Which product produced |
| `quantity` | INTEGER | NOT NULL, CHECK (> 0) | Quantity produced (pieces) |
| `made_date` | DATETIME | NOT NULL | Production timestamp |
| `expire_date` | DATETIME | NOT NULL | Expiry calculated from shelf_life |
| `notes` | TEXT | NULL | Production notes |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | |
| `updated_at` | DATETIME | NOT NULL, AUTO_UPDATE | |

**Indexes:**
```sql
CREATE UNIQUE INDEX idx_product_batches_batch_id ON product_batches(batch_id);
CREATE INDEX idx_product_batches_product_id ON product_batches(product_id);
CREATE INDEX idx_product_batches_expire_date ON product_batches(expire_date);
```

---

## 5. 🛒 POS, Sales & Discounts

### Table: `sales` (Bill Header)

| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Internal PK |
| `bill_number` | VARCHAR(50) | UNIQUE, NOT NULL | e.g., `BILL-1001` (POS display) |
| `cashier_id` | INTEGER | FOREIGN KEY → users | Cashier who processed |
| `subtotal` | DECIMAL(12,2) | NOT NULL, CHECK (>= 0) | Sum before discount |
| `discount_id` | INTEGER | FOREIGN KEY → discounts (NULL) | Applied discount (if any) |
| `discount_amount` | DECIMAL(12,2) | NOT NULL DEFAULT 0, CHECK (>= 0) | Discount value applied |
| `total_amount` | DECIMAL(12,2) | NOT NULL, CHECK (>= 0) | subtotal - discount_amount |
| `payment_method` | ENUM | NOT NULL | `Cash` / `Card` |
| `date_time` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | Transaction timestamp |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | |
| `updated_at` | DATETIME | NOT NULL, AUTO_UPDATE | |

**Indexes:**
```sql
CREATE UNIQUE INDEX idx_sales_bill_number ON sales(bill_number);
CREATE INDEX idx_sales_cashier_id ON sales(cashier_id);
CREATE INDEX idx_sales_date_time ON sales(date_time);
CREATE INDEX idx_sales_payment_method ON sales(payment_method);
```

---

### Table: `sale_items` (Bill Line Items)

| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique identifier |
| `sale_id` | INTEGER | FOREIGN KEY → sales | Parent bill |
| `product_id` | INTEGER | FOREIGN KEY → products | Which product sold |
| `quantity` | INTEGER | NOT NULL, CHECK (> 0) | Units sold |
| `unit_price` | DECIMAL(12,2) | NOT NULL, CHECK (>= 0) | **Frozen price** — price at checkout time (never changes) |
| `subtotal` | DECIMAL(12,2) | NOT NULL, CHECK (>= 0) | quantity × unit_price |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | |

**Indexes:**
```sql
CREATE INDEX idx_sale_items_sale_id ON sale_items(sale_id);
CREATE INDEX idx_sale_items_product_id ON sale_items(product_id);
```

**Rationale:**
- `unit_price` is immutable — even if product.selling_price changes tomorrow, this bill retains correct price.
- Frontend captures price at `addToCart()` time; Backend validates and stores a frozen copy.

---

### Table: `discounts`

| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique identifier |
| `discount_id` | VARCHAR(50) | UNIQUE, NOT NULL | e.g., `DISC-001` |
| `name` | VARCHAR(255) | NOT NULL | e.g., `Happy Hour` |
| `type` | ENUM | NOT NULL | `Percentage` / `FixedAmount` |
| `value` | DECIMAL(12,2) | NOT NULL, CHECK (> 0) | 50 (for 50%) or 150 (for Rs.150) |
| `applicable_to` | ENUM | NOT NULL | `All` / `Category` / `Product` |
| `target_category_id` | INTEGER | FOREIGN KEY → categories (NULL) | If applicable_to = `Category` |
| `target_product_id` | INTEGER | FOREIGN KEY → products (NULL) | If applicable_to = `Product` |
| `start_date` | DATE | NULL | Validity start date |
| `end_date` | DATE | NULL | Validity end date |
| `start_time` | TIME | NULL | Daily start time (e.g., `20:00:00` for 8 PM) |
| `end_time` | TIME | NULL | Daily end time (e.g., `21:00:00` for 9 PM) |
| `is_active` | BOOLEAN | NOT NULL DEFAULT TRUE | Discount enabled/disabled |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | |
| `updated_at` | DATETIME | NOT NULL, AUTO_UPDATE | |

**Indexes:**
```sql
CREATE UNIQUE INDEX idx_discounts_discount_id ON discounts(discount_id);
CREATE INDEX idx_discounts_applicable_to ON discounts(applicable_to);
CREATE INDEX idx_discounts_target_category_id ON discounts(target_category_id);
CREATE INDEX idx_discounts_target_product_id ON discounts(target_product_id);
CREATE INDEX idx_discounts_is_active ON discounts(is_active);
```

**Check Constraints:**
```sql
-- Ensure only one target is set based on applicable_to
ALTER TABLE discounts ADD CHECK (
  (applicable_to = 'All' AND target_category_id IS NULL AND target_product_id IS NULL)
  OR (applicable_to = 'Category' AND target_category_id IS NOT NULL AND target_product_id IS NULL)
  OR (applicable_to = 'Product' AND target_product_id IS NOT NULL AND target_category_id IS NULL)
);

-- Ensure dates are logical
ALTER TABLE discounts ADD CHECK (start_date IS NULL OR end_date IS NULL OR start_date <= end_date);

-- Ensure times are logical
ALTER TABLE discounts ADD CHECK (start_time IS NULL OR end_time IS NULL OR start_time < end_time);
```

**Rationale:**
- Split target_category_id and target_product_id instead of polymorphic item_type + item_id.
- CHECK constraint ensures data integrity at database level.
- Easier debugging and referential integrity.

---

## 6. 🗑️ Wastage & Tracking

### ⚠️ **CRITICAL FIX:** Split Wastage into Two Tables

Instead of a single `wastages` table with polymorphic `item_type + item_id`, we use two dedicated tables for referential integrity.

---

### Table: `product_wastages`

| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique identifier |
| `wastage_id` | VARCHAR(50) | UNIQUE, NOT NULL | e.g., `PW-001` |
| `product_id` | INTEGER | FOREIGN KEY → products | Which product wasted |
| `quantity` | INTEGER | NOT NULL, CHECK (> 0) | Wasted units |
| `unit_cost` | DECIMAL(12,2) | NOT NULL, CHECK (>= 0) | Loss value per unit at time of wastage |
| `total_loss` | DECIMAL(12,2) | NOT NULL, CHECK (>= 0) | quantity × unit_cost |
| `reason_id` | INTEGER | FOREIGN KEY → wastage_reasons | Why wasted |
| `reported_by` | INTEGER | FOREIGN KEY → users | Staff who reported |
| `notes` | TEXT | NULL | Additional details |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | |
| `updated_at` | DATETIME | NOT NULL, AUTO_UPDATE | |

**Indexes:**
```sql
CREATE UNIQUE INDEX idx_product_wastages_wastage_id ON product_wastages(wastage_id);
CREATE INDEX idx_product_wastages_product_id ON product_wastages(product_id);
CREATE INDEX idx_product_wastages_reason_id ON product_wastages(reason_id);
CREATE INDEX idx_product_wastages_reported_by ON product_wastages(reported_by);
CREATE INDEX idx_product_wastages_created_at ON product_wastages(created_at);
```

---

### Table: `ingredient_wastages`

| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique identifier |
| `wastage_id` | VARCHAR(50) | UNIQUE, NOT NULL | e.g., `IW-001` |
| `ingredient_id` | INTEGER | FOREIGN KEY → ingredients | Which ingredient wasted |
| `batch_id` | INTEGER | FOREIGN KEY → ingredient_batches (NULL) | If from specific batch |
| `quantity` | DECIMAL(14,3) | NOT NULL, CHECK (> 0) | Wasted amount (in base_unit) |
| `unit_cost` | DECIMAL(12,2) | NOT NULL, CHECK (>= 0) | Loss value per unit at time of wastage |
| `total_loss` | DECIMAL(12,2) | NOT NULL, CHECK (>= 0) | quantity × unit_cost |
| `reason_id` | INTEGER | FOREIGN KEY → wastage_reasons | Why wasted |
| `reported_by` | INTEGER | FOREIGN KEY → users | Staff who reported |
| `notes` | TEXT | NULL | Additional details |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | |
| `updated_at` | DATETIME | NOT NULL, AUTO_UPDATE | |

**Indexes:**
```sql
CREATE UNIQUE INDEX idx_ingredient_wastages_wastage_id ON ingredient_wastages(wastage_id);
CREATE INDEX idx_ingredient_wastages_ingredient_id ON ingredient_wastages(ingredient_id);
CREATE INDEX idx_ingredient_wastages_batch_id ON ingredient_wastages(batch_id);
CREATE INDEX idx_ingredient_wastages_reason_id ON ingredient_wastages(reason_id);
CREATE INDEX idx_ingredient_wastages_reported_by ON ingredient_wastages(reported_by);
CREATE INDEX idx_ingredient_wastages_created_at ON ingredient_wastages(created_at);
```

---

### Table: `wastage_reasons`

| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique identifier |
| `reason_id` | VARCHAR(50) | UNIQUE, NOT NULL | e.g., `WR-001` |
| `reason` | VARCHAR(255) | NOT NULL, UNIQUE | e.g., `Expired`, `Damaged`, `Spilled`, `Theft` |
| `description` | TEXT | NULL | Detailed description |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | |

**Indexes:**
```sql
CREATE UNIQUE INDEX idx_wastage_reasons_reason_id ON wastage_reasons(reason_id);
CREATE UNIQUE INDEX idx_wastage_reasons_reason ON wastage_reasons(reason);
```

---

## 7. 📊 Audit Log & Notifications

### Table: `product_stock_history` (Audit Trail for Products)

| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique identifier |
| `product_id` | INTEGER | FOREIGN KEY → products | Which product |
| `transaction_type` | ENUM | NOT NULL | `AddStock` / `UseStock` / `Wastage` / `Adjustment` |
| `qty_before` | INTEGER | NOT NULL, CHECK (>= 0) | Stock before transaction |
| `qty_after` | INTEGER | NOT NULL, CHECK (>= 0) | Stock after transaction |
| `change_amount` | INTEGER | NOT NULL | Delta (e.g., -2, +50) |
| `performed_by` | INTEGER | FOREIGN KEY → users | Staff who made the change |
| `reference_id` | VARCHAR(100) | NULL | Link to sale/wastage/batch ID |
| `notes` | TEXT | NULL | Additional context |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | |

**Indexes:**
```sql
CREATE INDEX idx_product_stock_history_product_id ON product_stock_history(product_id);
CREATE INDEX idx_product_stock_history_performed_by ON product_stock_history(performed_by);
CREATE INDEX idx_product_stock_history_transaction_type ON product_stock_history(transaction_type);
CREATE INDEX idx_product_stock_history_created_at ON product_stock_history(created_at);
```

---

### Table: `ingredient_stock_history` (Audit Trail for Ingredients)

| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique identifier |
| `ingredient_id` | INTEGER | FOREIGN KEY → ingredients | Which ingredient |
| `transaction_type` | ENUM | NOT NULL | `AddStock` / `UseStock` / `Wastage` / `Adjustment` |
| `qty_before` | DECIMAL(14,3) | NOT NULL, CHECK (>= 0) | Stock before (in base_unit) |
| `qty_after` | DECIMAL(14,3) | NOT NULL, CHECK (>= 0) | Stock after (in base_unit) |
| `change_amount` | DECIMAL(14,3) | NOT NULL | Delta in base_unit |
| `performed_by` | INTEGER | FOREIGN KEY → users | Staff who made the change |
| `reference_id` | VARCHAR(100) | NULL | Link to batch/recipe/wastage ID |
| `notes` | TEXT | NULL | Additional context |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | |

**Indexes:**
```sql
CREATE INDEX idx_ingredient_stock_history_ingredient_id ON ingredient_stock_history(ingredient_id);
CREATE INDEX idx_ingredient_stock_history_performed_by ON ingredient_stock_history(performed_by);
CREATE INDEX idx_ingredient_stock_history_transaction_type ON ingredient_stock_history(transaction_type);
CREATE INDEX idx_ingredient_stock_history_created_at ON ingredient_stock_history(created_at);
```

**Rationale:**
- Split into product and ingredient history (not polymorphic) for clarity.
- Every change is logged for audit trail and debugging.
- `reference_id` allows traceability (e.g., which sale caused stock change).

---

### Table: `notifications`

| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique identifier |
| `title` | VARCHAR(255) | NOT NULL | e.g., `Low Stock Alert` |
| `message` | TEXT | NOT NULL | e.g., `Sugar is below threshold` |
| `type` | ENUM | NOT NULL | `LowStock` / `Expiry` / `System` / `Warning` |
| `icon` | VARCHAR(100) | NULL | Icon name for frontend |
| `is_read` | BOOLEAN | NOT NULL DEFAULT FALSE | **DEPRECATED** — use `notification_receipts` |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | |

**Indexes:**
```sql
CREATE INDEX idx_notifications_type ON notifications(type);
CREATE INDEX idx_notifications_created_at ON notifications(created_at DESC);
```

**⚠️ IMPORTANT:** The `is_read` field is now deprecated. Use `notification_receipts` below for per-user read tracking.

---

### Table: `notification_receipts` (Per-User Read Status)

| Column Name | Data Type | Constraints | Description |
|---|---|---|---|
| `id` | INTEGER | PRIMARY KEY, AUTO_INCREMENT | Unique identifier |
| `notification_id` | INTEGER | FOREIGN KEY → notifications | Which notification |
| `user_id` | INTEGER | FOREIGN KEY → users | Which user receives it |
| `is_read` | BOOLEAN | NOT NULL DEFAULT FALSE | Read by this user? |
| `read_at` | DATETIME | NULL | When user read it |
| `created_at` | DATETIME | NOT NULL, DEFAULT CURRENT_TIMESTAMP | When created |

**Indexes:**
```sql
CREATE UNIQUE INDEX idx_notification_receipts_unique ON notification_receipts(notification_id, user_id);
CREATE INDEX idx_notification_receipts_user_id ON notification_receipts(user_id);
CREATE INDEX idx_notification_receipts_is_read ON notification_receipts(is_read);
```

**Rationale:**
- One notification can be read by many users.
- Each user can track independent read status.
- Solves scalability: broadcast one message, many receipts.
- Example: "Low Stock Alert" for Sugar sent to Manager, Baker, Storekeeper — each tracks own read status.

---

## 8. 📋 Summary of Key Improvements

| Issue | Original | Corrected | Benefit |
|---|---|---|---|
| **Wastage Structure** | Polymorphic (item_type + item_id) | Split tables (product_wastages, ingredient_wastages) | True FK constraints, better integrity |
| **Discounts Target** | Loose string (target_id) | Split FKs + CHECK constraint | No orphaned records, verified targets |
| **Notifications Read** | Single is_read field | notification_receipts table | Handles multiple users, proper tracking |
| **Stock Audit** | Polymorphic stock_history | Split tables (product/ingredient_stock_history) | Clear, indexable, type-safe |
| **Ingredient Units** | Inconsistent units in DB | Base unit + conversions at API | No calculation errors, consistent math |
| **Audit Columns** | Missing | created_at, updated_at everywhere | Compliance, debugging, soft delete support |
| **Constraints** | Loose | CHECK constraints, UNIQUE as needed | Data quality, early error detection |
| **Indexes** | Minimal | Comprehensive on FKs, dates, business IDs | Fast queries, dashboard performance |

---

## 9. Django ORM Integration Notes

### Creating Models

```python
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator

# Example for base_unit concept
class Ingredient(models.Model):
    BASE_UNITS = [
        ('g', 'Grams'),
        ('ml', 'Milliliters'),
        ('nos', 'Numbers'),
    ]
    
    ingredient_id = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    base_unit = models.CharField(max_length=20, choices=BASE_UNITS)
    total_quantity = models.DecimalField(max_digits=14, decimal_places=3, default=0)
    # ... other fields
    
    class Meta:
        indexes = [
            models.Index(fields=['ingredient_id']),
            models.Index(fields=['category_id']),
        ]

# Signals to keep total_quantity in sync
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

@receiver([post_save, post_delete], sender=IngredientBatch)
def sync_ingredient_total_quantity(sender, instance, **kwargs):
    ingredient = instance.ingredient
    ingredient.total_quantity = ingredient.batches.aggregate(
        total=models.Sum('current_qty')
    )['total'] or 0
    ingredient.save(update_fields=['total_quantity'])
```

### Running Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 10. Frontend Data Flow Example

### Checkout API Call (from React)

```json
POST /api/sales/

{
  "bill_number": "BILL-1042",
  "payment_method": "Cash",
  "items": [
    {
      "product_id": 3,
      "quantity": 2,
      "unit_price": 80.00
    }
  ]
}
```

**Backend Response:**
```json
{
  "id": 142,
  "bill_number": "BILL-1042",
  "subtotal": 160.00,
  "discount_amount": 0,
  "total_amount": 160.00,
  "payment_method": "Cash",
  "date_time": "2026-03-22T14:30:00Z",
  "sale_items": [
    {
      "product_id": 3,
      "quantity": 2,
      "unit_price": 80.00,
      "subtotal": 160.00
    }
  ]
}
```

---

## Conclusion

This schema is **production-ready** for Django + PostgreSQL. It includes:

✅ All original functionality  
✅ Referential integrity (true FKs, no polymorphism)  
✅ Audit trails for compliance  
✅ Proper scaling for read-per-user notifications  
✅ Base unit consistency for ingredient calculations  
✅ Frozen prices for bill immutability  
✅ Comprehensive indexes for performance  
✅ Check constraints for data quality  
✅ Standard created_at/updated_at columns  

---

*Last Updated: March 22, 2026*
