import { Minus, Plus, Trash2, Printer } from 'lucide-react';
import { Card } from './ui/card';
import { toNumber } from '../utils/numericUtils';

interface CartItem {
  id: number;
  name: string;
  selling_price: number;
  quantity: number;
  current_stock: number;
  unit_price: number;           // Frozen price when added (matches backend)
  subtotal: number;              // quantity * unit_price (pre-calculated)
}

interface AvailableDiscount {
  id: number;
  name: string;
  discount_id: string;
  discount_type: 'Percentage' | 'FixedAmount';
  value: string | number;
  applicable_to: 'All' | 'Category' | 'Product';
  target_category_id?: number;
  target_product_id?: number;
}

interface CartPanelProps {
  items: CartItem[];
  billNumber: string;
  onUpdateQuantity: (id: number, change: number) => void;
  onRemoveItem: (id: number) => void;
  onCheckout: () => void;
  isCounterOpen: boolean;
  paymentMethod: 'Cash' | 'Card';
  onPaymentMethodChange: (method: 'Cash' | 'Card') => void;
  availableDiscounts: AvailableDiscount[];
  selectedDiscount: AvailableDiscount | null;
  onSelectDiscount: (discount: AvailableDiscount | null) => void;
  calculatedDiscountAmount: number;
  discountsLoading: boolean;
}

export function CartPanel({ 
  items, 
  billNumber, 
  onUpdateQuantity, 
  onRemoveItem,
  onCheckout,
  isCounterOpen,
  paymentMethod,
  onPaymentMethodChange,
  availableDiscounts,
  selectedDiscount,
  onSelectDiscount,
  calculatedDiscountAmount,
  discountsLoading,
}: CartPanelProps) {
  // Safely convert subtotals that might be strings from backend API
  const subtotal = items.reduce((sum, item) => sum + toNumber(item.subtotal), 0);
  const total = toNumber(subtotal) - toNumber(calculatedDiscountAmount);

  return (
    <div className="h-full flex flex-col bg-white border-l border-gray-200">
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <h3 className="text-gray-900">Current Bill #{billNumber}</h3>
      </div>

      {/* Cart Items */}
      <div className="flex-1 overflow-y-auto p-6 space-y-3">
        {items.length === 0 ? (
          <div className="text-center py-12">
            <p className="text-gray-400">No items added yet</p>
            <p className="text-sm text-gray-400 mt-2">Click on products to add</p>
          </div>
        ) : (
          items.map((item) => (
            <Card key={item.id} className="p-4">
              <div className="flex items-start justify-between mb-3">
                <div className="flex-1">
                  <h4 className="text-gray-900">{item.name}</h4>
                  <p className="text-sm text-gray-600">Rs. {item.unit_price} each</p>
                </div>
                <button
                  onClick={() => onRemoveItem(item.id)}
                  className="p-1 hover:bg-red-100 rounded transition-colors"
                >
                  <Trash2 className="w-4 h-4 text-red-600" />
                </button>
              </div>

              <div className="flex items-center justify-between">
                {/* Quantity Controls */}
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => onUpdateQuantity(item.id, -1)}
                    className="w-8 h-8 flex items-center justify-center bg-gray-100 hover:bg-gray-200 rounded transition-colors"
                  >
                    <Minus className="w-4 h-4" />
                  </button>
                  <span className="w-12 text-center tabular-nums">{item.quantity}</span>
                  <button
                    onClick={() => onUpdateQuantity(item.id, 1)}
                    disabled={item.quantity >= item.current_stock}
                    className={`w-8 h-8 flex items-center justify-center rounded transition-colors ${
                      item.quantity >= item.current_stock
                        ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                        : 'bg-orange-100 hover:bg-orange-200 text-orange-700'
                    }`}
                  >
                    <Plus className="w-4 h-4" />
                  </button>
                </div>

                {/* Item Total */}
                <span className="text-orange-700 tabular-nums">
                  Rs. {item.subtotal.toLocaleString()}
                </span>
              </div>
            </Card>
          ))
        )}
      </div>

      {/* Footer - Totals and Checkout */}
      <div className="border-t border-gray-200 p-6 space-y-4 bg-gray-50">
        {/* Subtotal */}
        <div className="flex items-center justify-between text-gray-700">
          <span>Subtotal</span>
          <span className="tabular-nums">Rs. {subtotal.toFixed(2)}</span>
        </div>

        {/* Smart Discount Dropdown */}
        <div className="flex items-start justify-between gap-2 flex-wrap">
          <span className="text-gray-700 mt-1">Discount</span>
          <div className="flex-1 max-w-xs">
            {discountsLoading ? (
              <p className="text-sm text-gray-500">Loading discounts...</p>
            ) : (
              <select
                value={selectedDiscount?.id || ''}
                onChange={(e) => {
                  const discountId = e.target.value;
                  const discount = availableDiscounts.find(d => d.id === Number(discountId));
                  onSelectDiscount(discount || null);
                }}
                className="w-full px-3 py-2 text-sm border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-orange-500"
              >
                <option value="">No Discount</option>
                {availableDiscounts.map((discount) => {
                  const valueText =
                    discount.discount_type === 'Percentage'
                      ? `${discount.value}%`
                      : `Rs. ${Number(discount.value).toLocaleString()}`;
                  return (
                    <option key={discount.id} value={discount.id}>
                      {discount.name} - {valueText}
                    </option>
                  );
                })}
              </select>
            )}
          </div>
        </div>

        {/* Display Applied Discount Amount */}
        {calculatedDiscountAmount > 0 && (
          <div className="flex items-center justify-between text-green-600 text-sm">
            <span>Discount Applied</span>
            <span className="tabular-nums font-semibold">
              -Rs. {calculatedDiscountAmount.toLocaleString('en-IN', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              })}
            </span>
          </div>
        )}

        {/* Payment Method */}
        <div className="flex items-center justify-between">
          <span className="text-gray-700">Payment</span>
          <div className="flex gap-2">
            {(['Cash', 'Card'] as const).map(method => (
              <button
                key={method}
                onClick={() => onPaymentMethodChange(method)}
                className={`px-3 py-1 rounded-lg text-sm font-medium transition-colors ${
                  paymentMethod === method
                    ? 'bg-orange-600 text-white'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
              >
                {method}
              </button>
            ))}
          </div>
        </div>

        {/* Total */}
        <div className="pt-4 border-t border-gray-300">
          <div className="flex items-center justify-between mb-4">
            <span className="text-gray-900">TOTAL PAYABLE</span>
            <span className="text-2xl text-orange-700 tabular-nums">
              Rs. {total.toFixed(2)}
            </span>
          </div>

          {/* Checkout Button */}
          <button
            onClick={onCheckout}
            disabled={items.length === 0}
            className={`w-full py-4 rounded-lg flex items-center justify-center gap-2 transition-colors ${
              items.length === 0
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-orange-600 hover:bg-orange-700 text-white shadow-lg'
            }`}
          >
            <Printer className="w-6 h-6" />
            <span className="text-lg">CHECKOUT / PRINT</span>
          </button>
        </div>
      </div>
    </div>
  );
}
