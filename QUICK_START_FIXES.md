# Quick Start: Immediate Fixes (Copy & Paste Ready)

## File 1: Create `src/types/api.ts` (COPY ENTIRE FILE)

```typescript
// src/types/api.ts
// Exact types returned by Django REST Framework serializers

export type UserRole = 'Manager' | 'Cashier' | 'Baker' | 'Storekeeper';

// ==== RAW API RESPONSE TYPES ====

export interface UserResponse {
  id: number;
  username: string;
  email: string;
  full_name: string;
  employee_id?: string;
  nic?: string;
  contact?: string;
  role: UserRole;
  status: 'active' | 'inactive' | 'suspended';
  avatar_color: string;
  last_login?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface ProductResponse {
  id: number;
  product_id: string;
  name: string;
  description?: string;
  image_url?: string;
  category_id: number;
  category_name: string;
  category_type?: string;
  cost_price: string;
  selling_price: string;
  profit_margin: number;
  current_stock: string;
  status: string;
  is_low_stock?: boolean;
  is_out_of_stock?: boolean;
  shelf_life?: number;
  shelf_unit?: 'hours' | 'days' | 'weeks';
  created_at?: string;
  updated_at?: string;
}

export interface SaleItemResponse {
  id: number;
  product_id: number;
  product_name: string;
  quantity: string;
  unit_price: string;
  subtotal: string;
  created_at?: string;
}

export interface SaleResponse {
  id: number;
  bill_number: string;
  cashier_id: number;
  cashier_name: string;
  subtotal: string;
  discount_id?: number | null;
  discount_name?: string;
  discount_type?: string;
  discount_value?: string;
  discount_amount: string;
  total_amount: string;
  payment_method: 'Cash' | 'Card' | 'Mobile' | 'Cheque' | 'Other';
  notes?: string;
  item_count: number;
  items?: SaleItemResponse[];
  date_time: string;
  created_at?: string;
  updated_at?: string;
}

// ==== UNIFIED TYPES (NO API RESPONSE) ====

export interface AuthUser {
  username: string;
  full_name: string;
  role: UserRole;
  avatarColor: string;
}

export interface Product {
  id: number;
  productId: string;
  name: string;
  description?: string;
  imageUrl?: string;
  categoryId: number;
  categoryName: string;
  costPrice: number;
  sellingPrice: number;
  profitMargin: number;
  currentStock: number;
  status: string;
  shelfLife?: number;
  shelfUnit?: string;
}

export interface CartItem {
  id: number;
  productId: string;
  productName: string;
  quantity: number;
  unitPrice: number;
  subtotal: number;
  category: string;
}

export interface Sale {
  id: number;
  billNumber: string;
  cashierName: string;
  subtotal: number;
  discountId?: number | null;
  discountName?: string;
  discountAmount: number;
  totalAmount: number;
  paymentMethod: string;
  itemCount: number;
  dateTime: string;
  // Computed
  date?: string;
  time?: string;
  itemsSummary?: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next?: string;
  previous?: string;
  results: T[];
}
```

---

## File 2: Create `src/services/apiMapping.ts` (COPY ENTIRE FILE)

```typescript
// src/services/apiMapping.ts
// Converts backend responses to unified types

import {
  ProductResponse, Product,
  SaleResponse, Sale,
  UserResponse, AuthUser,
  SaleItemResponse
} from '../types/api';

// ============ UTILITIES ============

export const parseDecimal = (value: string | number | undefined): number => {
  if (value === undefined || value === null) return 0;
  const num = typeof value === 'string' ? parseFloat(value) : value;
  return isNaN(num) ? 0 : num;
};

export const parseDatetime = (isoString: string) => {
  try {
    const date = new Date(isoString);
    return {
      date: date.toISOString().split('T')[0],
      time: date.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        hour12: true
      })
    };
  } catch {
    return { date: '', time: '' };
  }
};

// ============ MAPPERS ============

export const mapAuthUser = (raw: UserResponse): AuthUser => ({
  username: raw.username,
  full_name: raw.full_name,
  role: raw.role,
  avatarColor: raw.avatar_color
});

export const mapProduct = (raw: ProductResponse): Product => ({
  id: raw.id,
  productId: raw.product_id,
  name: raw.name,
  description: raw.description,
  imageUrl: raw.image_url,
  categoryId: raw.category_id,
  categoryName: raw.category_name,
  costPrice: parseDecimal(raw.cost_price),
  sellingPrice: parseDecimal(raw.selling_price),
  profitMargin: raw.profit_margin || 0,
  currentStock: parseDecimal(raw.current_stock),
  status: raw.status || 'available',
  shelfLife: raw.shelf_life,
  shelfUnit: raw.shelf_unit
});

export const mapSaleItem = (raw: SaleItemResponse) => ({
  id: raw.id,
  productId: raw.product_id,
  productName: raw.product_name,
  quantity: parseDecimal(raw.quantity),
  unitPrice: parseDecimal(raw.unit_price),
  subtotal: parseDecimal(raw.subtotal)
});

export const mapSale = (raw: SaleResponse): Sale => {
  const { date, time } = parseDatetime(raw.date_time);
  const itemsSummary = raw.items
    ? raw.items.map(i => `${i.product_name} x${parseDecimal(i.quantity)}`).join(', ')
    : `${raw.item_count} items`;

  return {
    id: raw.id,
    billNumber: raw.bill_number,
    cashierName: raw.cashier_name,
    subtotal: parseDecimal(raw.subtotal),
    discountId: raw.discount_id,
    discountName: raw.discount_name,
    discountAmount: parseDecimal(raw.discount_amount),
    totalAmount: parseDecimal(raw.total_amount),
    paymentMethod: raw.payment_method,
    itemCount: raw.item_count,
    dateTime: raw.date_time,
    date,
    time,
    itemsSummary
  };
};

// ============ BATCH MAPPERS ============

export const mapProductList = (raw: ProductResponse[]): Product[] =>
  raw.map(mapProduct);

export const mapSaleList = (raw: SaleResponse[]): Sale[] =>
  raw.map(mapSale);
```

