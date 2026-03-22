# BAKERY OS - COMPLETE SYSTEMS ARCHITECTURE REPORT

## 1. PROJECT OVERVIEW

### Core Purpose
BakeryOS is a **comprehensive bakery management system** designed to handle all operational aspects of a bakery business including:
- **Point-of-Sale (POS)** - customer billing and transactions
- **Inventory Management** - products and raw ingredients tracking
- **Production Management** - batch tracking, recipes, and ingredient management
- **Staff Management** - role-based user access control
- **Loss Tracking** - wastage/spoilage documentation
- **Sales Analytics** - transaction history and reporting
- **Promotional Management** - discount creation and application

### Technology Stack
- **Frontend**: React 18 + TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS + Shadcn UI Components
- **State Management**: React Context API (AuthContext)
- **Authentication**: Mock session-based (sessionStorage)
- **Data Storage**: Currently mock data (no backend integration)
- **Document Export**: jsPDF + html2canvas for PDF generation

### Current Status
- ✅ Frontend fully functional with mock data
- ⚠️ No backend API integration yet
- ⚠️ Session-based auth only (cleared on tab close)
- ⚠️ No database persistence

---

## 2. USER ROLES & PERMISSIONS

The system implements **4 distinct user roles** with granular permission controls:

### MANAGER `bg-purple-600`
**Default Role | Full System Access**

**Permissions:**
| Feature | Access Level |
|---------|------------|
| Dashboard | Full (KPIs, Analytics, Transactions) |
| User Management | Full CRUD (Create, Edit, Delete staff) |
| Stock Management | Full (Products & Ingredients) |
| Category Management | Full (Create, Edit, Delete categories) |
| Billing/Sales | Read-only (view reports) |
| Discount Management | **Full CRUD + Activate/Deactivate** (exclusive) |
| Wastage Tracking | Full (all filters, full analytics) |
| Sales Reports | Full access with all filters |
| Navigation | All menu items visible |

**Dashboard Features:**
- KPI cards (Total users, revenue, transactions)
- Top-selling items chart
- Wastage breakdown analysis
- Transaction history

---

### CASHIER `bg-green-600`
**Point-of-Sale Operator | Billing Only**

**Permissions:**
| Feature | Access Level |
|---------|------------|
| Dashboard | Welcome message only |
| Billing & Checkout | **Full (Process sales, manage cart, apply discounts)** |
| Inventory | Read-only (View stock levels only) |
| Discount Application | Can apply active discounts to bills |
| Payment Methods | Cash & Card |
| Navigation | **Billing tab only** (other menu items hidden) |

**Restricted From:**
- User management
- Inventory editing
- Discount creation/management
- Wastage reporting
- Stock management

---

### BAKER `bg-orange-600`
**Production Worker | Ingredient & Recipe Focus**

**Permissions:**
| Feature | Access Level |
|---------|------------|
| Dashboard | **Bake Now list + Low ingredients + Wastage today** |
| Stock View | View products with linked recipes |
| Ingredients | Full view with stock history |
| Recipes | View product recipes & requirements |
| Low Stock Alerts | Full access (ingredient level) |
| Wastage Reporting | Can report product & ingredient wastage |
| Stock Management Tab | Visible (but products marked as secondary) |
| Navigation | Stock management tab default |

**Key Features:**
- Bake now list (products ready for production)
- Low ingredient alerts
- Recipe ingredient requirements
- Wastage reason tracking

---

### STOREKEEPER `bg-blue-600`
**Inventory Manager | Ingredient Specialist**

**Permissions:**
| Feature | Access Level |
|---------|------------|
| Dashboard | **Low stock ingredients + Expiring batches** |
| Ingredients Tab | **Exclusive full access** |
| Products Tab | Hidden (not accessible) |
| Batch Management | Full (Add, edit, track batches) |
| Expiry Tracking | Full (Date-based alerts) |
| Stock History | Full audit trail per ingredient |
| Wastage Reporting | Ingredient wastage only |
| Navigation | **Forced to Ingredients tab** |

**Key Features:**
- Batch tracking with made/expiry dates
- Expiry alerts (within 2 days)
- Supplier management
- Cost tracking per ingredient

---

### Authentication System

**Mock Credentials** (Session-based):
```
Manager:   username: "manager"   | password: "123"
Cashier:   username: "cashier"   | password: "123"
Baker:     username: "baker"     | password: "123"
Storekeeper: username: "store"   | password: "123"
```

**Storage**: `sessionStorage` (survives page refresh, cleared on tab close)

