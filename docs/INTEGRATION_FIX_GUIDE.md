# Backend ↔ Frontend Integration Fix Guide

## Quick Reference: What to Fix First

### 1️⃣ Create API Response Types (Frontend)

Create a new file: `src/types/api.ts`

```typescript
// src/types/api.ts

// ============ USER TYPES ============
export interface UserResponse {
  id: number;
  username: string;
  email: string;
  full_name: string;
  employee_id?: string;
  nic?: string;
  contact?: string;
  role: 'Manager' | 'Cashier' | 'Baker' | 'Storekeeper';
  status: 'active' | 'inactive' | 'suspended';
  avatar_color: string;
  last_login?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

// The local AuthUser is a simplified version
export interface AuthUser {
  username: string;
  full_name: string;  // ✓ Changed from 'name'
  role: UserRole;
  avatarColor: string;
}

// ============ PRODUCT TYPES ============
export interface ProductResponse {
  id: number;
  product_id: string;        // e.g., "#PROD-1001"
  name: string;
  description?: string;
  image_url?: string;        // ✓ Changed from 'image'
  category_id: number;
  category_name: string;
  category_type: string;
  cost_price: string;         // Server returns as string (Decimal)
  selling_price: string;      // Server returns as string (Decimal)
  profit_margin: number;      // Percentage
  current_stock: string;      // Server returns as string (Decimal)
  status: string;
  is_low_stock: boolean;
  is_out_of_stock: boolean;
  shelf_life: number;
  shelf_unit: 'hours' | 'days' | 'weeks';
  created_at: string;
  updated_at: string;
}

// Client-side simplified Product (after parsing)
export interface Product {
  id: number;
  productId: string;
  name: string;
  sellingPrice: number;       // ✓ Parsed to number
  costPrice: number;
  currentStock: number;       // ✓ Parsed to number
  imageUrl?: string;
  categoryId: number;
  categoryName: string;
  profitMargin: number;
  status: string;
}

// ============ SALE TYPES ============
export interface SaleItemResponse {
  id: number;
  product_id: number;
  product_id_val: number;     // Redundant
  product_name: string;
  quantity: string;           // Server returns as string (Decimal)
  unit_price: string;         // Server returns as string (Decimal)
  subtotal: string;           // Server returns as string (Decimal)
  created_at: string;
}

export interface SaleResponse {
  id: number;
  bill_number: string;        // "BILL-1001"
  cashier_id: number;
  cashier_name: string;
  subtotal: string;           // Server returns as string (Decimal)
  discount_id?: number;
  discount_name?: string;
  discount_type?: 'percentage' | 'fixed';
  discount_value?: string;    // Server returns as string (Decimal)
  discount_amount: string;    // Server returns as string (Decimal)
  total_amount: string;       // Server returns as string (Decimal)
  payment_method: 'Cash' | 'Card' | 'Mobile' | 'Cheque' | 'Other';
  notes?: string;
  item_count: number;
  items?: SaleItemResponse[]; // Only in detail endpoint
  date_time: string;          // ISO DateTime
  created_at: string;
  updated_at?: string;
}

// Client-side simplified Sale (after parsing)
export interface Sale {
  id: number;
  billNumber: string;
  cashierName: string;
  subtotal: number;
  discountAmount: number;
  totalAmount: number;        // ✓ Renamed from 'total'
  paymentMethod: string;
  itemCount: number;
  dateTime: string;           // Keep as ISO string
  // Computed properties
  date?: string;              // "YYYY-MM-DD"
  time?: string;              // "HH:MM AM/PM"
  itemsSummary?: string;      // "Item1 x2, Item2 x1"
}

// ============ CART TYPES ============
export interface CartItem {
  id: number;
  productId: string;
  productName: string;
  quantity: number;
  unitPrice: number;          // ✓ Added
  subtotal: number;           // ✓ Added
  category: string;
}

// Paginated response wrapper
export interface PaginatedResponse<T> {
  count: number;
  next?: string;
  previous?: string;
  results: T[];
}
```

