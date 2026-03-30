import React from 'react';
import { X, Calendar, Clock, CreditCard, User } from 'lucide-react';
import { toNumber } from '../../utils/numericUtils';

interface SaleItem {
  id: number;
  product_id: number;
  product_name: string;
  quantity: number;
  unit_price: number;
  subtotal: number;
}

interface ViewSaleModalProps {
  isOpen: boolean;
  onClose: () => void;
  sale: {
    id: number;
    bill_number: string;
    cashier_name: string;
    payment_method: string;
    subtotal: number;
    discount_amount: number;
    discount_name?: string | null;
    total_amount: number;
    date_time: string;
    items?: SaleItem[];
  } | null;
}

export const ViewSaleModal: React.FC<ViewSaleModalProps> = ({ isOpen, onClose, sale }) => {
  if (!isOpen || !sale) return null;

  const items = sale.items || [];

  const formatDateTime = (dateTimeStr: string) => {
    const d = new Date(dateTimeStr);
    const datePart = d.toLocaleString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
    const timePart = d.toLocaleString('en-US', {
      hour: 'numeric',
      minute: '2-digit',
      hour12: true,
    });
    return { date: datePart, time: timePart };
  };

  const { date, time } = formatDateTime(sale.date_time);

  return (
    <div className="fixed inset-0 z-[100] bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white w-full max-w-4xl max-h-[92vh] rounded-3xl shadow-2xl flex flex-col relative overflow-hidden border border-gray-200">
        
        {/* ===== STICKY HEADER WITH BILL ID ===== */}
        <div className="sticky top-0 z-20 bg-gradient-to-r from-neutral-100 via-white to-neutral-50 border-b-2 border-neutral-200 px-10 py-8 shadow-sm">
          <div className="flex items-center justify-between">
            <div className="flex-1">
              <div className="text-sm font-bold text-gray-600 uppercase tracking-widest mb-2">
                Bill Number
              </div>
              <div className="text-4xl font-black text-gray-900 tracking-tight">
                {sale.bill_number}
              </div>
            </div>
            <button
              onClick={onClose}
              className="p-3 rounded-xl hover:bg-gray-100 active:bg-gray-200 transition-colors duration-150 text-gray-400 hover:text-gray-600"
              aria-label="Close"
            >
              <X className="w-7 h-7" />
            </button>
          </div>
        </div>

        {/* ===== CONTENT AREA ===== */}
        <div className="flex-1 overflow-y-auto px-10 py-8 space-y-8">
          
          {/* ===== SUMMARY DETAILS CARDS ===== */}
          <div className="grid grid-cols-4 gap-4">
            {/* Date */}
            <div className="bg-gradient-to-br from-sky-50 to-sky-25 border border-sky-200 rounded-2xl p-5 shadow-sm hover:shadow-md transition-shadow duration-200">
              <div className="flex items-center gap-3 mb-3">
                <div className="p-2.5 bg-sky-100 rounded-lg">
                  <Calendar className="w-5 h-5 text-sky-600" />
                </div>
                <div className="text-xs font-bold text-sky-700 uppercase tracking-wide">Date</div>
              </div>
              <div className="text-base font-bold text-gray-900">
                {date}
              </div>
            </div>

            {/* Time */}
            <div className="bg-gradient-to-br from-amber-50 to-amber-25 border border-amber-200 rounded-2xl p-5 shadow-sm hover:shadow-md transition-shadow duration-200">
              <div className="flex items-center gap-3 mb-3">
                <div className="p-2.5 bg-amber-100 rounded-lg">
                  <Clock className="w-5 h-5 text-amber-600" />
                </div>
                <div className="text-xs font-bold text-amber-700 uppercase tracking-wide">Time</div>
              </div>
              <div className="text-base font-bold text-gray-900">
                {time}
              </div>
            </div>

            {/* Payment Method */}
            <div className="bg-gradient-to-br from-purple-50 to-purple-25 border border-purple-200 rounded-2xl p-5 shadow-sm hover:shadow-md transition-shadow duration-200">
              <div className="flex items-center gap-3 mb-3">
                <div className="p-2.5 bg-purple-100 rounded-lg">
                  <CreditCard className="w-5 h-5 text-purple-600" />
                </div>
                <div className="text-xs font-bold text-purple-700 uppercase tracking-wide">Payment</div>
              </div>
              <div className="text-base font-bold text-gray-900">
                {sale.payment_method || 'Cash'}
              </div>
            </div>

            {/* Cashier */}
            <div className="bg-gradient-to-br from-emerald-50 to-emerald-25 border border-emerald-200 rounded-2xl p-5 shadow-sm hover:shadow-md transition-shadow duration-200">
              <div className="flex items-center gap-3 mb-3">
                <div className="p-2.5 bg-emerald-100 rounded-lg">
                  <User className="w-5 h-5 text-emerald-600" />
                </div>
                <div className="text-xs font-bold text-emerald-700 uppercase tracking-wide">Cashier</div>
              </div>
              <div className="text-base font-bold text-gray-900 truncate">
                {sale.cashier_name || 'N/A'}
              </div>
            </div>
          </div>

          {/* ===== ITEMS TABLE SECTION ===== */}
          <div>
            <h3 className="text-xl font-black text-gray-900 uppercase tracking-tight mb-4">
              Items Purchased
            </h3>
            
            <div className="border-2 border-gray-200 rounded-2xl overflow-hidden shadow-md">
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="bg-gray-900 text-white">
                      <th className="px-8 py-4 text-left font-bold text-sm uppercase tracking-wider">
                        Product
                      </th>
                      <th className="px-6 py-4 text-center font-bold text-sm uppercase tracking-wider w-20">
                        Qty
                      </th>
                      <th className="px-8 py-4 text-right font-bold text-sm uppercase tracking-wider">
                        Unit Price
                      </th>
                      <th className="px-8 py-4 text-right font-bold text-sm uppercase tracking-wider">
                        Subtotal
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {items.length > 0 ? (
                      items.map((item, idx) => (
                        <tr
                          key={idx}
                          className="hover:bg-gray-50 transition-colors duration-150 group"
                        >
                          <td className="px-8 py-4 font-bold text-gray-900 text-base">
                            {item.product_name}
                          </td>
                          <td className="px-6 py-4 text-center text-gray-700 font-semibold">
                            {item.quantity}
                          </td>
                          <td className="px-8 py-4 text-right text-gray-700 font-medium">
                            Rs. {toNumber(item.unit_price).toLocaleString()}
                          </td>
                          <td className="px-8 py-4 text-right font-bold text-emerald-600 text-base">
                            Rs. {toNumber(item.subtotal).toLocaleString()}
                          </td>
                        </tr>
                      ))
                    ) : (
                      <tr>
                        <td colSpan={4} className="px-8 py-12 text-center text-gray-400 font-medium">
                          No items found
                        </td>
                      </tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>

          {/* ===== TOTALS SECTION ===== */}
          <div className="flex flex-col items-end gap-4">
            {/* Subtotal and Discount (left-aligned in their container) */}
            <div className="w-full max-w-sm space-y-3 text-right">
              <div className="flex justify-between items-center px-4 py-2 bg-gray-50 rounded-lg">
                <span className="text-sm font-semibold text-gray-600">Subtotal:</span>
                <span className="text-sm font-bold text-gray-900">
                  Rs. {toNumber(sale.subtotal).toLocaleString()}
                </span>
              </div>

              {sale.discount_amount > 0 && (
                <div className="flex justify-between items-center px-4 py-2 bg-green-50 rounded-lg">
                  <span className="text-sm font-semibold text-green-700">
                    Discount {sale.discount_name ? `(${sale.discount_name})` : ''}:
                  </span>
                  <span className="text-sm font-bold text-green-700">
                    -Rs. {toNumber(sale.discount_amount).toLocaleString()}
                  </span>
                </div>
              )}
            </div>

            {/* Final Total - Prominent Box */}
            <div className="w-full max-w-sm bg-gradient-to-br from-emerald-500 via-green-500 to-emerald-600 rounded-2xl p-6 shadow-xl border-2 border-emerald-400">
              <div className="text-emerald-50/70 text-xs font-black uppercase tracking-widest mb-2">
                Final Total Amount
              </div>
              <div className="text-5xl font-black text-white drop-shadow-lg tracking-tight">
                Rs. {toNumber(sale.total_amount).toLocaleString()}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