**Role-Based Smart Redirect:**
- Manager → Dashboard
- Cashier → Billing Screen
- Baker → Stock Management (Products view)
- Storekeeper → Stock Management (Ingredients view)

---

## 3. DETAILED USER FLOWS

### FLOW 1: BILLING & CHECKOUT PROCESS

```
┌─────────────────────────────────────────────────────┐
│ 1. CASHIER LOGS IN → Redirected to Billing Screen   │
└─────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────┐
│ 2. VIEW PRODUCT CATALOG                              │
│    • Filter by Category (Buns, Bread, Cakes, Drinks) │
│    • Search by product name                          │
│    • Real-time stock validation                      │
└─────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────┐
│ 3. ADD ITEMS TO CART                                 │
│    • Click product → add to cart                     │
│    • Toast notification: "Added to cart"            │
│    • Cart Panel updates right side                   │
└─────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────┐
│ 4. MANAGE CART QUANTITIES                            │
│    • Increment/Decrement buttons                     │
│    • Validation: qty ≤ available stock              │
│    • Remove item option                             │
└─────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────┐
│ 5. APPLY DISCOUNT (OPTIONAL)                         │
│    • See "Active Discounts" badge                   │
│    • Select applicable discount                     │
│    • Discount calculated: amount = (value/100)*sub  │
└─────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────┐
│ 6. REVIEW TOTALS                                     │
│    • Subtotal = ∑(qty × price)                      │
│    • Discount Amount = (discount% × subtotal)       │
│    • Final Total = Subtotal - Discount              │
└─────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────┐
│ 7. SELECT PAYMENT METHOD                             │
│    • Cash or Card                                   │
└─────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────┐
│ 8. COMPLETE CHECKOUT                                 │
│    • Bill Number auto-generated (BILL-1001, etc.)   │
│    • POST /api/sales/ with items, total, method    │
│    • Toast: "Sale completed successfully"           │
└─────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────┐
│ 9. CLEAR CART & RESTART                              │
│    • Cart emptied                                   │
│    • Ready for next customer                        │
└─────────────────────────────────────────────────────┘
```

**Key Business Logic:**
- Products have frozen prices at sale time
- Stock is validated before checkout (not deducted until confirmed)
- Discounts can be fixed amount or percentage
- Bill numbers auto-increment per session

---

### FLOW 2: INVENTORY MANAGEMENT (ADD/EDIT PRODUCT)

```
┌──────────────────────────────────────────────────────┐
│ MANAGER: Stock Management → Products Tab             │
└──────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────┐
│ OPTION A: ADD NEW PRODUCT                            │
│ • Click "Add New Product" button                    │
└──────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────┐
│ FILL PRODUCT FORM:                                   │
│ ✓ Product ID (auto: #P001, #P002, etc.)            │
│ ✓ Product Name                                       │
│ ✓ Category (Buns/Bread/Cakes/Drinks/Pastries)      │
│ ✓ Selling Price (Rs.)                               │
│ ✓ Cost Price (Rs.) → Profit % calculated            │
│ ✓ Stock Quantity                                     │
│ ✓ Shelf Life (Days/Hours)                           │
│ ✓ Image URL                                          │
│ ✓ Recipe (Ingredients list with qty & unit)         │
└──────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────┐
│ LINK RECIPE INGREDIENTS                              │
│ • Search existing ingredients                       │
│ • Set quantity needed (e.g., 200g flour)            │
│ • Unit conversion to base storage unit              │
│ • Add notes (optional)                              │
└──────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────┐
│ SUBMIT → POST /api/products/                         │
│ • Auto-generate Item ID (#P001)                     │
│ • Save to database with timestamps                  │
└──────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────┐
│ OPTION B: EDIT EXISTING PRODUCT                      │
│ • Search product by name/ID                          │
│ • Click to open "Edit Product" modal                │
│ • Modify: Price, Stock, Shelf Life, Recipe         │
│ • Save changes → PUT /api/products/{id}/            │
└──────────────────────────────────────────────────────┘
```

**Key Business Logic:**
- Profit % automatically calculated: `(sellingPrice - costPrice) / costPrice × 100`
- Green badge if profitable, red if loss-making
- Recipe links to ingredients (used for inventory calculations)
- Shelf life in Days or Hours for expiry tracking

---

### FLOW 3: INGREDIENT & BATCH MANAGEMENT