---

### 2️⃣ Create API Service Layer with Mapping

Create: `src/services/apiMapping.ts`

```typescript
// src/services/apiMapping.ts

import { 
  ProductResponse, Product, 
  SaleResponse, Sale,
  SaleItemResponse,
  UserResponse,
  AuthUser 
} from '../types/api';

/**
 * Utility: Parse decimal string to number
 * Backend returns "450.50", we need 450.50
 */
export const parseDecimal = (value: string | number): number => {
  const num = typeof value === 'string' ? parseFloat(value) : value;
  return isNaN(num) ? 0 : num;
};

/**
 * MAP: ProductResponse → Product (client-friendly)
 */
export const mapProduct = (raw: ProductResponse): Product => ({
  id: raw.id,
  productId: raw.product_id,
  name: raw.name,
  sellingPrice: parseDecimal(raw.selling_price),
  costPrice: parseDecimal(raw.cost_price),
  currentStock: parseDecimal(raw.current_stock),
  imageUrl: raw.image_url,
  categoryId: raw.category_id,
  categoryName: raw.category_name,
  profitMargin: raw.profit_margin,
  status: raw.status,
});

/**
 * MAP: UserResponse → AuthUser (login context)
 */
export const mapAuthUser = (raw: UserResponse): AuthUser => ({
  username: raw.username,
  full_name: raw.full_name,        // ✓ Fixed: was trying to access 'name'
  role: raw.role as any,
  avatarColor: raw.avatar_color,   // ✓ Fixed: snake_case handling
});

/**
 * Helper: Parse ISO datetime to separate date/time
 */
export const parseDatetime = (isoString: string) => {
  const date = new Date(isoString);
  return {
    date: date.toISOString().split('T')[0],  // "YYYY-MM-DD"
    time: date.toLocaleTimeString('en-US', {  // "HH:MM:SS AM/PM"
      hour: '2-digit',
      minute: '2-digit',
      hour12: true
    })
  };
};

/**
 * MAP: SaleItemResponse → client format
 */
export const mapSaleItem = (raw: SaleItemResponse) => ({
  id: raw.id,
  productId: raw.product_id,
  productName: raw.product_name,
  quantity: parseDecimal(raw.quantity),
  unitPrice: parseDecimal(raw.unit_price),
  subtotal: parseDecimal(raw.subtotal),
});

/**
 * MAP: SaleResponse → Sale (client-friendly)
 */
export const mapSale = (raw: SaleResponse): Sale => {
  const { date, time } = parseDatetime(raw.date_time);
  
  return {
    id: raw.id,
    billNumber: raw.bill_number,
    cashierName: raw.cashier_name,
    subtotal: parseDecimal(raw.subtotal),
    discountAmount: parseDecimal(raw.discount_amount),
    totalAmount: parseDecimal(raw.total_amount),  // ✓ Fixed: was 'total'
    paymentMethod: raw.payment_method,
    itemCount: raw.item_count,
    dateTime: raw.date_time,
    date,
    time,
    itemsSummary: raw.items 
      ? raw.items.map(i => `${i.product_name} x${i.quantity}`).join(', ')
      : `${raw.item_count} items`
  };
};
```

---

### 3️⃣ Fix AuthContext.tsx

```typescript
// src/context/AuthContext.tsx

import React, { createContext, useContext, useState, useEffect } from 'react';
import { UserRole, AuthUser } from '../types/api';
import { mapAuthUser } from '../services/apiMapping';

// 3. Context Type
interface AuthContextType {
  user: AuthUser | null;
  login: (userResponse: any) => void;      // Accept backend response
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
        console.error("Failed to parse user data", error);
        sessionStorage.removeItem('bakeryUser');
      }
    }
  }, []);

  const login = (userResponse: any) => {
    // ✓ Use mapping function to convert backend response
    const mappedUser = mapAuthUser(userResponse);
    
    // ✓ Map role to avatar color
    const colorMap = {
      'Manager': 'bg-purple-600',
      'Cashier': 'bg-green-600',
      'Baker': 'bg-orange-600',
      'Storekeeper': 'bg-blue-600'
    };
    
    const authUser: AuthUser = {
      ...mappedUser,
      avatarColor: mappedUser.avatarColor || colorMap[mappedUser.role] || 'bg-gray-500'
    };
    
    setUser(authUser);
    sessionStorage.setItem('bakeryUser', JSON.stringify(authUser));
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

### 4️⃣ Fix BillingScreen.tsx

```typescript
// src/components/BillingScreen.tsx