---

## File 3: Update `src/context/AuthContext.tsx` (REPLACE ENTIRE FILE)

```typescript
// src/context/AuthContext.tsx
import React, { createContext, useContext, useState, useEffect } from 'react';
import { UserRole, AuthUser, UserResponse } from '../types/api';
import { mapAuthUser } from '../services/apiMapping';

interface AuthContextType {
  user: AuthUser | null;
  login: (userResponse: UserResponse) => void;
  logout: () => void;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<AuthUser | null>(null);

  useEffect(() => {
    const storedUser = sessionStorage.getItem('bakeryUser');
    if (storedUser) {
      try {
        setUser(JSON.parse(storedUser));
      } catch (error) {
        console.error('Failed to parse user data', error);
        sessionStorage.removeItem('bakeryUser');
      }
    }
  }, []);

  const login = (userResponse: UserResponse) => {
    try {
      // Map backend response to client type
      const authUser = mapAuthUser(userResponse);
      setUser(authUser);
      sessionStorage.setItem('bakeryUser', JSON.stringify(authUser));
    } catch (error) {
      console.error('Login mapping failed:', error);
    }
  };

  const logout = () => {
    setUser(null);
    sessionStorage.removeItem('bakeryUser');
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within an AuthProvider');
  return context;
};
```

---

## File 4: Update `src/components/BillingScreen.tsx` (KEY SECTIONS)

**In the interface section, replace:**
```typescript
// BEFORE (WRONG)
interface Product {
  id: number;
  name: string;
  price: number;
  stock: number;
  image: string;
  category: string;
  itemId: string;
}

// AFTER (CORRECT)
import { Product, CartItem } from '../types/api';
import { mapProduct } from '../services/apiMapping';
```

**Replace the hardcoded products array:**
```typescript
// BEFORE (MOCK DATA)
const products: Product[] = [
  {
    id: 1,
    name: 'Fish Bun',
    price: 80,
    stock: 10,
    image: 'https://...',
    category: 'Buns',
    itemId: '#B001',
  },
  // ... more mocks
];

// AFTER (FETCH FROM API)
// Add this effect:
const [products, setProducts] = useState<Product[]>([]);

useEffect(() => {
  const fetchProducts = async () => {
    try {
      // Replace with actual API call
      const response = await fetch('/api/products/');
      const data = await response.json();
      const mappedProducts = data.results.map(mapProduct);
      setProducts(mappedProducts);
    } catch (error) {
      console.error('Failed to fetch products:', error);
    }
  };
  fetchProducts();
}, []);
```

**When adding to cart, use correct fields:**
```typescript
// BEFORE (WRONG FIELDS)
const addToCart = (product: Product) => {
  const item: CartItem = {
    ...product,
    quantity: 1,
    // Missing: unitPrice, subtotal
  };
};

// AFTER (CORRECT)
const addToCart = (product: Product) => {
  const item: CartItem = {
    id: product.id,
    productId: product.productId,      // ✓ FIXED
    productName: product.name,
    quantity: 1,
    unitPrice: product.sellingPrice,   // ✓ FIXED
    subtotal: product.sellingPrice,    // ✓ FIXED
    category: product.categoryName
  };
  setCart([...cart, item]);
};
```

**Calculations (these now work correctly):**
```typescript
const cartTotal = cart.reduce((sum, item) => sum + item.subtotal, 0);
const totalWithoutDiscount = useMemo(() => {
  return cart.reduce((sum, item) => sum + (item.unitPrice * item.quantity), 0);
}, [cart]);
```

---

## File 5: Update `src/components/SalesSummary.tsx` (KEY SECTIONS)

**Replace the type definition:**
```typescript
// BEFORE (WRONG)
type Sale = {
  id: string;
  date: string;
  time: string;
  items: string;
  total: number;
};

// AFTER (CORRECT)
import { Sale } from '../types/api';
import { mapSale } from '../services/apiMapping';
```