```
┌────────────────────────────────────────────────────┐
│ STOREKEEPER: Stock Management → Ingredients Tab    │
└────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────┐
│ A) ADD NEW INGREDIENT                               │
│    • Fill ingredient form:                          │
│      - ID (auto: #I001, #I002)                     │
│      - Name (e.g., "All-Purpose Flour")            │
│      - Category (Flour/Dairy/Spices/etc.)          │
│      - Supplier Name + Contact                     │
│      - Cost Price per unit (Rs.)                   │
│      - Initial Stock Qty                           │
│      - Unit (kg/L/pcs/g/ml)                        │
│      - Tracking Type (Weight/Volume/Count)         │
│      - Low Stock Threshold (e.g., 10 kg alert)    │
│      - Shelf Life (Days/Hours)                     │
└────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────┐
│ B) ADD NEW BATCH (Production Lot)                   │
│    • Click "Add New Batch"                          │
│    • Select Ingredient                             │
│    • Enter:                                         │
│      - Quantity (e.g., 50 kg flour received)       │
│      - Made Date (e.g., 2026-03-15)                │
│      - Expiry Date (auto-calc + manual override)   │
│      - Notes (e.g., "Supplier order #SOP1234")    │
│    • Auto-generate Batch ID (#BATCH-1234)         │
│    • Stock added to ingredient total               │
└────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────┐
│ C) VIEW STOCK HISTORY                               │
│    • Timeline of all stock transactions:           │
│      - In: "Added Batch #BATCH-1234" +50kg         │
│      - Out: "Used in Product XYZ" -2kg             │
│      - Loss: "Wastage reported" -1kg               │
│    • Per-batch FIFO tracking                       │
└────────────────────────────────────────────────────┘
                         ↓
┌────────────────────────────────────────────────────┐
│ D) EXPIRY ALERTS                                    │
│    • System checks: expireDate < today + 2 days   │
│    • Alert badge: "Expires in 1 day"              │
│    • Storekeeper dashboard shows expiring batches  │
└────────────────────────────────────────────────────┘
```

---

### FLOW 4: WASTAGE REPORTING

```
┌─────────────────────────────────────────────┐
│ ANY STAFF MEMBER: Report Wastage             │
└─────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────┐
│ BROWSE WASTAGE SCREEN                        │
│ • See all wastage records                    │
│ • Filter by:                                 │
│   - Date Range (Today/Week/Month/Year/All)  │
│   - Reason (Expired/Burnt/Stale/Damaged)    │
│   - Item name (search)                       │
└─────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────┐
│ CLICK "REPORT NEW WASTAGE"                   │
│                                              │
│ Select wastage type:                         │
│  → Product Wastage                           │
│  → Ingredient Wastage                        │
└─────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────┐
│ FILL WASTAGE FORM:                           │
│ • Item Name (search from catalog)            │
│ • Quantity Wasted                            │
│ • Unit (pcs/kg/L)                            │
│ • Reason: Expired | Burnt | Stale | Damaged │
│          Spilled | Custom reason             │
│ • Notes (optional)                           │
│ • Cost per Unit (auto-filled)               │
│ • Total Loss = Qty × Cost (calculated)      │
└─────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────┐
│ SUBMIT → POST /api/wastage/                  │
│ • Record created with timestamp              │
│ • Stock automatically decremented             │
│ • Stock history entry created                │
└─────────────────────────────────────────────┘
                      ↓
┌─────────────────────────────────────────────┐
│ ANALYTICS UPDATED:                           │
│ • KPI: Total loss today (Rs.)               │
│ • KPI: Total qty wasted (units)             │
│ • Chart: Wastage breakdown by reason        │
│ • Trend: Most wasted items                  │
└─────────────────────────────────────────────┘
```

**Key Business Logic:**
- Total Loss = Quantity × Unit Cost (financial impact)
- Wastage reasons are predefined (Expired, Burnt, etc.) + custom
- Automatically deducts from ingredient stock
- KPIs aggregate by date range and reason

---

### FLOW 5: DISCOUNT CREATION & APPLICATION

