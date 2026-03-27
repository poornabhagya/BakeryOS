import { useState, useRef, useEffect } from 'react';
import { Search, X, Plus, FileText, Printer, Loader } from 'lucide-react';
import { CartPanel } from './CartPanel';
import { Badge } from './ui/badge';
import { Card } from './ui/card';
import { useAuth } from '../context/AuthContext';
import { toNumber, multiplyNumeric } from '../utils/numericUtils';
import apiClient from '../services/api';
import { convertApiProductToUi } from '../utils/conversions';

interface Product {
  id: number;
  product_id: string;
  name: string;
  selling_price: number;
  cost_price?: number;
  current_stock: number;
  image_url: string;
  category_id: number;
  category_name: string;
  profit_margin?: number;
  status?: string;
  shelf_life?: number;
  shelf_unit?: string;
}

interface CartItem extends Product {
  quantity: number;
  unit_price: number;           // Frozen price when added to cart (matches backend SaleItem.unit_price)
  subtotal: number;              // quantity * unit_price (matches backend SaleItem.subtotal)
}

const products: Product[] = [
  {
    id: 1,
    product_id: '#PROD-1001',
    name: 'Fish Bun',
    selling_price: 80,
    current_stock: 10,
    image_url: 'https://images.unsplash.com/photo-1756137943021-6f2ffaa646da?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxmaXNoJTIwYnVuJTIwcGFzdHJ5fGVufDF8fHx8MTc2ODgzODYxMHww&ixlib=rb-4.1.0&q=80&w=1080',
    category_id: 1,
    category_name: 'Buns',
  },
  {
    id: 2,
    product_id: '#PROD-1002',
    name: 'Tea Bun',
    selling_price: 60,
    current_stock: 15,
    image_url: 'https://images.unsplash.com/photo-1741004420618-209c60a86d58?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHx0ZWElMjBidW4lMjBicmVhZHxlbnwxfHx8fDE3Njg4Mzg2MTF8MA&ixlib=rb-4.1.0&q=80&w=1080',
    category_id: 1,
    category_name: 'Buns',
  },
  {
    id: 3,
    product_id: '#PROD-1003',
    name: 'Chocolate Cake',
    selling_price: 450,
    current_stock: 8,
    image_url: 'https://images.unsplash.com/photo-1700448293876-07dca826c161?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjaG9jb2xhdGUlMjBjYWtlJTIwc2xpY2V8ZW58MXx8fHwxNzY4ODA2NzgwfDA&ixlib=rb-4.1.0&q=80&w=1080',
    category_id: 2,
    category_name: 'Cakes',
  },
  {
    id: 4,
    product_id: '#PROD-1004',
    name: 'Croissant',
    selling_price: 120,
    current_stock: 20,
    image_url: 'https://images.unsplash.com/photo-1712723246766-3eaea22e52ff?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjcm9pc3NhbnQlMjBwYXN0cnl8ZW58MXx8fHwxNzY4ODEyNzg4fDA&ixlib=rb-4.1.0&q=80&w=1080',
    category_id: 3,
    category_name: 'Pastries',
  },
  {
    id: 5,
    product_id: '#PROD-1005',
    name: 'Coffee',
    selling_price: 150,
    current_stock: 30,
    image_url: 'https://images.unsplash.com/photo-1564676677001-92e8f1a0df30?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxjb2ZmZWUlMjBjdXAlMjBkcmlua3xlbnwxfHx8fDE3Njg4MDk4ODR8MA&ixlib=rb-4.1.0&q=80&w=1080',
    category_id: 5,
    category_name: 'Drinks',
  },
  {
    id: 6,
    product_id: '#PROD-1006',
    name: 'Bread Loaf',
    selling_price: 90,
    current_stock: 12,
    image_url: 'https://images.unsplash.com/photo-1663904460424-91895028aa9e?crop=entropy&cs=tinysrgb&fit=max&fm=jpg&ixid=M3w3Nzg4Nzd8MHwxfHNlYXJjaHwxfHxicmVhZCUyMGxvYWYlMjBmcmVzaHxlbnwxfHx8fDE3Njg4Mzg2MTJ8MA&ixlib=rb-4.1.0&q=80&w=1080',
    category_id: 4,
    category_name: 'Bread',
  },
];

const categories = ['All', 'Buns', 'Bread', 'Cakes', 'Drinks'];

// --- Bill Number Generator ---
function generateBillNumber(counter: number): string {
  return `BILL-${String(counter).padStart(4, '0')}`;
}