**Replace mock data:**
```typescript
// BEFORE
const mockSales: Sale[] = [
  { id: '#ORD-1001', date: ..., time: ..., items: ..., total: 7000 },
  // ...
];

// AFTER
// Remove mock data and fetch from API
const [sales, setSales] = useState<Sale[]>([]);

useEffect(() => {
  const fetchSales = async () => {
    try {
      const response = await fetch('/api/sales/');
      const data = await response.json();
      const mappedSales = data.results.map(mapSale);
      setSales(mappedSales);
    } catch (error) {
      console.error('Failed to fetch sales:', error);
    }
  };
  fetchSales();
}, []);
```

**Filter logic (use correct field names):**
```typescript
const filtered = useMemo(() => {
  return sales.filter(s => {
    // ✓ Use correct field names
    if (s.date && (s.date < dateFrom || s.date > dateTo)) return false;
    if (searchId.trim() && !s.billNumber.toLowerCase().includes(searchId.toLowerCase())) return false;
    if (amountFilter === 'High' && s.totalAmount <= 1000) return false;
    return true;
  });
}, [dateFrom, dateTo, searchId, amountFilter, sales]);
```

**Display fields (use correct mapped names):**
```typescript
// In table: replace these
<tr key={sale.id}>
  <td>{sale.billNumber}</td>        {/* ✓ was: id */}
  <td>{sale.date}</td>              {/* ✓ parsed from date_time */}
  <td>{sale.time}</td>              {/* ✓ parsed from date_time */}
  <td>{sale.itemsSummary}</td>      {/* ✓ from items array */}
  <td>${sale.totalAmount.toFixed(2)}</td>  {/* ✓ was: total */}
</tr>
```

---

## File 6: Create API Service `src/services/api.ts`

```typescript
// src/services/api.ts
import axios from 'axios';
import {
  ProductResponse, Product, PaginatedResponse,
  SaleResponse, Sale, UserResponse,
  mapProduct, mapSale
} from '../types/api';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' }
});

// Add token to requests
apiClient.interceptors.request.use((config) => {
  const token = sessionStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// ============ PRODUCTS ============
export const productAPI = {
  list: async (page = 1): Promise<Product[]> => {
    try {
      const res = await apiClient.get('/products/', { params: { page } });
      return res.data.results.map(mapProduct);
    } catch (error) {
      console.error('Failed to fetch products:', error);
      return [];
    }
  },

  get: async (id: number): Promise<Product | null> => {
    try {
      const res = await apiClient.get(`/products/${id}/`);
      return mapProduct(res.data);
    } catch (error) {
      console.error('Failed to fetch product:', error);
      return null;
    }
  },

  create: async (data: any) => {
    try {
      const res = await apiClient.post('/products/', data);
      return mapProduct(res.data);
    } catch (error) {
      console.error('Failed to create product:', error);
      throw error;
    }
  },

  update: async (id: number, data: any) => {
    try {
      const res = await apiClient.put(`/products/${id}/`, data);
      return mapProduct(res.data);
    } catch (error) {
      console.error('Failed to update product:', error);
      throw error;
    }
  }
};

// ============ SALES ============
export const saleAPI = {
  list: async (page = 1): Promise<Sale[]> => {
    try {
      const res = await apiClient.get('/sales/', { params: { page } });
      return res.data.results.map(mapSale);
    } catch (error) {
      console.error('Failed to fetch sales:', error);
      return [];
    }
  },

  get: async (id: number): Promise<Sale | null> => {
    try {
      const res = await apiClient.get(`/sales/${id}/`);
      return mapSale(res.data);
    } catch (error) {
      console.error('Failed to fetch sale:', error);
      return null;
    }
  },

  create: async (data: any) => {
    try {
      const res = await apiClient.post('/sales/', data);
      return mapSale(res.data);
    } catch (error) {
      console.error('Failed to create sale:', error);
      throw error;
    }
  }
};

// ============ USERS ============
export const userAPI = {
  list: async (page = 1) => {
    try {
      const res = await apiClient.get('/users/', { params: { page } });
      return res.data;
    } catch (error) {
      console.error('Failed to fetch users:', error);
      return { results: [], count: 0 };
    }
  }
};
```

---

## ✅ Step-by-Step Implementation

1. **Copy** `src/types/api.ts` (File 1) into your project
2. **Copy** `src/services/apiMapping.ts` (File 2) into your project
3. **Update** `src/context/AuthContext.tsx` (File 3)
4. **Update** `src/components/BillingScreen.tsx` (File 4) - or create a new corrected version
5. **Update** `src/components/SalesSummary.tsx` (File 5)
6. **Copy** `src/services/api.ts` (File 6) into your project

7. **Install axios** (if not already installed):
   ```bash
   npm install axios
   ```

8. **Test** by running:
   ```bash
   npm start
   ```

---

## 🧪 Test Checklist

- [ ] Login with valid credentials - should not error on field access
- [ ] Products display with correct prices and stock
- [ ] Add product to cart - quantities and prices should calculate correctly
- [ ] Create a sale - bill numbers and dates should display properly
- [ ] No console errors about undefined fields
- [ ] Total calculations are accurate
- [ ] Date/time displays correctly

