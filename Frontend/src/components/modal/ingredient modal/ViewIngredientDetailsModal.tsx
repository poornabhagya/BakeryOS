import React from 'react';
import { Clock } from 'lucide-react';

interface ViewIngredientDetailsModalProps {
  isOpen: boolean;
  onClose: () => void;
  item: {
    id: string;
    name: string;
    category: string;
    trackingType: string;
    lowStockValue?: number;
    supplier: string;
    supplierContact?: string;
  } | null;
}



export const ViewIngredientDetailsModal: React.FC<ViewIngredientDetailsModalProps> = ({ isOpen, onClose, item }) => {
  if (!isOpen || !item) return null;

  return (
    <div className="fixed inset-0 z-[100] bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white w-full max-w-lg rounded-3xl shadow-2xl flex flex-col relative overflow-hidden border border-orange-100 animate-fade-in">
        {/* Sticky Orange Header */}
        <div className="sticky top-0 z-20 bg-gradient-to-r from-orange-100/90 to-white/90 border-b border-orange-200 flex items-center justify-between px-8 py-5 shadow-sm">
          <div className="flex items-center gap-2 flex-wrap">
            <h2 className="text-2xl font-extrabold text-orange-700 leading-tight mr-2 tracking-tight drop-shadow-sm">Ingredient Details</h2>
            <span className="inline-block px-2 py-1 bg-orange-200 text-orange-800 text-xs font-semibold rounded-full tracking-wide shadow-sm border border-orange-300">{item.id}</span>
          </div>
          <button onClick={onClose} className="p-2 rounded-lg hover:bg-orange-100 active:bg-orange-200 transition-colors duration-150" aria-label="Close">
            <span className="text-gray-400 text-2xl">×</span>
          </button>
        </div>

        {/* Divider */}
        <div className="h-[2px] w-full bg-gradient-to-r from-orange-100 via-orange-200 to-orange-100" />

        {/* Ingredient Details Section */}
        <div className="flex flex-col gap-6 p-8 bg-orange-50/40">
          <div className="mb-2">
            <div className="text-sm font-bold text-orange-700 uppercase tracking-wider mb-2">Basic Information</div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 bg-white rounded-xl p-4 border border-orange-100 shadow-sm">
              <div>
                <div className="text-xs text-gray-500 font-semibold uppercase mb-1 tracking-wide">Item ID</div>
                <div className="text-base font-semibold text-gray-700">{item.id}</div>
              </div>
              <div>
                <div className="text-xs text-gray-500 font-semibold uppercase mb-1 tracking-wide">Item Name</div>
                <div className="text-base font-semibold text-gray-700">{item.name}</div>
              </div>
              <div>
                <div className="text-xs text-gray-500 font-semibold uppercase mb-1 tracking-wide">Category</div>
                <div className="text-base font-semibold text-gray-700">{item.category}</div>
              </div>
              <div>
                <div className="text-xs text-gray-500 font-semibold uppercase mb-1 tracking-wide">Stock Tracking Type</div>
                <div className="text-base font-semibold text-gray-700">{item.trackingType}</div>
              </div>
            </div>
          </div>
          <div className="mb-2">
            <div className="text-sm font-bold text-orange-700 uppercase tracking-wider mb-2">Stock Status Thresholds</div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 bg-white rounded-xl p-4 border border-orange-100 shadow-sm">
              <div>
                <div className="text-xs text-gray-500 font-semibold uppercase mb-1 tracking-wide">Low Stock Value</div>
                <div className="text-base font-semibold text-gray-700">{typeof item.lowStockValue === 'number' ? item.lowStockValue : '--'}</div>
              </div>
            </div>
          </div>
          <div>
            <div className="text-sm font-bold text-orange-700 uppercase tracking-wider mb-2">Supplier Details</div>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 bg-white rounded-xl p-4 border border-orange-100 shadow-sm">
              <div>
                <div className="text-xs text-gray-500 font-semibold uppercase mb-1 tracking-wide">Supplier Name</div>
                <div className="text-base font-semibold text-gray-700">{item.supplier}</div>
              </div>
              <div>
                <div className="text-xs text-gray-500 font-semibold uppercase mb-1 tracking-wide">Supplier Contact Number</div>
                <div className="text-base font-semibold text-gray-700">{item.supplierContact ?? '--'}</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