export function BillingScreen() {
    const { user } = useAuth();

    // --- State: API Data Fetching ---
    const [products, setProducts] = useState<Product[]>([]);
    const [isLoading, setIsLoading] = useState(true);
    const [fetchError, setFetchError] = useState<string | null>(null);

    // --- Fetch Products from API ---
    useEffect(() => {
      const fetchProducts = async () => {
        try {
          setIsLoading(true);
          setFetchError(null);
          const response = await apiClient.products.getAll();
          // response.items already contains UI-formatted products
          setProducts(response.items);
        } catch (error) {
          const errorMsg = error instanceof Error ? error.message : 'Failed to fetch products';
          setFetchError(errorMsg);
          console.error('Error fetching products:', error);
        } finally {
          setIsLoading(false);
        }
      };

      fetchProducts();
    }, []);

    // --- Bill Counter (will come from backend later) ---
    const billCounter = useRef(1001);
    const [currentBillNumber, setCurrentBillNumber] = useState(() => generateBillNumber(billCounter.current));

    // Toast Notification State
    const [toast, setToast] = useState<{ message: string; type: 'success' | 'close'; visible: boolean; key: number }>({ message: '', type: 'success', visible: false, key: 0 });

    // Toast Helper
    const showToast = (message: string, type: 'success' | 'close') => {
      console.log('[Toast Triggered]', { message, type });
      setToast(prev => ({ message, type, visible: true, key: prev.key + 1 }));
      setTimeout(() => setToast(t => ({ ...t, visible: false })), 3000);
    };
  const [cart, setCart] = useState<CartItem[]>([]);
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [stockError, setStockError] = useState<string | null>(null);
  // Cash Counter state
  const [isCounterOpen, setIsCounterOpen] = useState(false);
  // Payment method & discount state
  const [paymentMethod, setPaymentMethod] = useState<'Cash' | 'Card'>('Cash');
  const [discountAmount, setDiscountAmount] = useState(0);

  const addToCart = (product: Product) => {
    const existingItem = cart.find(item => item.id === product.id);
    
    if (existingItem) {
      if (existingItem.quantity >= toNumber(product.current_stock)) {
        setStockError(`Insufficient Stock for ${product.name}! (Max: ${product.current_stock})`);
        setTimeout(() => setStockError(null), 5000);
        return;
      }
      setCart(cart.map(item =>
        item.id === product.id
          ? { 
              ...item, 
              quantity: item.quantity + 1, 
              subtotal: multiplyNumeric(item.quantity + 1, item.unit_price) 
            }
          : item
      ));
    } else {
      const unitPrice = toNumber(product.selling_price);
      setCart([...cart, { ...product, quantity: 1, unit_price: unitPrice, subtotal: unitPrice }]);
    }
  };

  const updateQuantity = (id: number, change: number) => {
    setCart(cart.map(item => {
      if (item.id === id) {
        const newQuantity = item.quantity + change;
        if (newQuantity <= 0) return item;
        if (newQuantity > toNumber(item.current_stock)) {
          setStockError(`Insufficient Stock for ${item.name}! (Max: ${item.current_stock})`);
          setTimeout(() => setStockError(null), 5000);
          return item;
        }
        return { 
          ...item, 
          quantity: newQuantity, 
          subtotal: multiplyNumeric(newQuantity, item.unit_price) 
        };
      }
      return item;
    }).filter(item => item.quantity > 0));
  };

  const removeItem = (id: number) => {
    setCart(cart.filter(item => item.id !== id));
  };

  const handleCheckout = () => {
    if (cart.length === 0) return;

    // --- Build API Payload (matches Django sales + sale_items schema) ---
    const payload = {
      bill_number: currentBillNumber,
      payment_method: paymentMethod,
      items: cart.map(item => ({
        product_id: item.id,
        quantity: item.quantity,
        unit_price: item.unit_price,      // Frozen price — captured when product was added to cart
        subtotal: item.subtotal,           // quantity * unit_price (pre-calculated)
      })),
    };

    // --- TODO: Replace with actual API call ---
    // await fetch('/api/sales/', {
    //   method: 'POST',
    //   headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
    //   body: JSON.stringify(payload),
    // });

    console.log('[Checkout Payload]', JSON.stringify(payload, null, 2));
    showToast(`Bill ${currentBillNumber} saved successfully!`, 'success');

    // Reset for next bill
    setCart([]);
    setDiscountAmount(0);
    setPaymentMethod('Cash');
    billCounter.current += 1;
    setCurrentBillNumber(generateBillNumber(billCounter.current));
  };

  const filteredProducts = products.filter(product => {
    const matchesCategory = selectedCategory === 'All' || product.category_name === selectedCategory;
    const matchesSearch = product.name.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  // Toast-based notify
  const notify = (opened: boolean) => {
    if (opened) {
      showToast('✅ Cash Counter Opened Successfully.', 'success');
    } else {
      showToast('🔒 Shift Ended. Counter Closed.', 'close');
    }
  };

  const handleToggle = () => {
    if (!isCounterOpen) {
      setIsCounterOpen(true);
      notify(true);
    } else {
      if (window.confirm('Close counter?')) {
        setIsCounterOpen(false);
        setTimeout(() => notify(false), 10); // ensure state updates before showing toast
      }
    }
  };

  return (
    <>
      {/* Toast Notification - Fixed Position adjusted to top-24 to clear Navbar */}
      <div
        className={`fixed top-24 right-8 z-[9999] transition-all duration-500 ease-in-out transform ${
          toast.visible ? 'opacity-100 translate-y-0' : 'opacity-0 -translate-y-4 pointer-events-none'
        }`}
      >
        <div
          className={`px-6 py-4 rounded-xl shadow-2xl flex items-center gap-3 font-bold border-l-4 backdrop-blur-sm ${
            toast.type === 'success'
              ? 'bg-green-100 text-green-800 border-green-600'
              : 'bg-gray-800 text-white border-gray-500'
          }`}
          style={{ minWidth: '300px', boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)' }}
        >
          <span className="text-2xl">{toast.type === 'success' ? '✅' : '🔒'}</span>
          <div>
            <h4 className="text-sm font-extrabold uppercase tracking-wider opacity-70">
              {toast.type === 'success' ? 'System Status' : 'Shift Status'}
            </h4>
            <p className="text-base">{toast.message}</p>
          </div>
        </div>
      </div>
      <div className="flex flex-col bg-gray-50 min-h-screen relative">
        {/* Header with Explicit Toggle Button */}
        <div className="flex items-center justify-between px-8 py-6 bg-white shadow relative z-50" style={{ position: 'relative' }}>
          <h1 className="text-2xl font-bold text-gray-800">Billing</h1>
          <div style={{ position: 'relative', zIndex: 100, display: 'flex', alignItems: 'center', gap: 12 }}>
            <button
              onClick={handleToggle}
              className={
                isCounterOpen
                  ? 'bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 font-bold text-base shadow-md transition-all duration-200 focus:outline-none focus:ring-4 focus:ring-red-300 border-2 border-red-600'
                  : 'bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg flex items-center gap-2 font-bold text-base shadow-md animate-pulse transition-all duration-200 focus:outline-none focus:ring-4 focus:ring-green-300 border-2 border-green-700'
              }
              style={{
                minWidth: 120,
                fontSize: '1rem',
                letterSpacing: '0.01em',
                backgroundColor: isCounterOpen ? '#ef4444' : '#16a34a', // fallback
                color: '#fff',
                borderColor: isCounterOpen ? '#dc2626' : '#15803d',
                zIndex: 100,
                boxShadow: '0 2px 8px 0 #0002, 0 2px 4px 0 #16a34a33',
                fontWeight: 700,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <span style={{ fontSize: '1.2em', marginRight: 6 }}>
                {isCounterOpen ? '🔒' : '🔓'}
              </span>
              {isCounterOpen ? 'Close Counter' : 'Open Counter'}
            </button>
            {/* Debug Toast Button */}
            <button
              onClick={() => showToast('🧪 This is a test toast!', 'success')}
              className="ml-4 px-3 py-1 rounded bg-blue-500 text-white font-bold text-xs shadow hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-300"
              type="button"
            >
              Show Test Toast
            </button>
          </div>
        </div>
        {/* Stock Error Alert Bar */}
        {stockError && (
          <div className="bg-red-600 text-white px-6 py-3 flex items-center justify-between z-50">
            <span className="flex items-center gap-2">
              <span className="text-lg">⚠️</span>
              <strong>Error:</strong> {stockError}
            </span>
            <button
              onClick={() => setStockError(null)}
              className="p-1 hover:bg-red-700 rounded transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        )}
        {/* Overlay when counter is closed - blocks all billing actions */}
        {!isCounterOpen && (
          <div className="absolute inset-0 z-30 flex flex-col items-center justify-center bg-white/80 backdrop-blur-sm select-none" style={{ pointerEvents: 'auto' }}>
            <div className="text-3xl font-bold text-gray-500 mb-4">Open Counter to Start</div>
          </div>
        )}
        {/* Main Content */}
        <div className="flex overflow-hidden relative" style={{ height: 'calc(100vh - 64px)' }}>
          {/* Left Side - Product Catalog (65%) */}
          <div className="flex-1 flex flex-col overflow-hidden" style={{ width: '65%' }}>
            {/* Search Bar & Category Filters */}
            <div className="p-6 bg-white border-b border-gray-200">
              {/* Search Bar */}
              <div className="relative mb-4">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search products..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-orange-500"
                  disabled={!isCounterOpen}
                />
              </div>
              {/* Category Chips */}
              <div className="flex gap-2 flex-wrap">
                {categories.map(category => (
                  <Badge
                    key={category}
                    onClick={() => isCounterOpen && setSelectedCategory(category)}
                    className={`cursor-pointer px-4 py-2 transition-colors ${
                      selectedCategory === category
                        ? 'bg-orange-600 text-white hover:bg-orange-700'
                        : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                    } ${!isCounterOpen ? 'pointer-events-none opacity-60' : ''}`}
                  >
                    {category}
                  </Badge>
                ))}
              </div>
            </div>
            {/* Product Table */}
            <div className="flex-1 overflow-y-auto p-6">
              {isLoading && (
                <div className="flex items-center justify-center h-full">
                  <div className="text-center">
                    <Loader className="w-8 h-8 animate-spin text-orange-600 mx-auto mb-4" />
                    <p className="text-gray-600">Loading products...</p>
                  </div>
                </div>
              )}
              {fetchError && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
                  <p className="font-bold">Error loading products</p>
                  <p className="text-sm">{fetchError}</p>
                </div>
              )}
              {!isLoading && !fetchError && (
              <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
                <table className="w-full">
                  <thead>
                    <tr className="border-b border-gray-200 bg-gray-50">
                      <th className="px-6 py-3 text-left text-sm text-gray-600">Item ID</th>
                      <th className="px-6 py-3 text-left text-sm text-gray-600">Item Name</th>
                      <th className="px-6 py-3 text-left text-sm text-gray-600">Stock Qty</th>
                      <th className="px-6 py-3 text-left text-sm text-gray-600">Price</th>
                      <th className="px-6 py-3 text-left text-sm text-gray-600">Action</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredProducts.map(product => (
                      <tr 
                        key={product.id} 
                        className="border-b border-gray-100 hover:bg-gray-50 transition-colors"
                      >
                        <td className="px-6 py-4 text-sm text-gray-600">{product.product_id}</td>
                        <td className="px-6 py-4 text-gray-900">{product.name}</td>
                        <td className="px-6 py-4 text-gray-900 tabular-nums">{product.current_stock}</td>
                        <td className="px-6 py-4 text-orange-700 tabular-nums">Rs. {product.selling_price}</td>
                        <td className="px-6 py-4">
                          <button
                            onClick={() => addToCart(product)}
                            disabled={product.current_stock === 0 || !isCounterOpen}
                            className={`px-4 py-2 rounded-lg flex items-center gap-1 transition-colors ${
                              product.current_stock === 0 || !isCounterOpen
                                ? 'bg-gray-200 text-gray-400 cursor-not-allowed'
                                : 'bg-orange-600 hover:bg-orange-700 text-white'
                            }`}
                          >
                            <Plus className="w-4 h-4" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {filteredProducts.length === 0 && (
                  <div className="text-center py-12">
                    <p className="text-gray-400">No products found</p>
                  </div>
                )}
              </div>
              )}
            </div>
            {/* Previous Bill Summary Section */}
            <div className="p-6 pt-0">
              <Card className="border border-gray-200 bg-orange-50">
                <div className="p-4">
                  <h4 className="text-gray-800 mb-3">Previous Bill Summary</h4>
                  {/* Bill Details */}
                  <div className="space-y-2 mb-4">
                    <p className="text-sm text-gray-700">
                      <span className="text-orange-700">Bill #107</span> • Fish Bun (x2), Tea Bun (x1)
                    </p>
                    <p className="text-sm text-gray-600">
                      <span className="tabular-nums">Total: Rs. 220</span> | <span className="tabular-nums">Discount: Rs. 0</span>
                    </p>
                  </div>
                  {/* Action Buttons */}
                  <div className="flex gap-3">
                    <button
                      onClick={() => alert('Opening PDF...')}
                      className="flex-1 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg flex items-center justify-center gap-2 transition-colors"
                      disabled={!isCounterOpen}
                    >
                      <FileText className="w-4 h-4" />
                      <span className="text-sm">Open PDF</span>
                    </button>
                    <button
                      onClick={() => alert('Reprinting bill...')}
                      className="flex-1 px-4 py-2 border border-gray-300 hover:bg-gray-50 text-gray-700 rounded-lg flex items-center justify-center gap-2 transition-colors"
                      disabled={!isCounterOpen}
                    >
                      <Printer className="w-4 h-4" />
                      <span className="text-sm">Reprint</span>
                    </button>
                  </div>
                </div>
              </Card>
            </div>
          </div>
          {/* Right Side - Cart Panel (35%) */}
          <div style={{ width: '35%' }}>
            <CartPanel
              items={cart}
              billNumber={currentBillNumber}
              onUpdateQuantity={updateQuantity}
              onRemoveItem={removeItem}
              onCheckout={handleCheckout}
              isCounterOpen={isCounterOpen}
              paymentMethod={paymentMethod}
              onPaymentMethodChange={setPaymentMethod}
              discountAmount={discountAmount}
              onDiscountChange={setDiscountAmount}
            />
          </div>
        </div>
      </div>
    </>
  );
}