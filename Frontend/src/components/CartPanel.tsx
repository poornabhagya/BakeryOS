import { Minus, Plus, Trash2, Printer } from 'lucide-react';
import { Card } from './ui/card';

interface CartItem {
  id: number;
  name: string;
  price: number;
  quantity: number;
  stock: number;
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
  discountAmount: number;
  onDiscountChange: (amount: number) => void;
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
  discountAmount,
  onDiscountChange,
}: CartPanelProps) {
  const subtotal = items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
  const total = subtotal - discountAmount;

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
                  <p className="text-sm text-gray-600">Rs. {item.price} each</p>
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
                    disabled={item.quantity >= item.stock}
                    className={`w-8 h-8 flex items-center justify-center rounded transition-colors ${
                      item.quantity >= item.stock
                        ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                        : 'bg-orange-100 hover:bg-orange-200 text-orange-700'
                    }`}
                  >
                    <Plus className="w-4 h-4" />
                  </button>
                </div>

                {/* Item Total */}
                <span className="text-orange-700 tabular-nums">
                  Rs. {(item.price * item.quantity).toLocaleString()}
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
          <span className="tabular-nums">Rs. {subtotal.toLocaleString()}</span>
        </div>

        {/* Discount Input */}
        <div className="flex items-center justify-between">
          <span className="text-gray-700">Discount</span>
          <input
            type="number"
            placeholder="0"
            className="w-24 px-3 py-1 text-right border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-orange-500"
            value={discountAmount || ''}
            onChange={(e) => onDiscountChange(Number(e.target.value) || 0)}
          />
        </div>

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
              Rs. {total.toLocaleString()}
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