import { useState, useRef } from 'react';
import { Product, CartItem } from '../types/api';
import { mapProduct } from '../services/apiMapping';

// ✓ Now uses correct type from api.ts
interface BillingProduct extends Product {
  quantity?: number;
}

export function BillingScreen() {
  const [cart, setCart] = useState<CartItem[]>([]);

  // Example: When fetching from API
  const handleAddToCart = (rawProductFromAPI: any) => {
    // ✓ Use mapping function
    const product = mapProduct(rawProductFromAPI);
    
    const cartItem: CartItem = {
      id: product.id,
      productId: product.productId,
      productName: product.name,
      quantity: 1,
      unitPrice: product.sellingPrice,       // ✓ Correctly mapped
      subtotal: product.sellingPrice,
      category: product.categoryName,
    };
    
    setCart([...cart, cartItem]);
  };

  // ✓ Calculations now work correctly with numbers
  const cartTotal = cart.reduce((sum, item) => sum + item.subtotal, 0);
  const profitMargin = cart.reduce((sum, item) => sum + (item.subtotal * 0.2), 0);

  return (
    <div>
      {/* Cart items */}
      {cart.map(item => (
        <div key={item.id}>
          <span>{item.productName}</span>
          <span>{item.quantity}</span>
          <span>₺{item.unitPrice.toFixed(2)}</span>  {/* ✓ Number formatting works */}
          <span>₺{item.subtotal.toFixed(2)}</span>
        </div>
      ))}
      <div>Total: ₺{cartTotal.toFixed(2)}</div>
    </div>
  );
}
```

---

### 5️⃣ Fix SalesSummary.tsx

```typescript
// src/components/SalesSummary.tsx

import { useMemo, useState } from 'react';
import { Sale } from '../types/api';
import { mapSale } from '../services/apiMapping';

export function SalesSummary() {
  const [sales, setSales] = useState<Sale[]>([]);

  // Example: When fetching from API
  const handleFetchSales = async (rawSalesFromAPI: any[]) => {
    // ✓ Map all responses
    const mappedSales = rawSalesFromAPI.map(mapSale);
    setSales(mappedSales);
  };

  const filtered = useMemo(() => {
    return sales.filter(s => {
      // ✓ Use correct field names
      if (s.date && (s.date < dateFrom || s.date > dateTo)) return false;
      if (searchId.trim() && !s.billNumber?.toLowerCase().includes(searchId.trim().toLowerCase())) return false;
      if (amountFilter === 'High' && s.totalAmount <= 1000) return false;
      return true;
    });
  }, [dateFrom, dateTo, searchId, amountFilter, sales]);

  // ✓ Calculations work correctly
  const totalRevenue = filtered.reduce((sum, s) => sum + s.totalAmount, 0);
  const totalTransactions = filtered.length;
  const avgOrder = totalTransactions ? Math.round(totalRevenue / totalTransactions) : 0;

  return (
    <div>
      {/* Display with correct mappings */}
      {filtered.map(sale => (
        <tr key={sale.id}>
          <td>{sale.billNumber}</td>          {/* ✓ Changed from 'id' */}
          <td>{sale.date}</td>                {/* ✓ Parsed from date_time */}
          <td>{sale.time}</td>                {/* ✓ Parsed from date_time */}
          <td>{sale.itemsSummary}</td>        {/* ✓ From items array */}
          <td>₺{sale.totalAmount.toFixed(2)}</td>  {/* ✓ Changed from 'total' */}
        </tr>
      ))}
    </div>
  );
}
```

---

## 🔄 API Call Example (with axios)

```typescript
// src/services/api.ts

