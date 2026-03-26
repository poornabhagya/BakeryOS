# Frontend Field Mapping Report
## Avatar Color, Cost Price, and Profit Margin References

**Generated:** March 26, 2026
**Scope:** Frontend TypeScript/React Components

---

## 1. AVATARCOLOR (camelCase - Frontend State)

### Type: Computed Color String Value (CSS Class)
Used to store avatar background color based on user role.

| File | Line | Usage Type | Context |
|------|------|-----------|---------|
| [src/context/AuthContext.tsx](src/context/AuthContext.tsx#L13) | 13 | **Definition** | Interface `AuthUser` - optional field: `avatarColor?: string;` |
| [src/context/AuthContext.tsx](src/context/AuthContext.tsx#L57) | 57 | **Assignment** | `login()` function - assigns role-based color: `avatarColor: color` |
| [src/components/Header.tsx](src/components/Header.tsx#L24) | 24 | **Definition** | Function `getAvatarColor()` - returns color based on role |
| [src/components/Header.tsx](src/components/Header.tsx#L67) | 67 | **Access** | Template rendering - CSS class interpolation |
| [src/components/StaffTable.tsx](src/components/StaffTable.tsx#L18) | 18 | **Definition** | Interface `StaffMember` - optional field: `avatarColor?: string;` |
| [src/components/StaffTable.tsx](src/components/StaffTable.tsx#L40) | 40 | **Assignment** | Mock data - Baker role: `avatarColor: 'bg-blue-200'` |
| [src/components/StaffTable.tsx](src/components/StaffTable.tsx#L52) | 52 | **Assignment** | Mock data - Cashier role: `avatarColor: 'bg-green-200'` |
| [src/components/StaffTable.tsx](src/components/StaffTable.tsx#L64) | 64 | **Assignment** | Mock data - Storekeeper role: `avatarColor: 'bg-orange-200'` |
| [src/components/StaffTable.tsx](src/components/StaffTable.tsx#L76) | 76 | **Assignment** | Mock data - Manager role: `avatarColor: 'bg-purple-200'` |
| [src/components/StaffTable.tsx](src/components/StaffTable.tsx#L124) | 124 | **Access** | Template rendering - Avatar className: `${member.avatarColor \|\| 'bg-gray-200'}` |
| [src/components/UserManagement.tsx](src/components/UserManagement.tsx#L23) | 23 | **Definition** | Interface `StaffMember` - optional field: `avatarColor?: string;` |
| [src/components/UserManagement.tsx](src/components/UserManagement.tsx#L37) | 37 | **Assignment** | Mock data - Baker role: `avatarColor: 'bg-blue-200'` |
| [src/components/UserManagement.tsx](src/components/UserManagement.tsx#L49) | 49 | **Assignment** | Mock data - Cashier role: `avatarColor: 'bg-green-200'` |
| [src/components/UserManagement.tsx](src/components/UserManagement.tsx#L61) | 61 | **Assignment** | Mock data - Storekeeper role: `avatarColor: 'bg-orange-200'` |
| [src/components/UserManagement.tsx](src/components/UserManagement.tsx#L73) | 73 | **Assignment** | Mock data - Manager role: `avatarColor: 'bg-purple-200'` |
| [src/components/UserManagement.tsx](src/components/UserManagement.tsx#L128) | 128 | **Assignment** | Add user handler - computed based on role: `avatarColor: userData.role === 'Manager' ? 'bg-purple-200' : ... ` |

---

## 2. AVATAR_COLOR (snake_case - API Response Field)

### Type: Optional String (from Backend API)
Serialized from backend User model - intended for user avatar color.

| File | Line | Usage Type | Context |
|------|------|-----------|---------|
| [src/utils/apiTypes.ts](src/utils/apiTypes.ts#L21) | 21 | **Definition** | Interface `ApiUser` - optional field: `avatar_color?: string;` |

### Analysis
- **Status**: Defined in API types but **NOT actively used** in frontend
- **Mapping Issue**: Frontend uses `avatarColor` (camelCase) computed from `role`, not `avatar_color` from API
- **Gap**: Backend sends `avatar_color` but frontend ignores it, instead generating colors on the fly

---

## 3. COSTPRICE (camelCase - Frontend State)

### Type: String (Input/State Value)
React state hook for cost price input in product modals.

| File | Line | Usage Type | Context |
|------|------|-----------|---------|
| [src/components/AddItemModal.tsx](src/components/AddItemModal.tsx#L42) | 42 | **Assignment** | State initialization: `const [costPrice, setCostPrice] = useState<string>('');` |
| [src/components/AddItemModal.tsx](src/components/AddItemModal.tsx#L85) | 85 | **Access** | Profit margin calculation: `profitMargin = costPrice && sellingPrice && ...` |
| [src/components/AddItemModal.tsx](src/components/AddItemModal.tsx#L86) | 86 | **Access** | Formula: `toNumber(costPrice)` in calculation |
| [src/components/AddItemModal.tsx](src/components/AddItemModal.tsx#L87) | 87 | **Access** | Formula: Division operation `/ toNumber(costPrice)` |
| [src/components/AddItemModal.tsx](src/components/AddItemModal.tsx#L139) | 139 | **Access** | Input binding: `value={costPrice}` and onChange handler |
| [src/components/AddItemModal.tsx](src/components/AddItemModal.tsx#L139) | 139 | **Assignment** | onChange event: `e => setCostPrice(e.target.value)` |
| [src/components/EditProductItemModal.tsx](src/components/EditProductItemModal.tsx#L59) | 59 | **Assignment** | State initialization: `const [costPrice, setCostPrice] = useState('');` |
| [src/components/EditProductItemModal.tsx](src/components/EditProductItemModal.tsx#L71) | 71 | **Assignment** | Pre-fill from API: `setCostPrice(itemToEdit.cost_price?.toString() \|\| '');` |
| [src/components/EditProductItemModal.tsx](src/components/EditProductItemModal.tsx#L107) | 107 | **Access** | Profit margin calculation: `profitMargin = costPrice && ...` |
| [src/components/EditProductItemModal.tsx](src/components/EditProductItemModal.tsx#L108) | 108 | **Access** | Formula: `toNumber(costPrice)` |
| [src/components/EditProductItemModal.tsx](src/components/EditProductItemModal.tsx#L109) | 109 | **Access** | Formula: Division `/ toNumber(costPrice)` |
| [src/components/EditProductItemModal.tsx](src/components/EditProductItemModal.tsx#L173) | 173 | **Access** | Input binding: `value={costPrice}` |
| [src/components/EditProductItemModal.tsx](src/components/EditProductItemModal.tsx#L173) | 173 | **Assignment** | onChange: `e => setCostPrice(e.target.value)` |
| [src/model/AddItemModal.tsx](src/model/AddItemModal.tsx#L30) | 30 | **Assignment** | State initialization: `const [costPrice, setCostPrice] = useState('');` |
| [src/model/AddItemModal.tsx](src/model/AddItemModal.tsx#L41) | 41 | **Access** | Profit calculation: `if (costPrice && sellingPrice && ...` |
| [src/model/AddItemModal.tsx](src/model/AddItemModal.tsx#L41) | 41 | **Access** | Formula: `toNumber(costPrice)` |
| [src/model/AddItemModal.tsx](src/model/AddItemModal.tsx#L42) | 42 | **Assignment** | Variable: `const cp = toNumber(costPrice);` |
| [src/components/modal/AddItemModal.tsx](src/components/modal/AddItemModal.tsx#L37) | 37 | **Assignment** | State initialization: `const [costPrice, setCostPrice] = useState('');` |
| [src/components/modal/AddItemModal.tsx](src/components/modal/AddItemModal.tsx#L48) | 48 | **Access** | Profit calculation: `if (costPrice && sellingPrice && ...` |
| [src/components/modal/AddItemModal.tsx](src/components/modal/AddItemModal.tsx#L48) | 48 | **Access** | Formula: `toNumber(costPrice)` |
| [src/components/modal/AddItemModal.tsx](src/components/modal/AddItemModal.tsx#L49) | 49 | **Assignment** | Variable: `const cp = toNumber(costPrice);` |
| [src/components/modal/AddItemModal.tsx](src/components/modal/AddItemModal.tsx#L169) | 169 | **Access** | Input binding: `value={costPrice}` |
| [src/components/modal/AddItemModal.tsx](src/components/modal/AddItemModal.tsx#L169) | 169 | **Assignment** | onChange: `e => setCostPrice(e.target.value)` |
| [src/components/modal/AddItemModal.tsx](src/components/modal/AddItemModal.tsx#L176) | 176 | **Access** | Conditional rendering: `{profit !== null && sellingPrice && costPrice && (` |
| [src/components/modal/AddItemModal.tsx](src/components/modal/AddItemModal.tsx#L178) | 178 | **Access** | Comparison: `Number(sellingPrice) > Number(costPrice)` |
| [src/components/modal/AddItemModal.tsx](src/components/modal/AddItemModal.tsx#L180) | 180 | **Access** | Comparison: `Number(sellingPrice) < Number(costPrice)` |
| [src/components/modal/EditProductItemModal.tsx](src/components/modal/EditProductItemModal.tsx#L48) | 48 | **Assignment** | State initialization: `const [costPrice, setCostPrice] = useState('');` |
| [src/components/modal/EditProductItemModal.tsx](src/components/modal/EditProductItemModal.tsx#L60) | 60 | **Assignment** | Pre-fill from item: `setCostPrice(itemToEdit.cost?.toString() \|\| '');` |
| [src/components/modal/EditProductItemModal.tsx](src/components/modal/EditProductItemModal.tsx#L172) | 172 | **Access** | Input binding: `value={costPrice}` |
| [src/components/modal/EditProductItemModal.tsx](src/components/modal/EditProductItemModal.tsx#L172) | 172 | **Assignment** | onChange: `e => setCostPrice(e.target.value)` |
| [src/components/modal/ingredient modal/AddIngredientItemModal.tsx](src/components/modal/ingredient%20modal/AddIngredientItemModal.tsx#L22) | 22 | **Assignment** | State initialization: `const [costPrice, setCostPrice] = useState('');` |
| [src/components/modal/ingredient modal/AddIngredientItemModal.tsx](src/components/modal/ingredient%20modal/AddIngredientItemModal.tsx#L35) | 35 | **Access** | Profit calculation: `if (costPrice && sellingPrice && ...` |
| [src/components/modal/ingredient modal/AddIngredientItemModal.tsx](src/components/modal/ingredient%20modal/AddIngredientItemModal.tsx#L35) | 35 | **Access** | Formula: `Number(costPrice)` |
| [src/components/modal/ingredient modal/AddIngredientItemModal.tsx](src/components/modal/ingredient%20modal/AddIngredientItemModal.tsx#L36) | 36 | **Assignment** | Variable: `const cp = Number(costPrice);` |

---

## 4. COST_PRICE (snake_case - API Response & Object Notation)

### Type: String (from API serialization) → Number (converted to UI type)
Backend sends cost_price as Decimal serialized to string in JSON.

| File | Line | Usage Type | Context |
|------|------|-----------|---------|
| [src/utils/apiTypes.ts](src/utils/apiTypes.ts#L35) | 35 | **Definition** | Interface `ApiProduct` - field: `cost_price: string;` with comment: `// ⚠️ Backend sends as Decimal, serialized to string` |
| [src/utils/apiTypes.ts](src/utils/apiTypes.ts#L91) | 91 | **Definition** | Interface `UiProduct` extends - omits: `'selling_price' \| 'cost_price' \| 'current_stock'` |
| [src/utils/apiTypes.ts](src/utils/apiTypes.ts#L93) | 93 | **Definition** | Interface `UiProduct` - redefined as: `cost_price: number;` |
| [src/utils/apiTypes.ts](src/utils/apiTypes.ts#L114) | 114 | **Assignment** | Conversion function `convertApiProductToUi()` - destructure: `const { selling_price, cost_price, ... } = product;` |
| [src/utils/apiTypes.ts](src/utils/apiTypes.ts#L118) | 118 | **Assignment** | Conversion - map to number: `cost_price: Number(cost_price),` |
| [src/components/BillingScreen.tsx](src/components/BillingScreen.tsx#L14) | 14 | **Definition** | Interface `Product` - optional field: `cost_price?: number;` |
| [src/components/BillingScreen.tsx](src/components/BillingScreen.tsx#L19) | 19 | **Definition** | Interface `Product` - optional field: `profit_margin?: number;` |
| [src/components/StockManagementScreen.tsx](src/components/StockManagementScreen.tsx#L27) | 27 | **Definition** | Type `Product` - field: `cost_price: number;` |
| [src/components/StockManagementScreen.tsx](src/components/StockManagementScreen.tsx#L32) | 32 | **Assignment** | Mock data - Fish Bun: `cost_price: 45` |
| [src/components/StockManagementScreen.tsx](src/components/StockManagementScreen.tsx#L33) | 33 | **Assignment** | Mock data - Tea Bun: `cost_price: 30` |
| [src/components/StockManagementScreen.tsx](src/components/StockManagementScreen.tsx#L34) | 34 | **Assignment** | Mock data - Butter Cake: `cost_price: 200` |
| [src/components/StockManagementScreen.tsx](src/components/StockManagementScreen.tsx#L35) | 35 | **Assignment** | Mock data - Sandwich Bread: `cost_price: 110` |
| [src/components/StockManagementScreen.tsx](src/components/StockManagementScreen.tsx#L36) | 36 | **Assignment** | Mock data - Iced Coffee: `cost_price: 80` |
| [src/components/StockManagementScreen.tsx](src/components/StockManagementScreen.tsx#L37) | 37 | **Assignment** | Mock data - Chicken Roll: `cost_price: 60` |
| [src/components/StockManagementScreen.tsx](src/components/StockManagementScreen.tsx#L101) | 101 | **Definition** | Type `Product` - optional field: `cost_price?: number;` |
| [src/components/StockManagementScreen.tsx](src/components/StockManagementScreen.tsx#L330) | 330 | **Access** | Template rendering: `<td>Rs. {p.cost_price}</td>` |
| [src/components/StockManagementScreen.tsx](src/components/StockManagementScreen.tsx#L361) | 361 | **Access** | Edit handler - copy data: `cost_price: p.cost_price,` |
| [src/components/EditProductItemModal.tsx](src/components/EditProductItemModal.tsx#L45) | 45 | **Definition** | Interface `Product` in `EditProductItemModalProps` - field: `cost_price: number;` |
| [src/model/EditProductItemModal.tsx](src/model/EditProductItemModal.tsx#L34) | 34 | **Definition** | Type definition - field: `cost_price: number;` |
| [src/components/modal/ViewProductModal.tsx](src/components/modal/ViewProductModal.tsx#L18) | 18 | **Definition** | Interface `item` prop - optional field: `cost_price?: number;` |
| [src/components/modal/ViewProductModal.tsx](src/components/modal/ViewProductModal.tsx#L37) | 37 | **Access** | Profit calculation: `const profit = subtractNumeric(toNumber(item.selling_price), toNumber(item.cost_price));` |
| [src/components/modal/ViewProductModal.tsx](src/components/modal/ViewProductModal.tsx#L65) | 65 | **Access** | Template rendering: `Rs. {toNumber(item.cost_price).toFixed(2)}` |

---

## 5. PROFITMARGIN (camelCase - Computed Value)

### Type: String (percentage with "%" suffix) OR null
Dynamically calculated from costPrice and sellingPrice.

| File | Line | Usage Type | Context |
|------|------|-----------|---------|
| [src/components/AddItemModal.tsx](src/components/AddItemModal.tsx#L85) | 85 | **Definition/Computation** | Variable declaration: `const profitMargin = costPrice && sellingPrice && ... ? \`...\` : null;` |
| [src/components/AddItemModal.tsx](src/components/AddItemModal.tsx#L87) | 87 | **Computation** | Formula: `(((toNumber(sellingPrice) - toNumber(costPrice)) / toNumber(costPrice)) * 100).toFixed(1)}%` |
| [src/components/AddItemModal.tsx](src/components/AddItemModal.tsx#L146) | 146 | **Access** | Conditional render: `{profitMargin && (` |
| [src/components/AddItemModal.tsx](src/components/AddItemModal.tsx#L147) | 147 | **Access** | Display: `<Badge>Profit Margin: {profitMargin}</Badge>` |
| [src/components/EditProductItemModal.tsx](src/components/EditProductItemModal.tsx#L107) | 107 | **Definition/Computation** | Variable declaration: `const profitMargin = costPrice && sellingPrice && ... ? \`...\` : null;` |
| [src/components/EditProductItemModal.tsx](src/components/EditProductItemModal.tsx#L109) | 109 | **Computation** | Formula: `(((toNumber(sellingPrice) - toNumber(costPrice)) / toNumber(costPrice)) * 100).toFixed(1)}%` |
| [src/components/EditProductItemModal.tsx](src/components/EditProductItemModal.tsx#L180) | 180 | **Access** | Conditional render: `{profitMargin && (` |
| [src/components/EditProductItemModal.tsx](src/components/EditProductItemModal.tsx#L181) | 181 | **Access** | Display: `<Badge>Recalculate Profit: {profitMargin}</Badge>` |

---

## 6. PROFIT_MARGIN (snake_case - API Response Field)

### Type: Number
Sent from backend in API response.

| File | Line | Usage Type | Context |
|------|------|-----------|---------|
| [src/utils/apiTypes.ts](src/utils/apiTypes.ts#L36) | 36 | **Definition** | Interface `ApiProduct` - field: `profit_margin: number;` |
| [src/components/BillingScreen.tsx](src/components/BillingScreen.tsx#L19) | 19 | **Definition** | Interface `Product` - optional field: `profit_margin?: number;` |

---

## Summary & Analysis

### Key Findings

#### 1. **Avatar Color Mismatch** 🔴
- **Backend sends**: `avatar_color` (snake_case)
- **Frontend uses**: `avatarColor` (camelCase), computed from role, NOT from API
- **Impact**: Backend's `avatar_color` field is completely ignored
- **Recommendation**: Decide whether to use backend value or continue frontend computation

#### 2. **Cost Price Mapping** ✅  
- **API sends**: `cost_price` (string, serialized Decimal)
- **Frontend converts**: Via `convertApiProductToUi()` to number
- **Frontend uses**: Both `cost_price` (from API data) and `costPrice` (React state for inputs)
- **Status**: Properly handled with conversion function

#### 3. **Profit Margin Calculation** ✅
- **API sends**: `profit_margin` (number, pre-calculated)
- **Frontend also computes**: `profitMargin` locally in modals
- **Status**: Dual approach - API value available but frontend recalculates for UI feedback
- **Note**: Frontend calculation happens in AddItemModal and EditProductItemModal for real-time feedback

#### 4. **State vs API Fields**
| Field | Frontend State | API Response | In UI |
|-------|---|---|---|
| Avatar Color | `avatarColor` | `avatar_color` | ❌ Not used |
| Cost Price | `costPrice` (string) | `cost_price` (string) | ✅ Converted & Used |
| Profit Margin | `profitMargin` (computed) | `profit_margin` (number) | ✅ Both Available |

---

## Recommendations

1. **Avatar Color**: Either use backend `avatar_color` or remove the field from API types
2. **Cost Price**: Conversion flow is correct; maintain current approach
3. **Profit Margin**: Keep both backend calculation and frontend computation for flexibility
4. **File Locations with Multiple Versions**: 
   - `AddItemModal.tsx` exists in 3 locations: `src/components/`, `src/model/`, `src/components/modal/`
   - `EditProductItemModal.tsx` exists in 2 locations: `src/components/`, `src/model/`
   - Consider consolidating to single source of truth