```
┌──────────────────────────────────────────────┐
│ MANAGER ONLY: Discount Management             │
└──────────────────────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────┐
│ CREATE NEW DISCOUNT                           │
│ • Name (e.g., "Evening Happy Hour")          │
│ • Type: Percentage (50%) OR Fixed (Rs. 150) │
│ • Applicable To:                             │
│   - All items                                │
│   - Specific category (e.g., "Drinks")      │
│   - Specific product (e.g., "Fish Bun")     │
│ • Validity:                                  │
│   - Start Date (optional)                    │
│   - End Date (optional)                      │
│   - Start Time (e.g., 20:00 for 8 PM)       │
│   - End Time (e.g., 21:00 for 9 PM)         │
│ • Active/Inactive toggle                     │
└──────────────────────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────┐
│ POST /api/discounts/                          │
│ • Auto-generate ID (#D001, #D002)            │
│ • Store with validity conditions             │
└──────────────────────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────┐
│ CASHIER VIEW: BILLING SCREEN                  │
│ • Badge shows: "Active Discounts Available"  │
│ • Click to apply                             │
│ • System validates:                          │
│   ✓ Is discount active? (toggle)            │
│   ✓ Is today within date range?             │
│   ✓ Is current time within time range?      │
│   ✓ Does product match target?              │
│ • If all valid: Apply discount              │
│ • Calculate: Amount = (value/100) × Subtotal│
└──────────────────────────────────────────────┘
                       ↓
┌──────────────────────────────────────────────┐
│ MANAGER ANALYTICS:                            │
│ • Total discount applied today               │
│ • Most used discounts                        │
│ • Discount effectiveness                     │
└──────────────────────────────────────────────┘
```

---

### FLOW 6: USER MANAGEMENT (STAFF CRUD)

```
┌─────────────────────────────────────────┐
│ MANAGER: User Management Screen          │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│ VIEW ALL STAFF                            │
│ • Search by name or NIC                  │
│ • Filter by Role (Manager/Cashier/etc.)  │
│ • Filter by Status (Active/Inactive)    │
│ • KPI cards: Total users, Active Count  │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│ ADD NEW STAFF MEMBER                      │
│ • Employee Name                           │
│ • National ID (NIC)                       │
│ • Contact Number                          │
│ • Assign Role (Manager/Cashier/etc.)     │
│ • Create Username (unique)                │
│ • Create Password                         │
│ • Status (Active/Inactive)               │
│ • Auto-assign avatar color per role      │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│ POST /api/users/                          │
│ • Auto-generate Employee ID (#EMP-001)   │
│ • Hash password on backend                │
│ • Set role-based permissions              │
└─────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────┐
│ EDIT / DELETE STAFF                       │
│ • Click staff record                      │
│ • Edit: Name, Contact, Role, Status      │
│ • Delete: Soft delete (flag as inactive) │
└─────────────────────────────────────────┘
```

---

## 4. CORE BUSINESS LOGIC

### A) PRICING & PROFIT CALCULATION

**Formula:**
```
Profit = Selling Price - Cost Price
Profit % = (Profit / Cost Price) × 100
```

**Display Logic:**
- ✅ Green badge if Profit % > 0
- ❌ Red badge if Profit % ≤ 0

**Example:**
```
Product: Fish Bun
Selling Price: Rs. 80
Cost Price: Rs. 45
Profit: Rs. 35
Profit %: (35/45) × 100 = 77.78%
Display: "77.78%" with green badge
```

---

### B) DISCOUNT CALCULATION

**Percentage Discount:**
```
Discount Amount = (Discount % / 100) × Subtotal
Final Price = Subtotal - Discount Amount
```

**Fixed Amount Discount:**
```
Discount Amount = Fixed Value (e.g., Rs. 150)
Final Price = Subtotal - Discount Amount
```

**Example:**
```
Subtotal: Rs. 1000
Discount: "50%" OR "Rs. 150"
Option 1 (50%): Final = 1000 - 500 = Rs. 500
Option 2 (Rs.150): Final = 1000 - 150 = Rs. 850
```

---

### C) STOCK VALIDATION

**At Billing:**
- Before adding to cart: Check `requested_qty ≤ available_stock`
- Show error if insufficient stock
- Update cart quantity: Validate `new_qty ≤ max_available`

**Low Stock Threshold:**
```
if (current_stock < low_stock_threshold) {
  Label: "Low Stock" (yellow badge)
  Alert: Show in baker/storekeeper dashboards
}
```

**Stock Status Labels:**
```
0 stock → "Out of Stock" (red)
0 < stock ≤ 5 → "Low Stock" (yellow)
stock > 5 → "In Stock" (green)
```

---

### D) BATCH & EXPIRY MANAGEMENT

**Expiry Calculation:**
```
Expiry Date = Made Date + Shelf Life (in days or hours)
```

**Expiry Alert Trigger:**
```
if (expiry_date - today ≤ 2 days) {
  Show Alert: "Expires in X days"
  Priority: High (display in dashboard)
}
```