import axios from 'axios';
import { 
  ProductResponse, 
  Product,
  PaginatedResponse,
  mapProduct 
} from '../types/api';

const API_BASE = 'http://localhost:8000/api';

const apiClient = axios.create({
  baseURL: API_BASE,
  headers: { 'Content-Type': 'application/json' }
});

// ============ USER ENDPOINTS ============
export const userAPI = {
  login: async (username: string, password: string) => {
    const res = await apiClient.post('/auth/login/', { username, password });
    return res.data;  // Returns UserResponse
  },

  getUsers: async (page = 1) => {
    const res = await apiClient.get('/users/', { params: { page } });
    return res.data as PaginatedResponse<UserResponse>;
  }
};

// ============ PRODUCT ENDPOINTS ============
export const productAPI = {
  list: async (page = 1): Promise<PaginatedResponse<Product>> => {
    const res = await apiClient.get('/products/', { params: { page } });
    
    // ✓ Map all products
    return {
      ...res.data,
      results: res.data.results.map(mapProduct)
    };
  },

  get: async (id: number): Promise<Product> => {
    const res = await apiClient.get(`/products/${id}/`);
    return mapProduct(res.data);
  }
};

// ============ SALE ENDPOINTS ============
export const saleAPI = {
  list: async (page = 1): Promise<PaginatedResponse<Sale>> => {
    const res = await apiClient.get('/sales/', { params: { page } });
    
    // ✓ Map all sales
    return {
      ...res.data,
      results: res.data.results.map(mapSale)
    };
  }
};
```

---

## ✅ Testing the Fixes

```typescript
// Test: src/tests/apiMapping.test.ts

import { mapProduct, mapSale, parseDecimal } from '../services/apiMapping';

describe('API Mapping', () => {
  test('mapProduct converts decimal strings correctly', () => {
    const raw = {
      id: 1,
      product_id: '#PROD-1001',
      name: 'Fish Bun',
      selling_price: '80.50',     // ← string
      cost_price: '40.25',        // ← string
      current_stock: '10.00',     // ← string
      // ... other fields
    };
    
    const mapped = mapProduct(raw);
    
    expect(mapped.sellingPrice).toBe(80.50);        // ✓ number
    expect(mapped.costPrice).toBe(40.25);           // ✓ number
    expect(mapped.currentStock).toBe(10);           // ✓ number
    expect(typeof mapped.sellingPrice).toBe('number');
  });

  test('mapSale handles date_time correctly', () => {
    const raw = {
      id: 1,
      bill_number: 'BILL-1001',
      date_time: '2024-01-15T09:30:00Z',
      // ... other fields
    };
    
    const mapped = mapSale(raw);
    
    expect(mapped.date).toBe('2024-01-15');  // ✓ ISO date
    expect(mapped.time).toMatch(/\d{2}:\d{2}/);  // ✓ HH:MM format
  });

  test('parseDecimal handles various inputs', () => {
    expect(parseDecimal('450.50')).toBe(450.50);
    expect(parseDecimal(450.50)).toBe(450.50);
    expect(parseDecimal('invalid')).toBe(0);
    expect(parseDecimal('0')).toBe(0);
  });
});
```

---

## 📋 Implementation Checklist

- [ ] Create `src/types/api.ts` with all type definitions
- [ ] Create `src/services/apiMapping.ts` with mapping functions
- [ ] Update `src/context/AuthContext.tsx` to use mapping
- [ ] Update `src/components/BillingScreen.tsx` to use correct types
- [ ] Update `src/components/SalesSummary.tsx` to use correct types
- [ ] Update API service to map responses
- [ ] Add unit tests for mapping functions
- [ ] Test login flow with real backend
- [ ] Test product listing
- [ ] Test sale creation and display
- [ ] Test cart operations
- [ ] Verify all calculations are correct

