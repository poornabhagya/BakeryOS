import { useState, useRef, useEffect } from 'react';
import { Search, X, Plus, FileText, Printer, Loader } from 'lucide-react';
import jsPDF from 'jspdf';
import html2canvas from 'html2canvas';
import { CartPanel } from './CartPanel';
import { Badge } from './ui/badge';
import { Card } from './ui/card';
import { useAuth } from '../context/AuthContext';
import { toNumber, multiplyNumeric } from '../utils/numericUtils';
import apiClient, { categoryApi } from '../services/api';
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

// --- Bill Number Generator ---
function generateBillNumber(counter: number): string {
  return `BILL-${String(counter).padStart(4, '0')}`;
}

export function BillingScreen() {
  const COUNTER_STORAGE_KEY = 'bakery_pos_counter_open';
    const { user } = useAuth();

    // --- State: API Data Fetching ---
    const [products, setProducts] = useState<Product[]>([]);
    const [categories, setCategories] = useState<Array<{ id: number; name: string }>>([{ id: 0, name: 'All' }]);
    const [isLoading, setIsLoading] = useState(true);
    const [fetchError, setFetchError] = useState<string | null>(null);
    const [categoriesLoading, setCategoriesLoading] = useState(true);

    // --- Bill Counter (fetched from backend) ---
    const billCounter = useRef(1001);
    const printableRef = useRef<HTMLDivElement>(null);
    const [currentBillNumber, setCurrentBillNumber] = useState('BILL-1001');

    // --- Fetch Products and Next Bill Number from API ---
    useEffect(() => {
      const fetchInitialData = async () => {
        try {
          setIsLoading(true);
          setFetchError(null);

          // Fetch all product pages so POS has the complete searchable catalog.
          const productsResponse = await apiClient.products.getAllPages();
          setProducts(productsResponse.items);

          // Fetch next bill number from backend
          const billResponse = await apiClient.sales.getNextBillNumber();
          if (billResponse && billResponse.next_number) {
            billCounter.current = billResponse.next_number;
            setCurrentBillNumber(billResponse.next_bill_number);
            console.log('[Bill Number Fetched]', billResponse.next_bill_number);
          }
        } catch (error) {
          const errorMsg = error instanceof Error ? error.message : 'Failed to fetch initial data';
          setFetchError(errorMsg);
          console.error('Error fetching initial data:', error);
        } finally {
          setIsLoading(false);
        }
      };

      fetchInitialData();
    }, []);

    // --- Fetch Categories from API ---
    useEffect(() => {
      const fetchCategories = async () => {
        try {
          setCategoriesLoading(true);
          // Fetch only Product categories (not Ingredient categories)
          const fetchedCategories = await categoryApi.getProducts();
          setCategories([
            { id: 0, name: 'All' },
            ...(fetchedCategories || []).map((cat: any) => ({
              id: cat.id,
              name: cat.name,
            })),
          ]);
          console.log('[Product Categories Fetched]', fetchedCategories);
        } catch (error) {
          console.error('Error fetching product categories:', error);
          // Set default categories on error
          setCategories([{ id: 0, name: 'All' }]);
        } finally {
          setCategoriesLoading(false);
        }
      };

      fetchCategories();
    }, []);

    // --- Fetch Active Discounts from API ---
    useEffect(() => {
      const fetchDiscounts = async () => {
        try {
          setDiscountsLoading(true);
          setDiscountsError(null);
          const fetchedDiscounts = await apiClient.discounts.getActive();
          setAvailableDiscounts(fetchedDiscounts || []);
          console.log('[Active Discounts Fetched]', fetchedDiscounts);
        } catch (error) {
          console.error('Error fetching active discounts:', error);
          setDiscountsError('Failed to load discounts');
          setAvailableDiscounts([]);
        } finally {
          setDiscountsLoading(false);
        }
      };

      fetchDiscounts();
    }, []);

    // --- Fetch Latest Sale (Previous Bill) on Mount ---
    useEffect(() => {
      const fetchLatestSale = async () => {
        try {
          const latestSale = await apiClient.sales.getLatestWithItems();
          
          if (latestSale) {
            // Convert UiSaleItem array to CartItem format for previousBill display
            const convertedItems = latestSale.items.map(saleItem => ({
              id: saleItem.product_id_val,
              name: saleItem.product_name,
              quantity: saleItem.quantity,
              unit_price: saleItem.unit_price,
              subtotal: saleItem.subtotal,
              selling_price: saleItem.unit_price,
              current_stock: 0, // Not needed for display
              product_id: saleItem.product_id.toString(),
              category_id: 0,
              category_name: '',
            })) as CartItem[];
            
            const previousBillData = {
              bill_number: latestSale.bill_number,
              items: convertedItems,
              subtotal: latestSale.subtotal,
              discount: latestSale.discount_amount,
              total: latestSale.total_amount,
              created_at: latestSale.date_time,
            };
            
            setPreviousBill(previousBillData);
            console.log('[Latest Sale Fetched for Previous Bill Summary]', previousBillData);
          }
        } catch (error) {
          console.error('Error fetching latest sale:', error);
          // Silent fail - it's okay if there's no previous bill
        }
      };

      fetchLatestSale();
    }, []);

    // Toast Notification State
    const [toast, setToast] = useState<{ message: string; type: 'success' | 'close' | 'error'; visible: boolean; key: number }>({ message: '', type: 'success', visible: false, key: 0 });

    // Toast Helper
    const showToast = (message: string, type: 'success' | 'close' | 'error') => {
      console.log('[Toast Triggered]', { message, type });
      setToast(prev => ({ message, type, visible: true, key: prev.key + 1 }));
      setTimeout(() => setToast(t => ({ ...t, visible: false })), 3000);
    };
  // Cart and bill state
  const [cart, setCart] = useState<CartItem[]>([]);
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [stockError, setStockError] = useState<string | null>(null);
  // Cash Counter state
  const [isCounterOpen, setIsCounterOpen] = useState(() => {
    if (typeof window === 'undefined') return false;
    return localStorage.getItem(COUNTER_STORAGE_KEY) === 'true';
  });
  // Payment method & discount state
  const [paymentMethod, setPaymentMethod] = useState<'Cash' | 'Card'>('Cash');
  
  // Discount state - Smart discounts instead of manual input
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
  
  const [availableDiscounts, setAvailableDiscounts] = useState<AvailableDiscount[]>([]);
  const [selectedDiscount, setSelectedDiscount] = useState<AvailableDiscount | null>(null);
  const [calculatedDiscountAmount, setCalculatedDiscountAmount] = useState(0);
  const [discountsError, setDiscountsError] = useState<string | null>(null);
  const [discountsLoading, setDiscountsLoading] = useState(true);

  // Previous Bill Summary State
  const [previousBill, setPreviousBill] = useState<{
    bill_number: string;
    items: CartItem[];
    subtotal: number;
    discount: number;
    total: number;
    created_at?: string;
  } | null>(null);

  // --- Discount Computation Logic ---
  const isDiscountApplicable = (discount: AvailableDiscount): boolean => {
    if (cart.length === 0) return false;

    if (discount.applicable_to === 'All') {
      // Applies to entire cart
      return true;
    } else if (discount.applicable_to === 'Category') {
      // Only applicable if cart contains item from target category
      return cart.some(item => item.category_id === discount.target_category_id);
    } else if (discount.applicable_to === 'Product') {
      // Only applicable if cart contains target product
      return cart.some(item => item.id === discount.target_product_id);
    }
    return false;
  };

  const calculateDiscountAmount = (discount: AvailableDiscount, subtotal: number): number => {
    const value = toNumber(discount.value);

    if (discount.discount_type === 'Percentage') {
      // Percentage: apply to subtotal
      return (subtotal * value) / 100;
    } else {
      // FixedAmount: return fixed value (capped at subtotal)
      return Math.min(value, subtotal);
    }
  };

  // --- Update discount when selection changes or cart changes ---
  useEffect(() => {
    if (!selectedDiscount || cart.length === 0) {
      setCalculatedDiscountAmount(0);
      return;
    }

    // Check if discount still applies
    if (!isDiscountApplicable(selectedDiscount)) {
      console.warn(`[Discount] Selected discount no longer applies with current cart`);
      setSelectedDiscount(null);
      setCalculatedDiscountAmount(0);
      showToast(`Discount "${selectedDiscount.name}" no longer applies`, 'close');
      return;
    }

    // Recalculate discount amount based on current subtotal
    const subtotal = cart.reduce((sum, item) => sum + item.subtotal, 0);
    const newDiscountAmount = calculateDiscountAmount(selectedDiscount, subtotal);
    setCalculatedDiscountAmount(newDiscountAmount);
  }, [selectedDiscount, cart]);

  // --- Handle discount selection with validation ---
  const handleSelectDiscount = (discount: AvailableDiscount | null) => {
    console.log('[Discount Selected]', discount);

    if (!discount) {
      setSelectedDiscount(null);
      setCalculatedDiscountAmount(0);
      return;
    }

    // Validate if discount applies to current cart
    if (!isDiscountApplicable(discount)) {
      showToast(
        `Discount "${discount.name}" is not applicable to items in your cart`,
        'close'
      );
      return;
    }

    setSelectedDiscount(discount);
  };

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

  const handleCheckout = async () => {
    if (cart.length === 0) return;

    // --- Build API Payload (matches Django sales + sale_items schema) ---
    const payload = {
      payment_method: paymentMethod,
      items: cart.map(item => ({
        product_id: item.id,
        quantity: String(item.quantity),  // Backend expects quantity as string
        unit_price: String(item.unit_price),
        subtotal: String(item.subtotal),
      })),
    };

    try {
      console.log('[Checkout Payload]', JSON.stringify(payload, null, 2));
      
      // --- Make API call to save sale to backend ---
      const response = await apiClient.sales.create(payload as any);
      
      console.log('[Sale Created Successfully]', response);
      showToast(`Bill ${currentBillNumber} saved successfully!`, 'success');

      // Save current bill as "previous bill" for display
      const subtotal = cart.reduce((sum, item) => sum + item.subtotal, 0);
      const total = subtotal - calculatedDiscountAmount;
      setPreviousBill({
        bill_number: currentBillNumber,
        items: cart,
        subtotal: subtotal,
        discount: calculatedDiscountAmount,
        total: total,
        created_at: new Date().toISOString(),
      });

      // Reset for next bill
      setCart([]);
      setSelectedDiscount(null);
      setCalculatedDiscountAmount(0);
      setPaymentMethod('Cash');
      billCounter.current += 1;
      setCurrentBillNumber(generateBillNumber(billCounter.current));
    } catch (error) {
      const errorMsg = error instanceof Error ? error.message : 'Failed to save bill';
      console.error('[Checkout Error]', error);
      showToast(`Error saving bill: ${errorMsg}`, 'error');
    }
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

  // Keep counter state in sync across tabs/windows.
  useEffect(() => {
    const handleStorage = (event: StorageEvent) => {
      if (event.key !== COUNTER_STORAGE_KEY) return;
      setIsCounterOpen(event.newValue === 'true');
    };

    window.addEventListener('storage', handleStorage);
    return () => window.removeEventListener('storage', handleStorage);
  }, []);

  const handleToggle = async () => {
    if (!isCounterOpen) {
      setIsCounterOpen(true);
      localStorage.setItem(COUNTER_STORAGE_KEY, 'true');
      try {
        await apiClient.notifications.sendCounterStatus('opened');
      } catch (error) {
        console.error('[Counter Status Notification Error - Open]', error);
      }
      notify(true);
    } else {
      if (window.confirm('Close counter?')) {
        setIsCounterOpen(false);
        localStorage.removeItem(COUNTER_STORAGE_KEY);
        try {
          await apiClient.notifications.sendCounterStatus('closed');
        } catch (error) {
          console.error('[Counter Status Notification Error - Close]', error);
        }
        setTimeout(() => notify(false), 10); // ensure state updates before showing toast
      }
    }
  };

  // Generate PDF from previous bill and open in new tab
  const generateAndOpenPDF = async () => {
    if (!previousBill || !printableRef.current) return;

    try {
      // Create a new window to render the bill without Tailwind styles causing issues
      const printWindow = window.open('', '', 'height=800,width=600');
      if (!printWindow) {
        throw new Error('Failed to open window for PDF generation');
      }

      // Build the receipt HTML without Tailwind classes
      const receiptHTML = `
        <!DOCTYPE html>
        <html>
        <head>
          <meta charset="UTF-8">
          <style>
            * {
              margin: 0;
              padding: 0;
              box-sizing: border-box;
            }
            body {
              font-family: monospace;
              line-height: 1.6;
              background: white;
              color: black;
              padding: 20px;
            }
            .bill-header {
              text-align: center;
              margin-bottom: 20px;
              border-bottom: 1px solid #ddd;
              padding-bottom: 10px;
            }
            .bill-header h2 {
              margin: 0;
              font-size: 18px;
              font-weight: bold;
            }
            .bill-header p {
              margin: 5px 0;
              font-size: 12px;
            }
            .bill-meta {
              margin-bottom: 15px;
              font-size: 12px;
            }
            .bill-meta-row {
              display: flex;
              justify-content: space-between;
              margin-bottom: 5px;
            }
            .divider {
              border-top: 1px solid #ddd;
              margin: 15px 0;
            }
            table {
              width: 100%;
              margin-bottom: 15px;
              font-size: 12px;
              border-collapse: collapse;
            }
            thead {
              border-bottom: 1px solid #ddd;
            }
            th {
              text-align: left;
              padding-bottom: 5px;
              font-weight: bold;
            }
            td {
              padding: 5px 0;
              border-bottom: 1px solid #eee;
            }
            .qty-col {
              text-align: center;
            }
            .price-col {
              text-align: right;
            }
            .total-col {
              text-align: right;
            }
            .bill-totals {
              font-size: 12px;
              margin-bottom: 15px;
            }
            .total-row {
              display: flex;
              justify-content: space-between;
              margin-bottom: 5px;
            }
            .discount-row {
              display: flex;
              justify-content: space-between;
              margin-bottom: 5px;
              color: #28a745;
            }
            .final-total {
              display: flex;
              justify-content: space-between;
              margin-top: 10px;
              padding-top: 10px;
              border-top: 1px solid #ddd;
              font-weight: bold;
              font-size: 14px;
            }
            .bill-footer {
              text-align: center;
              margin-top: 20px;
              font-size: 11px;
              border-top: 1px solid #ddd;
              padding-top: 10px;
            }
            .bill-footer p {
              margin: 5px 0;
              color: #666;
            }
          </style>
        </head>
        <body>
          <div class="bill-header">
            <h2>BakeryOS</h2>
            <p>Manager Portal - Receipt</p>
          </div>

          <div class="bill-meta">
            <div class="bill-meta-row">
              <span>Bill Number:</span>
              <span style="font-weight: bold;">${previousBill.bill_number}</span>
            </div>
            <div class="bill-meta-row">
              <span>Date:</span>
              <span>${previousBill.created_at ? new Date(previousBill.created_at).toLocaleString() : 'N/A'}</span>
            </div>
          </div>

          <div class="divider"></div>

          <table>
            <thead>
              <tr>
                <th>Item</th>
                <th class="qty-col">Qty</th>
                <th class="price-col">Price</th>
                <th class="total-col">Total</th>
              </tr>
            </thead>
            <tbody>
              ${previousBill.items.map((item) => `
                <tr>
                  <td>${item.name}</td>
                  <td class="qty-col">${item.quantity}</td>
                  <td class="price-col">Rs. ${item.unit_price.toLocaleString()}</td>
                  <td class="total-col">Rs. ${item.subtotal.toLocaleString()}</td>
                </tr>
              `).join('')}
            </tbody>
          </table>

          <div class="divider"></div>

          <div class="bill-totals">
            <div class="total-row">
              <span>Subtotal:</span>
              <span>Rs. ${previousBill.subtotal.toLocaleString()}</span>
            </div>
            ${previousBill.discount > 0 ? `
              <div class="discount-row">
                <span>Discount:</span>
                <span>-Rs. ${previousBill.discount.toLocaleString()}</span>
              </div>
            ` : ''}
            <div class="final-total">
              <span>Total:</span>
              <span>Rs. ${previousBill.total.toLocaleString()}</span>
            </div>
          </div>

          <div class="bill-footer">
            <p>Thank you for your purchase!</p>
            <p>Printed: ${new Date().toLocaleString()}</p>
          </div>
        </body>
        </html>
      `;

      // Write the HTML to the new window
      printWindow.document.write(receiptHTML);
      printWindow.document.close();

      // Wait a moment for the content to render, then convert to canvas and PDF
      setTimeout(() => {
        html2canvas(printWindow.document.body, {
          scale: 2,
          useCORS: true,
          backgroundColor: '#ffffff',
          logging: false,
          allowTaint: true,
        })
          .then((canvas) => {
            // Create PDF
            const pdf = new jsPDF({
              orientation: 'portrait',
              unit: 'mm',
              format: 'a4',
            });

            const imgData = canvas.toDataURL('image/png');
            const imgWidth = 210;
            const imgHeight = (canvas.height * imgWidth) / canvas.width;

            pdf.addImage(imgData, 'PNG', 0, 0, imgWidth, imgHeight);

            // Open PDF in new tab
            const pdfBlob = pdf.output('blob');
            const pdfUrl = URL.createObjectURL(pdfBlob);
            window.open(pdfUrl, '_blank');

            // Close the temporary window
            printWindow.close();

            showToast('PDF opened successfully!', 'success');
            console.log('[PDF Generated]', { bill_number: previousBill.bill_number });
          })
          .catch((error) => {
            console.error('Error converting to canvas:', error);
            printWindow.close();
            showToast('Failed to generate PDF', 'error');
          });
      }, 500);
    } catch (error) {
      console.error('Error generating PDF:', error);
      showToast('Failed to generate PDF', 'error');
    }
  };

  // Trigger browser print dialog for testing
  const triggerPrint = () => {
    if (!previousBill || !printableRef.current) return;

    try {
      // Temporarily show the printable element
      const originalDisplay = printableRef.current.style.display;
      printableRef.current.style.display = 'block';

      // Open browser print dialog
      window.print();

      // Restore original display (if needed)
      printableRef.current.style.display = originalDisplay;

      console.log('[Print Dialog Opened]', { bill_number: previousBill.bill_number });
    } catch (error) {
      console.error('Error opening print dialog:', error);
      showToast('Failed to open print dialog', 'error');
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
              : toast.type === 'error'
              ? 'bg-red-100 text-red-800 border-red-600'
              : 'bg-gray-800 text-white border-gray-500'
          }`}
          style={{ minWidth: '300px', boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1)' }}
        >
          <span className="text-2xl">{toast.type === 'success' ? '✅' : toast.type === 'error' ? '❌' : '🔒'}</span>
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
                {categoriesLoading ? (
                  <p className="text-gray-500 text-sm">Loading categories...</p>
                ) : (
                  categories.map(category => (
                    <Badge
                      key={category.id}
                      onClick={() => isCounterOpen && setSelectedCategory(category.name)}
                      className={`cursor-pointer px-4 py-2 transition-colors ${
                        selectedCategory === category.name
                          ? 'bg-orange-600 text-white hover:bg-orange-700'
                          : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                      } ${!isCounterOpen ? 'pointer-events-none opacity-60' : ''}`}
                    >
                      {category.name}
                    </Badge>
                  ))
                )}
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
                    {previousBill ? (
                      <>
                        <p className="text-sm text-gray-700">
                          <span className="text-orange-700">Bill #{previousBill.bill_number}</span> • {previousBill.items.map(item => `${item.name} (x${item.quantity})`).join(', ')}
                        </p>
                        <p className="text-sm text-gray-600">
                          <span className="tabular-nums">Total: Rs. {previousBill.total.toLocaleString()}</span> | <span className="tabular-nums">Discount: Rs. {previousBill.discount.toLocaleString()}</span>
                        </p>
                      </>
                    ) : (
                      <p className="text-sm text-gray-500 italic">No previous bill yet</p>
                    )}
                  </div>
                  {/* Action Buttons */}
                  <div className="flex gap-3">
                    <button
                      onClick={generateAndOpenPDF}
                      className="flex-1 px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 rounded-lg flex items-center justify-center gap-2 transition-colors"
                      disabled={!isCounterOpen || !previousBill}
                    >
                      <FileText className="w-4 h-4" />
                      <span className="text-sm">Open PDF</span>
                    </button>
                    <button
                      onClick={triggerPrint}
                      className="flex-1 px-4 py-2 border border-gray-300 hover:bg-gray-50 text-gray-700 rounded-lg flex items-center justify-center gap-2 transition-colors"
                      disabled={!isCounterOpen || !previousBill}
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
              availableDiscounts={availableDiscounts}
              selectedDiscount={selectedDiscount}
              onSelectDiscount={handleSelectDiscount}
              calculatedDiscountAmount={calculatedDiscountAmount}
              discountsLoading={discountsLoading}
            />
          </div>
        </div>
      </div>

      {/* Hidden Printable Bill Component - for PDF generation and print dialog */}
      {previousBill && (
        <div
          ref={printableRef}
          style={{ display: 'none' }}
          className="printable-bill"
        >
          <div style={{ padding: '20px', fontFamily: 'monospace', lineHeight: '1.6', backgroundColor: 'white', color: 'black' }}>
            {/* Header */}
            <div style={{ textAlign: 'center', marginBottom: '20px', borderBottom: '1px solid #ddd', paddingBottom: '10px' }}>
              <h2 style={{ margin: '0', fontSize: '18px', fontWeight: 'bold' }}>BakeryOS</h2>
              <p style={{ margin: '5px 0', fontSize: '12px' }}>Manager Portal - Receipt</p>
            </div>

            {/* Bill Number & Date */}
            <div style={{ marginBottom: '15px', fontSize: '12px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
                <span>Bill Number:</span>
                <span style={{ fontWeight: 'bold' }}>{previousBill.bill_number}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span>Date:</span>
                <span>{previousBill.created_at ? new Date(previousBill.created_at).toLocaleString() : 'N/A'}</span>
              </div>
            </div>

            {/* Divider */}
            <div style={{ borderTop: '1px solid #ddd', marginBottom: '15px' }}></div>

            {/* Items Table */}
            <table style={{ width: '100%', marginBottom: '15px', fontSize: '12px', borderCollapse: 'collapse' }}>
              <thead>
                <tr style={{ borderBottom: '1px solid #ddd' }}>
                  <th style={{ textAlign: 'left', paddingBottom: '5px', fontWeight: 'bold' }}>Item</th>
                  <th style={{ textAlign: 'center', paddingBottom: '5px', fontWeight: 'bold' }}>Qty</th>
                  <th style={{ textAlign: 'right', paddingBottom: '5px', fontWeight: 'bold' }}>Price</th>
                  <th style={{ textAlign: 'right', paddingBottom: '5px', fontWeight: 'bold' }}>Total</th>
                </tr>
              </thead>
              <tbody>
                {previousBill.items.map((item, idx) => (
                  <tr key={idx} style={{ borderBottom: '1px solid #eee' }}>
                    <td style={{ paddingTop: '5px', paddingBottom: '5px' }}>{item.name}</td>
                    <td style={{ textAlign: 'center', paddingTop: '5px', paddingBottom: '5px' }}>{item.quantity}</td>
                    <td style={{ textAlign: 'right', paddingTop: '5px', paddingBottom: '5px' }}>Rs. {item.unit_price.toLocaleString()}</td>
                    <td style={{ textAlign: 'right', paddingTop: '5px', paddingBottom: '5px' }}>Rs. {item.subtotal.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>

            {/* Divider */}
            <div style={{ borderTop: '1px solid #ddd', marginBottom: '10px' }}></div>

            {/* Totals */}
            <div style={{ fontSize: '12px', marginBottom: '15px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px' }}>
                <span>Subtotal:</span>
                <span>Rs. {previousBill.subtotal.toLocaleString()}</span>
              </div>
              {previousBill.discount > 0 && (
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '5px', color: '#28a745' }}>
                  <span>Discount:</span>
                  <span>-Rs. {previousBill.discount.toLocaleString()}</span>
                </div>
              )}
              <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: '10px', paddingTop: '10px', borderTop: '1px solid #ddd', fontWeight: 'bold', fontSize: '14px' }}>
                <span>Total:</span>
                <span>Rs. {previousBill.total.toLocaleString()}</span>
              </div>
            </div>

            {/* Footer */}
            <div style={{ textAlign: 'center', marginTop: '20px', fontSize: '11px', borderTop: '1px solid #ddd', paddingTop: '10px' }}>
              <p style={{ margin: '5px 0' }}>Thank you for your purchase!</p>
              <p style={{ margin: '5px 0', color: '#666' }}>Printed: {new Date().toLocaleString()}</p>
            </div>
          </div>
        </div>
      )}

      {/* Print Stylesheet */}
      <style>{`
        @media print {
          body {
            margin: 0;
            padding: 0;
          }
          * {
            -webkit-print-color-adjust: exact !important;
            color-adjust: exact !important;
            print-color-adjust: exact !important;
          }
          .printable-bill {
            display: block !important;
            padding: 0;
            margin: 0;
          }
          .printable-bill * {
            visibility: visible;
          }
        }
      `}</style>
    </>
  );
}