**FIFO Logic:**
- Each batch tracked separately
- Ingredients drawn from oldest batch first (by madeDate)
- Used for accurate cost calculation and quality management

---

### E) WASTAGE LOSS CALCULATION

**Financial Impact:**
```
Total Loss (Rs.) = Quantity Wasted × Unit Cost
```

**Aggregated Metrics:**
```
Total Loss Today = Sum of (qty × cost) for today's wastage
Total Qty Wasted = Sum of quantities wasted
Most Wasted Item = Item with highest frequency
Wastage by Reason = Breakdown by Expired/Burnt/Damaged/etc.
```

**Example:**
```
Bread (1 unit × Rs. 110) = Rs. 110 loss
Flour (2 kg × Rs. 40/kg) = Rs. 80 loss
Total Daily Loss = Rs. 190
```

---

### F) UNIT CONVERSIONS

**Base Units:**
- **Weight**: Grams (g) as base → stored in kg
- **Volume**: Milliliters (ml) as base → stored in L
- **Count**: Single pieces (pcs) → no conversion

**Recipe Example:**
```
Storage: All-Purpose Flour = 50 kg (base: 50,000 g)
Recipe Requirement: 200g (converted from kg = 0.2 kg)
System: 0.2 kg deducted from 50 kg = 49.8 kg remains
```

**Tracking Types:**
- Weight (kg, g) - for flour, sugar, butter
- Volume (L, ml) - for milk, oil, water
- Count (pcs) - for eggs, butter portions

---

### G) SALES PROCESSING LOGIC

**Bill Creation:**
```
Bill Number = "BILL-" + incremented integer
Format: BILL-1001, BILL-1002, BILL-1003
(Auto-increment per session)
```

**Sale Completion:**
```
1. Validate all items have stock
2. Freeze prices (save price at time of sale)
3. Calculate subtotal = Σ(qty × frozen_price)
4. Apply discount (if applicable)
5. Final Total = Subtotal - Discount
6. Record payment method (Cash/Card)
7. POST /api/sales/ with bill payload
8. Clear cart for next customer
```

**Payload Structure:**
```json
{
  "billNumber": "BILL-1001",
  "paymentMethod": "Cash",
  "items": [
    {
      "productId": 1,
      "productName": "Fish Bun",
      "quantity": 3,
      "unitPrice": 80,
      "subtotal": 240
    }
  ],
  "subtotal": 360,
  "discountAmount": 50,
  "total": 310
}
```

---

## 5. DATA ENTITIES & ATTRIBUTES

### Entity 1: USER (Staff Member)

**Purpose:** System login and role-based access control

| Field | Type | Required | Example | Notes |
|-------|------|----------|---------|-------|
| `id` | number | ✓ | 1 | Auto-incremented primary key |
| `employeeId` | string | ✓ | "EMP-001" | Auto-generated unique ID |
| `name` | string | ✓ | "Ravi Silva" | Full name |
| `nic` | string | ✗ | "123456789V" | National ID optional |
| `username` | string | ✓ | "ravi_silva" | Unique login identifier |
| `password` | string | ✓ | "hashed_pwd" | Must be hashed on backend |
| `contact` | string | ✗ | "0712345678" | Phone number |
| `role` | enum | ✓ | "Manager" | Manager \| Cashier \| Baker \| Storekeeper |
| `status` | enum | ✓ | "Active" | Active \| Inactive |
| `avatarColor` | string | ✓ | "bg-purple-600" | Tailwind color per role |
| `createdAt` | timestamp | ✓ | 2026-01-15T10:30:00Z | ISO format |
| `updatedAt` | timestamp | ✓ | 2026-03-15T14:20:00Z | ISO format |
| `lastLogin` | timestamp | ✗ | 2026-03-15T08:45:00Z | For audit purposes |

**Unique Constraints:** `username` (must be unique)

---

### Entity 2: PRODUCT (Finished Goods)

**Purpose:** Items for sale to customers

| Field | Type | Required | Example | Notes |
|-------|------|----------|---------|-------|
| `id` | string | ✓ | "#P001" | Primary key, unique |
| `name` | string | ✓ | "Fish Bun" | Product name |
| `category` | string | ✓ | "Buns" | Buns \| Bread \| Cakes \| Drinks \| Pastries |
| `costPrice` | number | ✓ | 45 | Cost in Rs. per unit |
| `sellingPrice` | number | ✓ | 80 | Selling price in Rs. |
| `quantity` | number | ✓ | 10 | Current stock units |
| `shelfLife` | number | ✗ | 2 | Duration in shelfUnit |
| `shelfUnit` | string | ✗ | "Days" | Days \| Hours |
| `image` | string | ✗ | "https://..." | Product image URL |
| `recipe` | array | ✗ | [...] | Array of IngredientWithQty objects |
| `createdAt` | timestamp | ✓ | 2026-01-10T09:00:00Z | Creation timestamp |
| `updatedAt` | timestamp | ✓ | 2026-03-10T14:00:00Z | Last update timestamp |

