/**
 * API Response Types
 * 
 * These types match the backend serializer responses.
 * Note: Decimal fields serialize to strings in JSON, so we define them as string
 * but they should be converted using numericUtils before calculations
 */

/**
 * User type matching backend UserListSerializer response
 */
export interface ApiUser {
  id?: number;
  username: string;
  email?: string;
  full_name: string;          // Note: backend sends 'full_name', not 'name'
  employee_id: string;
  nic?: string | null;        // NIC Number - optional field
  contact?: string | null;    // Contact number - optional field
  role: string;
  status: string;             // 'active', 'inactive', or 'suspended'
  avatar_color?: string;
  is_active?: boolean;        // Soft delete flag - true if user is active, false if deactivated
  password?: string;          // Only used when creating/updating user
  created_at?: string;
  updated_at?: string;
}

/**
 * Product type matching backend ProductListSerializer response
 * All Decimal fields come as strings from backend
 */
export interface ApiProduct {
  id: number;
  product_id: string;         // Format: "#PROD-1001"
  name: string;
  selling_price: string;      // ⚠️ Backend sends as Decimal, serialized to string
  cost_price: string;         // ⚠️ Backend sends as Decimal, serialized to string
  profit_margin: number;
  current_stock: string;      // ⚠️ Backend sends as Decimal, serialized to string
  status: string;
  image_url: string;
  category_id: number;
  category_name: string;
  shelf_life?: number;
  shelf_unit?: string;
  created_at: string;
}

/**
 * Sale type matching backend SaleListSerializer response
 * All Decimal fields come as strings from backend
 */
export interface ApiSale {
  id: number;
  bill_number: string;
  cashier_id: number;
  cashier_name: string;
  subtotal: string;           // ⚠️ Backend sends as Decimal, serialized to string
  discount_id: number | null;
  discount_name: string | null;
  discount_amount: string;    // ⚠️ Backend sends as Decimal, serialized to string
  total_amount: string;       // ⚠️ Backend sends as Decimal, serialized to string
  payment_method: string;
  item_count: number;
  date_time: string;          // ISO datetime
  created_at: string;
}

/**
 * SaleItem type matching backend SaleItemSerializer response
 * All Decimal fields come as strings from backend
 */
export interface ApiSaleItem {
  id: number;
  product_id: number;
  product_id_val: number;
  product_name: string;
  quantity: string;           // ⚠️ Backend sends as Decimal, serialized to string
  unit_price: string;         // ⚠️ Backend sends as Decimal, serialized to string
  subtotal: string;           // ⚠️ Backend sends as Decimal, serialized to string
  created_at: string;
}

/**
 * Frontend UI types - all numeric fields are actual numbers
 * These are used after conversion from API types
 */

export interface UiUser extends Omit<ApiUser, 'full_name' | 'avatar_color'> {
  name: string;  // Mapped from backend 'full_name'
  avatarColor?: string;  // Mapped from backend 'avatar_color'
}

export interface UiProduct extends Omit<ApiProduct, 'selling_price' | 'cost_price' | 'current_stock' | 'profit_margin'> {
  selling_price: number;
  cost_price: number;
  current_stock: number;
  profitMargin: number;  // Mapped from backend 'profit_margin'
}

export interface UiSale extends Omit<ApiSale, 'subtotal' | 'discount_amount' | 'total_amount'> {
  subtotal: number;
  discount_amount: number;
  total_amount: number;
}

export interface UiSaleItem extends Omit<ApiSaleItem, 'quantity' | 'unit_price' | 'subtotal'> {
  quantity: number;
  unit_price: number;
  subtotal: number;
}

/**
 * Sale Detail types - includes items array from detail endpoint
 */
export interface ApiSaleDetail extends ApiSale {
  items: ApiSaleItem[];
}

export interface UiSaleDetail extends UiSale {
  items: UiSaleItem[];
}
