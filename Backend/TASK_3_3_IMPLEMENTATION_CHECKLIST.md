# Task 3.3 - Ingredient Batch Management - Implementation Checklist

**Estimated Duration:** 4 hours  
**Difficulty:** Medium  
**Dependencies:** Task 3.1 ✅ & Task 3.2 ✅ Complete

---

## 📋 Overview

This task implements batch-level tracking for ingredients, enabling quantity management, expiry date tracking, and FIFO (First-In-First-Out) consumption logic.

### Key Goals
1. ✅ Create IngredientBatch model with auto-ID (#B001...)
2. ✅ Implement CRUD API for batch management
3. ✅ Auto-sync Ingredient.total_quantity when batches change
4. ✅ Track remaining quantity per batch
5. ✅ Expiry date management with calculated fields
6. ✅ Batch history & audit trail
7. ✅ FIFO selection for consumption
8. ✅ Comprehensive testing

---

## 🎯 Deliverables Checklist

### 1. IngredientBatch Model
- [ ] Create model with auto-ID generation (#B001 format)
- [ ] Fields:
  - `batch_id` (CharField, unique, auto)
  - `ingredient_id` (FK → Ingredient)
  - `quantity_received` (DecimalField)
  - `cost_per_unit` (DecimalField, optional)
  - `received_date` (DateTimeField, auto=now)
  - `expiry_date` (DateTimeField)
  - `supplier_batch_id` (CharField, optional)
  - `batch_notes` (TextField, optional)
  - `is_expired` (BooleanField, auto-calc)
  - `remaining_quantity` (DecimalField, calculated)
  - `is_active` (BooleanField, soft delete)
  - Timestamps: `created_at`, `updated_at`
- [ ] Add constraints:
  - `quantity_received > 0`
  - `expiry_date >= received_date`
  - `cost_per_unit > 0` (if provided)
- [ ] Computed properties:
  - `is_expired` → `expiry_date < today`
  - `days_until_expiry` → days remaining
  - `remaining_quantity` → tracking via signals
- [ ] Ordering: `expiry_date` (asc) for FIFO
- [ ] Indexes:
  - `ingredient_id + is_active`
  - `expiry_date` (for expiry alerts)
  - `is_expired`

### 2. Signals for Auto-Sync
- [ ] Create signal handler in `apps.py`:
  ```python
  @receiver(post_save, sender=IngredientBatch)
  def sync_ingredient_quantity(sender, instance, **kwargs):
      # Sum all active batch remaining_quantities
      # Update Ingredient.total_quantity
  
  @receiver(post_delete, sender=IngredientBatch)
  def sync_ingredient_quantity_delete(sender, instance, **kwargs):
      # Same as above
  ```
- [ ] Signal triggered on:
  - New batch created
  - Batch quantity updated
  - Batch marked as consumed/expired
  - Batch deleted (soft delete)

### 3. Serializers
- [ ] `BatchSerializer` - List view
  - Fields: id, batch_id, ingredient_id, ingredient_name, quantity_received
  - Fields: received_date, expiry_date, days_until_expiry, is_expired
  - Fields: remaining_quantity, cost_per_unit, supplier_batch_id, is_active
- [ ] `BatchDetailSerializer` - Full details
  - All fields from above
  - Add computed field: `status` (ACTIVE, CONSUMED, EXPIRED, DAMAGED)
  - Add: `total_cost` (quantity_received × cost_per_unit)
- [ ] `BatchCreateUpdateSerializer` - Custom validation
  - Validate: quantity_received > 0
  - Validate: expiry_date >= received_date
  - Validate: cost_per_unit > 0 (if provided)
  - Accept ingredient_id, don't allow changing after creation
- [ ] `BatchInventorySerializer` - Minimal for inventory views
  - Fields: batch_id, remaining_quantity, expiry_date, is_expired

### 4. ViewSet & Endpoints
- [ ] Create `BatchViewSet` in views.py:
- [ ] Endpoints:
  ```
  GET    /api/batches/                    # List all (filtered, paginated)
  POST   /api/batches/                    # Create new batch
  GET    /api/batches/{id}/               # Batch details
  PATCH  /api/batches/{id}/               # Partial update (quantity, notes)
  DELETE /api/batches/{id}/               # Soft delete / mark expired
  GET    /api/batches/by_ingredient/      # Batches for ingredient (FIFO order)
  GET    /api/batches/expiring_soon/      # Expiring within X days (default 7)
  GET    /api/batches/expired/            # Expired batches
  POST   /api/batches/{id}/consume/       # Consume from batch
  GET    /api/batches/{id}/history/       # Batch consumption history (future)
  ```
- [ ] Filtering:
  - `ingredient_id` - Filter by ingredient
  - `is_active` - Filter by status
  - `is_expired` - Filter expired
  - `received_after` / `received_before` - Date range
  - `expiry_before` - Expiry date filter
  - `supplier_id` - Filter by supplier
- [ ] Ordering:
  - Default: `expiry_date` (FIFO)
  - Sortable by: `received_date`, `expiry_date`, `remaining_quantity`
- [ ] Search:
  - `batch_id`
  - `supplier_batch_id`
  - `ingredient__name`

### 5. Permissions
- [ ] Batch View: All authenticated users
- [ ] Create: Manager, Storekeeper
- [ ] Update: Manager, Storekeeper (limited fields)
- [ ] Delete/Consume: Manager, Storekeeper
- [ ] Create custom permission class for "can_consume_batch"

### 6. Business Logic

#### Stock Consumption Logic
- [ ] Implement FIFO consumption:
  ```python
  def get_fifo_batch(ingredient_id, quantity_needed):
      # Get oldest non-expired batch with remaining quantity
      batch = IngredientBatch.objects.filter(
          ingredient_id=ingredient_id,
          is_active=True,
          is_expired=False,
          remaining_quantity__gt=0
      ).order_by('expiry_date').first()
      return batch
  ```
- [ ] Validation before consumption:
  - Check ingredient not in use (by ProductionBatch) - future
  - Check quantity available in FIFO
  - Check batch not expired
- [ ] Update remaining_quantity when consumed
- [ ] Trigger signal to recalc ingredient total

#### Expiry Management
- [ ] Auto-mark as expired if current_date >= expiry_date
- [ ] Calculate `days_until_expiry` (can be negative)
- [ ] Implement `expiring_soon/` endpoint with configurable days

#### Cost Tracking (Optional, nice-to-have)
- [ ] Calculate `total_cost` = quantity_received × cost_per_unit
- [ ] Track cost per ingredient (average cost)
- [ ] Prepare for future cost analysis

### 7. URL Routing
- [ ] Add to `api/urls.py`:
  ```python
  from api.views import BatchViewSet
  
  router = DefaultRouter()
  router.register(r'batches', BatchViewSet, basename='batch')
  ```
- [ ] Final routes:
  ```
  GET /api/batches/
  POST /api/batches/
  GET /api/batches/{id}/
  PATCH /api/batches/{id}/
  DELETE /api/batches/{id}/
  GET /api/batches/by_ingredient/
  GET /api/batches/expiring_soon/
  GET /api/batches/expired/
  POST /api/batches/{id}/consume/
  ```

### 8. Database Migration
- [ ] Create migration:
  ```bash
  python manage.py makemigrations
  ```
- [ ] Review migration file
- [ ] Apply migration:
  ```bash
  python manage.py migrate
  ```
- [ ] Verify table created in SQLite

### 9. Seed Data (Optional)
- [ ] Create `management/commands/seed_batches.py`
- [ ] Add 2-3 batches per ingredient
- [ ] Vary expiry dates:
  - Some already expired (past dates)
  - Some expiring soon (within 7 days)
  - Some healthy (30+ days remaining)
- [ ] Existing ingredients: #I001 to #I018
- [ ] Sample batch IDs: #B001, #B002, etc.
- [ ] Command: `python manage.py seed_batches`

### 10. Testing
- [ ] Create `test_batches_endpoints.py`:
  - [ ] Test list batches (10+ items)
  - [ ] Test create batch (valid & invalid)
  - [ ] Test get batch details
  - [ ] Test update batch (PATCH)
  - [ ] Test delete batch (soft delete)
  - [ ] Test filter by ingredient
  - [ ] Test expiring_soon endpoint
  - [ ] Test expired endpoint
  - [ ] Test stock consumption logic
  - [ ] Test quantity sync to ingredient
  - [ ] Test permission checks
  - [ ] Test FIFO ordering
  - [ ] Test date validations
- [ ] All tests passing: ✅ 12+ test cases
- [ ] Permission checks for all endpoints

### 11. Integration Testing
- [ ] Verify ingredient quantity updates when:
  - New batch created
  - Batch consumed
  - Batch marked expired
  - Batch deleted
- [ ] Test workflow:
  1. Check ingredient #I001 quantity = 0
  2. Create batch #B001 with 100 kg
  3. Verify ingredient #I001 quantity = 100
  4. Consume 30 kg from batch
  5. Verify ingredient quantity = 70
- [ ] Test FIFO selection:
  1. Create 3 batches for same ingredient with different expiry dates
  2. Request 150 units (more than first batch)
  3. Verify first batch consumed completely, second batch partially

### 12. Documentation
- [ ] Create `TESTING_GUIDE_TASK_3_3.md`:
  - API endpoint documentation
  - All 10+ endpoints with curl examples
  - Field descriptions and types
  - Business logic explanation (FIFO, expiry)
  - Test cases with expected results
  - Troubleshooting guide
- [ ] Update `PROJECT_SUMMARY_PHASE_3.md`:
  - Add Task 3.3 to completion status
  - Update database schema section
  - Update integration points
  - Note Task 3.4 coming next
- [ ] Update `QUICK_REFERENCE.md`:
  - Add batch endpoints
  - Add common batch commands
  - Add debugging tips for batch queries
- [ ] Inline code comments:
  - Model docstrings
  - Serializer validation docstrings
  - ViewSet method documentation
  - Signal documentation

---

## 🔧 Implementation Steps (Recommended Order)

### Phase 1: Model Setup (30 min)
1. Create IngredientBatch model in `models.py`
2. Add auto-ID generation logic (copy from Category pattern)
3. Create model migration
4. Apply migration
5. Test model in shell

### Phase 2: Serializers (45 min)
1. Create BatchSerializer
2. Create BatchDetailSerializer
3. Create BatchCreateUpdateSerializer
4. Add validation in create/update serializers
5. Test serializers with sample data

### Phase 3: ViewSet & API (60 min)
1. Create BatchViewSet with CRUD
2. Add custom actions (consume, expiring_soon, expired)
3. Implement filtering & search
4. Add permissions
5. Register in urls.py
6. Test endpoints with curl

### Phase 4: Signals & Integration (30 min)
1. Create signal handler for quantity sync
2. Test signal when batch created
3. Test signal when batch updated
4. Test signal when batch deleted
5. Verify ingredient totals updated

### Phase 5: Testing (45 min)
1. Write 12+ test cases
2. Run all tests - verify passing
3. Test permission checks
4. Test edge cases (bad dates, duplicate IDs)
5. Test integration with ingredients

### Phase 6: Documentation (30 min)
1. Write TESTING_GUIDE_TASK_3_3.md
2. Update PROJECT_SUMMARY_PHASE_3.md
3. Update QUICK_REFERENCE.md
4. Add inline code comments
5. Review all documentation

**Total Time:** ~4 hours (matches estimate)

---

## 🚀 Quick Start Commands

```bash
# Setup
cd Backend
.\venv\Scripts\activate

# Create model & migration
python manage.py makemigrations
python manage.py migrate

# Load seed data (after implementation)
python manage.py seed_batches

# Run tests
python test_batches_endpoints.py

# Database inspection
python manage.py shell
>>> from api.models import IngredientBatch
>>> batches = IngredientBatch.objects.all()
>>> for b in batches: print(f"{b.batch_id}: {b.ingredient.name} - {b.remaining_quantity} remaining")

# Start server
python manage.py runserver
# Visit: http://localhost:8000/api/batches/
```

---

## 📊 Expected Seed Data Structure

```
Ingredient #I001 (All Purpose Flour)
├── Batch #B001: 100 kg, expires 2024-04-15 (FIFO)
├── Batch #B002: 50 kg, expires 2024-05-01
└── Batch #B003: 0 kg, expires 2024-03-20 (EXPIRED)

Ingredient #I002 (Whole Wheat Flour)
├── Batch #B004: 75 kg, expires 2024-04-22
└── Batch #B005: 25 kg, expires 2024-04-30

... (3 batches per ingredient × 18 ingredients = 54 batches total)
```

---

## ✅ Completion Criteria

Task 3.3 is **DONE** when:
1. ✅ IngredientBatch model created with all fields
2. ✅ Auto-ID generation working (#B001, #B002...)
3. ✅ All CRUD endpoints operational
4. ✅ Signals auto-sync ingredient quantities
5. ✅ Filtering, searching, ordering working
6. ✅ FIFO logic implemented & tested
7. ✅ Expiry date calculations correct
8. ✅ All 12+ tests passing
9. ✅ Permissions enforced
10. ✅ Documentation complete
11. ✅ Integration with ingredients verified
12. ✅ Ready for Task 3.4

---

## ⚠️ Common Pitfalls to Avoid

1. **Forgetting Signal Registration**
   - Signal won't work if not registered in `apps.py`
   - Test: Create batch in shell, check ingredient quantity updated

2. **FIFO Order Incorrect**
   - Default ordering must be by `expiry_date` ascending
   - Test: Query batches, verify oldest first

3. **Negative Remaining Quantity**
   - Prevent remaining_quantity from going below 0
   - Validate consumption amount <= remaining_quantity

4. **Expiry Date Not Calculated**
   - `is_expired` must be computed from comparison with today
   - Consider timezone for datetime comparison

5. **Soft Delete Not Implemented**
   - Use `is_active` field, don't hard delete
   - Filter out inactive in list views

6. **Permission Check Missing**
   - Add permission class to ViewSet
   - Test all endpoints with low-permission account

7. **Migration Not Applied**
   - Run `python manage.py migrate` after `makemigrations`
   - Verify table exists in SQLite

---

## 📚 Reference Files to Review

Before starting, review:
1. [models.py](models.py) - Category & Ingredient patterns to follow
2. [serializers.py](serializers.py) - Serializer structure (validation, custom fields)
3. [views.py](views.py) - ViewSet patterns, custom actions, filters
4. [TESTING_GUIDE_TASK_3_1.md](TESTING_GUIDE_TASK_3_1.md) - Testing patterns
5. [TESTING_GUIDE_TASK_3_2.md](TESTING_GUIDE_TASK_3_2.md) - More endpoint examples

---

**Good luck! You've got this! 🚀**

**Estimated Completion:** 4 hours of focused development

**Next Task (3.4):** Wastage Management (3 hours)