**Recipe Field Structure:**
```json
"recipe": [
  {
    "ingredientId": "#I001",
    "ingredientName": "All-Purpose Flour",
    "quantity": 200,
    "unit": "g",
    "notes": "Sifted flour"
  }
]
```

**Calculations:**
```
profit = sellingPrice - costPrice
profitPercent = (profit / costPrice) * 100
```

---

### Entity 3: INGREDIENT (Raw Material)

**Purpose:** Stock items used in recipes and production

| Field | Type | Required | Example | Notes |
|-------|------|----------|---------|-------|
| `id` | string | ✓ | "#I001" | Primary key, unique |
| `name` | string | ✓ | "All-Purpose Flour" | Ingredient name |
| `category` | string | ✓ | "Flour" | Flour \| Dairy \| Spices \| Vegetables \| Fruits \| Oils \| Meat \| Seafood \| Other |
| `supplier` | string | ✓ | "Local Mills" | Supplier name |
| `supplierContact` | string | ✗ | "0715555555" | Supplier phone |
| `costPrice` | number | ✓ | 40 | Cost in Rs. per unit |
| `quantity` | number | ✓ | 50 | Current stock quantity |
| `unit` | string | ✓ | "kg" | kg \| L \| pcs \| g \| ml |
| `trackingType` | string | ✓ | "Weight" | Weight \| Volume \| Count |
| `lowStockThreshold` | number | ✓ | 10 | Threshold qty for alerts |
| `shelfLife` | number | ✗ | 180 | Duration in shelfUnit |
| `shelfUnit` | string | ✗ | "Days" | Days \| Hours |
| `createdAt` | timestamp | ✓ | 2026-01-05T08:00:00Z | Creation timestamp |

**Unique Constraints:** `name` (within same category)

---

### Entity 4: BATCH (Production Lot)

**Purpose:** Track ingredient/product receiving with expiry dates for FIFO

| Field | Type | Required | Example | Notes |
|-------|------|----------|---------|-------|
| `batchId` | string | ✓ | "#BATCH-5678" | Auto-generated unique ID |
| `itemId` | string | ✓ | "#I001" | References Product OR Ingredient |
| `itemName` | string | ✓ | "All-Purpose Flour" | Denormalized for display |
| `itemType` | string | ✓ | "Ingredient" | Product \| Ingredient |
| `quantity` | number | ✓ | 50 | Quantity in batch |
| `unit` | string | ✓ | "kg" | Same unit as item |
| `madeDate` | timestamp | ✓ | 2026-03-01T00:00:00Z | ISO date (production/received) |
| `expireDate` | timestamp | ✓ | 2026-09-01T00:00:00Z | ISO date (calculated or set) |
| `status` | string | ✓ | "Active" | Active \| Expired \| Used \| Discarded |
| `notes` | string | ✗ | "Supplier order #SO-5432" | Optional reference notes |
| `createdAt` | timestamp | ✓ | 2026-03-01T10:00:00Z | Batch entry timestamp |

**Expiry Calculation:**
```
expireDate = madeDate + shelfLife (in days/hours)
```

---

### Entity 5: SALE / ORDER

**Purpose:** Record customer transactions

| Field | Type | Required | Example | Notes |
|-------|------|----------|---------|-------|
| `billNumber` | string | ✓ | "BILL-1001" | Unique primary key |
| `date` | date | ✓ | "2026-03-15" | YYYY-MM-DD format |
| `time` | string | ✓ | "14:30 PM" | HH:MM AM/PM format |
| `paymentMethod` | enum | ✓ | "Cash" | Cash \| Card |
| `items` | array | ✓ | [...] | Array of SaleItem objects |
| `subtotal` | number | ✓ | 360 | Sum of item subtotals |
| `discountId` | string | ✗ | "#D001" | Applied discount reference |
| `discountAmount` | number | ✓ | 50 | Amount deducted (0 if no discount) |
| `total` | number | ✓ | 310 | Subtotal - discountAmount |
| `cashier` | string | ✗ | "Ravi Silva" | Staff member name |
| `status` | string | ✓ | "Completed" | Completed \| Cancelled |
| `createdAt` | timestamp | ✓ | 2026-03-15T14:30:00Z | Transaction timestamp |

