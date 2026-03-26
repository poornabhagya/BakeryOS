import React from 'react';
import { Clock } from 'lucide-react';
import { toNumber, subtractNumeric } from '../../utils/numericUtils';

interface Ingredient {
  name: string;
  qty: number;
  unit: string;
}

interface ViewProductModalProps {
  isOpen: boolean;
  onClose: () => void;
  item: {
    id: string;
    name: string;
    selling_price?: number;
    cost_price?: number;
    shelfLife?: string;
    category_name: string;
  } | null;
}

function getMockIngredients(itemId: string): Ingredient[] {
  return [
    { name: 'Flour', qty: 500, unit: 'g' },
    { name: 'Sugar', qty: 100, unit: 'g' },
    { name: 'Butter', qty: 200, unit: 'g' },
    { name: 'Eggs', qty: 3, unit: 'pcs' },
  ];
}

export const ViewProductModal: React.FC<ViewProductModalProps> = ({ isOpen, onClose, item }) => {
  if (!isOpen || !item) return null;
  const ingredients = getMockIngredients(item.id);
  // Safely calculate profit even if prices come as strings from API
  const profit = subtractNumeric(toNumber(item.selling_price), toNumber(item.cost_price));

  return (
    <div className="fixed inset-0 z-[100] bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white w-full max-w-lg h-[85vh] rounded-3xl shadow-2xl flex flex-col relative overflow-hidden border border-orange-100">
        {/* Sticky Orange Header */}
        <div className="sticky top-0 z-20 bg-gradient-to-r from-orange-50/90 to-white/90 border-b border-orange-100 flex items-center justify-between px-8 py-5 shadow-sm">
          <div className="flex items-center gap-2 flex-wrap">
            <h2 className="text-2xl font-extrabold text-gray-900 leading-tight mr-2 tracking-tight drop-shadow-sm">{item.name}</h2>
            <span className="inline-block px-2 py-1 bg-orange-200 text-orange-800 text-xs font-semibold rounded-full tracking-wide shadow-sm border border-orange-300">{item.id}</span>
            <span className="inline-block px-2 py-1 bg-orange-100 text-orange-800 text-xs font-semibold rounded-full ml-2 border border-orange-200">{item.category_name}</span>
          </div>
          <button onClick={onClose} className="p-2 rounded-lg hover:bg-orange-100 active:bg-orange-200 transition-colors duration-150" aria-label="Close">
            <span className="text-gray-400 text-2xl">×</span>
          </button>
        </div>

        {/* Divider */}
        <div className="h-[1.5px] w-full bg-gradient-to-r from-orange-100/80 via-orange-200/80 to-orange-100/80" />

        {/* Unified Stats Bar */}
        <div className="flex w-full border border-orange-100 rounded-2xl overflow-hidden mb-6 shadow-md bg-gradient-to-r from-orange-50/60 to-white/60">
          <div className="flex-1 min-w-0 p-5 text-center bg-white/90 border-r border-orange-100 last:border-r-0 flex flex-col justify-center hover:bg-orange-50/60 transition-colors duration-150">
            <div className="text-xs text-gray-500 font-semibold uppercase mb-1 tracking-wide">Selling Price</div>
            <div className="text-xl font-extrabold text-green-600 drop-shadow-sm">Rs. {toNumber(item.selling_price).toFixed(2)}</div>
          </div>
          <div className="flex-1 min-w-0 p-5 text-center bg-white/90 border-r border-orange-100 last:border-r-0 flex flex-col justify-center hover:bg-orange-50/60 transition-colors duration-150">
            <div className="text-xs text-gray-500 font-semibold uppercase mb-1 tracking-wide">Cost Price</div>
            <div className="text-base font-semibold text-gray-500">Rs. {toNumber(item.cost_price).toFixed(2)}</div>
          </div>
          <div className="flex-1 min-w-0 p-5 text-center bg-white/90 border-r border-orange-100 last:border-r-0 flex flex-col justify-center hover:bg-orange-50/60 transition-colors duration-150">
            <div className="text-xs text-gray-500 font-semibold uppercase mb-1 tracking-wide">Margin</div>
            <div className="text-base font-bold text-orange-600">Rs. {profit.toFixed(2)}</div>
          </div>
          <div className="flex-1 min-w-0 p-5 text-center bg-white/90 flex flex-col justify-center hover:bg-orange-50/60 transition-colors duration-150">
            <div className="text-xs text-gray-500 font-semibold uppercase mb-1 tracking-wide">Shelf Life</div>
            <div className="flex items-center justify-center gap-1 text-base font-medium text-gray-700">
              <Clock className="w-4 h-4 text-gray-400" />{item.shelfLife ?? '--'}
            </div>
          </div>
        </div>

        {/* Recipe Table */}
        <div className="flex-1 flex flex-col min-h-0">
          <div className="sticky top-0 z-10 bg-white/95 px-8 pt-2 pb-2 border-b border-orange-100 shadow-sm">
            <span className="text-sm font-bold text-gray-700 uppercase tracking-wide">Recipe / Ingredients</span>
          </div>
          <div className="flex-1 overflow-y-auto px-8 pb-6">
            <table className="w-full text-xs rounded-xl overflow-hidden">
              <thead>
                <tr className="bg-orange-50/80">
                  <th className="px-3 py-2 text-left font-bold uppercase text-orange-700 tracking-wide">Ingredient</th>
                  <th className="px-3 py-2 text-center font-bold uppercase text-orange-700 tracking-wide">Qty</th>
                  <th className="px-3 py-2 text-center font-bold uppercase text-orange-700 tracking-wide">Unit</th>
                </tr>
              </thead>
              <tbody>
                {ingredients.map((ing, idx) => (
                  <tr key={idx} className="border-b last:border-b-0 bg-white hover:bg-orange-50/80 transition-colors duration-100">
                    <td className="px-3 py-2 font-medium text-gray-800 text-left">{ing.name}</td>
                    <td className="px-3 py-2 text-center text-gray-700">{ing.qty}</td>
                    <td className="px-3 py-2 text-center text-gray-600">{ing.unit}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
};