**SaleItem Structure:**
```json
"items": [
  {
    "productId": 1,
    "productName": "Fish Bun",
    "quantity": 3,
    "unitPrice": 80,
    "subtotal": 240,
    "discount": 0
  }
]
```

---

### Entity 6: DISCOUNT (Promotion Rule)

**Purpose:** Promotional offers applied to sales

| Field | Type | Required | Example | Notes |
|-------|------|----------|---------|-------|
| `id` | string | ✓ | "#D001" | Auto-generated unique ID |
| `name` | string | ✓ | "Evening Happy Hour" | Discount name |
| `type` | enum | ✓ | "Percentage" | Percentage \| FixedAmount |
| `value` | number | ✓ | 50 | 50 (for 50%) or 150 (for Rs. 150) |
| `applicableTo` | enum | ✓ | "Category" | All \| Category \| Product |
| `targetId` | string | ✗ | "Drinks" | Category name or product ID |
| `startDate` | date | ✗ | "2026-03-01" | YYYY-MM-DD (optional) |
| `endDate` | date | ✗ | "2026-12-31" | YYYY-MM-DD (optional) |
| `startTime` | string | ✗ | "20:00" | HH:MM in 24-hr format |
| `endTime` | string | ✗ | "21:00" | HH:MM in 24-hr format |
| `active` | boolean | ✓ | true | Enable/disable discount |
| `createdBy` | string | ✓ | "Ravi Silva" | Manager username |
| `createdAt` | timestamp | ✓ | 2026-03-01T10:00:00Z | Creation timestamp |
| `updatedAt` | timestamp | ✓ | 2026-03-10T14:00:00Z | Last updated |

---

### Entity 7: WASTAGE (Loss Record)

**Purpose:** Track spoilage and loss for financial and operational analysis

| Field | Type | Required | Example | Notes |
|-------|------|----------|---------|-------|
| `wastageId` | string | ✓ | "#W001" | Auto-generated unique ID |
| `itemId` | string | ✓ | "#P001" | Product or Ingredient ID |
| `itemName` | string | ✓ | "Fish Bun" | Item name |
| `itemType` | enum | ✓ | "Product" | Product \| Ingredient |
| `category` | string | ✓ | "Buns" | Product/Ingredient category |
| `quantity` | number | ✓ | 5 | Quantity wasted |
| `unit` | string | ✓ | "pcs" | pcs \| kg \| L \| g \| ml |
| `unitCost` | number | ✓ | 45 | Cost per unit in Rs. |
| `reason` | string | ✓ | "Expired" | Expired \| Burnt \| Stale \| Damaged \| Spilled \| Custom |
| `reportedBy` | string | ✓ | "Maya Kumari" | Staff member name |
| `date` | date | ✓ | "2026-03-15" | YYYY-MM-DD |
| `time` | string | ✓ | "14:30 PM" | HH:MM AM/PM |
| `notes` | string | ✗ | "Batch #BATCH-5678 expired" | Optional details |
| `totalLoss` | number | ✓ | 225 | quantity × unitCost (Rs.) |
| `createdAt` | timestamp | ✓ | 2026-03-15T14:30:00Z | Record timestamp |

**Calculation:**
```
totalLoss (Rs.) = quantity × unitCost
```

---

### Entity 8: STOCK HISTORY (Audit Log)

**Purpose:** Complete audit trail of all inventory movements

| Field | Type | Required | Example | Notes |
|-------|------|----------|---------|-------|
| `historyId` | string | ✓ | "#H001" | Auto-generated |
| `itemId` | string | ✓ | "#I001" | Product or Ingredient |
| `itemName` | string | ✓ | "All-Purpose Flour" | Denormalized |
| `itemType` | enum | ✓ | "Ingredient" | Product \| Ingredient |
| `transactionType` | enum | ✓ | "AddStock" | AddStock \| UseStock \| Wastage \| Adjustment |
| `quantityBefore` | number | ✓ | 50 | Stock before transaction |
| `quantityAfter` | number | ✓ | 48 | Stock after transaction |
| `changeAmount` | number | ✓ | -2 | Quantity delta (negative = remove) |
| `batchId` | string | ✗ | "#BATCH-5678" | If related to specific batch |
| `reason` | string | ✓ | "Used in Recipe: Fish Bun" | Transaction reason |
| `performedBy` | string | ✓ | "Maya Kumari" | Staff member |
| `timestamp` | timestamp | ✓ | 2026-03-15T14:30:00Z | ISO timestamp |

---

### Entity 9: CATEGORY (Product/Ingredient Categories)

**Purpose:** Organize products and ingredients into logical groups

**Product Categories** (enum):
```
- Buns
- Bread
- Cakes
- Drinks
- Pastries
```

**Ingredient Categories** (enum):
```
- Flour
- Dairy
- Spices
- Vegetables
- Fruits
- Oils
- Meat
- Seafood
- Other
```

---

## 6. SUMMARY TABLE: DATA ENTITIES AT A GLANCE

| Entity | Purpose | Key Fields | Access By |
|--------|---------|-----------|-----------|
| **User** | Staff login + roles | id, username, role, status | All (authentication) |
| **Product** | Items for sale | name, price, stock, recipe | Manager, Cashier, Baker |
| **Ingredient** | Raw materials | name, supplier, stock, batch | Manager, Baker, Storekeeper |
| **Batch** | Production lots | itemId, madeDate, expireDate | Storekeeper, Baker |
| **Sale** | Transactions | billNumber, items, total, method | Cashier (create), Manager (view) |
| **Discount** | Promotions | name, type, value, dates | Manager (CRUD), Cashier (apply) |
| **Wastage** | Loss records | itemId, quantity, reason, cost | All staff (report) |
| **StockHistory** | Audit log | itemId, transactionType, qty | Manager (view) |

---

## 7. REQUIRED API ENDPOINTS FOR BACKEND

```
# SALES
POST   /api/sales/                    - Create sale
GET    /api/sales/                    - List sales with filters
GET    /api/sales/{billNumber}/       - Get specific sale

# PRODUCTS
GET    /api/products/                 - List all products
POST   /api/products/                 - Create product
GET    /api/products/{id}/            - Get product details
PUT    /api/products/{id}/            - Update product
DELETE /api/products/{id}/            - Delete product
GET    /api/products/{id}/stock/      - Get stock history

# INGREDIENTS
GET    /api/ingredients/              - List all ingredients
POST   /api/ingredients/              - Create ingredient
GET    /api/ingredients/{id}/         - Get details
PUT    /api/ingredients/{id}/         - Update ingredient
DELETE /api/ingredients/{id}/         - Delete ingredient
GET    /api/ingredients/{id}/stock/   - Get stock history

# BATCHES
POST   /api/batches/                  - Add new batch
GET    /api/ingredients/{id}/batches/ - List batches for ingredient
PUT    /api/batches/{id}/             - Update batch
DELETE /api/batches/{id}/             - Delete batch

# USERS
GET    /api/users/                    - List staff
POST   /api/users/                    - Create user
GET    /api/users/{id}/               - Get user details
PUT    /api/users/{id}/               - Update user
DELETE /api/users/{id}/               - Delete user

# WASTAGE
POST   /api/wastage/                  - Report wastage
GET    /api/wastage/                  - List wastage with filters
GET    /api/wastage/{id}/             - Get wastage details

# DISCOUNTS
GET    /api/discounts/                - List discounts
POST   /api/discounts/                - Create discount
PUT    /api/discounts/{id}/           - Update discount
DELETE /api/discounts/{id}/           - Delete discount

# CATEGORIES
GET    /api/categories/               - List all categories
POST   /api/categories/               - Create category
PUT    /api/categories/{id}/          - Update category
DELETE /api/categories/{id}/          - Delete category
```

---

## 8. KEY ARCHITECTURAL INSIGHTS FOR BACKEND DESIGN

1. **Role-Based Access Control (RBAC)**: Implement at API level - managers have full access, cashiers only to billing endpoints, etc.

2. **Stock Management**: Maintain transaction history for auditing. Use FIFO for batch consumption.

3. **Discount Engine**: Store conditions (date ranges, times) in database. Validate during sale processing.

4. **Pricing**: Cost vs. Selling price separate. Calculate profit % on backend before returning to frontend.

5. **Cascade Deletes**: Deleting a product should cascade to recipes, batches, and sales history references.

6. **Data Validation**: Enforce unique constraints (product name, ingredient name, username, batch ID).

7. **Idempotency**: Sale endpoints should be idempotent to prevent duplicate bill entries.

8. **Audit Logging**: Every transaction should create stock history entry for compliance.

This comprehensive breakdown should provide all necessary context to design and build the backend database and APIs.
