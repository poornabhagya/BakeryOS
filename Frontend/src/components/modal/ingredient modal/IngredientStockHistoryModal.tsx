import React, { useState } from 'react';
import { X, Search, Plus } from 'lucide-react';
import { AddNewIngredientStockModal } from './AddNewIngredientStockModal';
import { AddWastageModal } from '../../modal/AddWastageModal'; // Check Path
import { useAuth } from '../../../context/AuthContext'; // 1. Auth Import

interface StockHistoryEntry {
  batchId: string;
  stockDate: string;
  expireDate: string;
  cost: number;
  quantity: number; 
  currentQty: number; 
  unit: string;
  note?: string;
}

interface Ingredient {
  id: string;
  name: string;
  trackingType: string;
}

interface IngredientStockHistoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  ingredient: Ingredient | null;
  history?: StockHistoryEntry[];
}

const dummyHistory: StockHistoryEntry[] = [
  { batchId: 'BID-001', stockDate: '2026-01-27', expireDate: '2026-02-10', cost: 1200, quantity: 20, currentQty: 20, unit: 'kg', note: 'Restocked from supplier' },
  { batchId: 'BID-002', stockDate: '2026-01-27', expireDate: '2026-02-05', cost: 300, quantity: 5, currentQty: 5, unit: 'kg', note: 'Used in production' },
  { batchId: 'BID-003', stockDate: '2026-01-27', expireDate: '2026-02-01', cost: 150, quantity: -2, currentQty: -2, unit: 'kg', note: 'Inventory correction' },
];

export const IngredientStockHistoryModal: React.FC<IngredientStockHistoryModalProps> = ({ isOpen, onClose, ingredient, history }) => {
  const { user } = useAuth(); // 2. Get User
  // 3. Define Permissions: Only Manager & Storekeeper can ADD Stock
  const canAddStock = user?.role === 'Manager' || user?.role === 'Storekeeper';

  const [search, setSearch] = useState('');
  const [addStockModalOpen, setAddStockModalOpen] = useState(false);
  const [stockEntries, setStockEntries] = useState<StockHistoryEntry[]>(history || dummyHistory);
  const [wastageModalOpen, setWastageModalOpen] = useState(false);
  const [selectedBatch, setSelectedBatch] = useState<StockHistoryEntry | null>(null);

  // Filter entries by search
  const filteredEntries = stockEntries.filter((entry: StockHistoryEntry) =>
    (entry.stockDate?.toLowerCase() ?? '').includes(search.toLowerCase()) ||
    (entry.expireDate?.toLowerCase() ?? '').includes(search.toLowerCase()) ||
    (entry.note?.toLowerCase().includes(search.toLowerCase()) ?? false)
  );

  const handleAddStock = (entry: StockHistoryEntry) => {
    setStockEntries([entry, ...stockEntries]);
  };

  if (!isOpen || !ingredient) return null;

  return (
    <div className="fixed inset-0 z-[100] bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white w-full max-w-2xl rounded-3xl shadow-2xl flex flex-col relative overflow-hidden border border-orange-100 animate-fade-in">
        {/* Header */}
        <div className="sticky top-0 z-20 bg-gradient-to-r from-orange-100/90 to-white/90 border-b border-orange-200 flex items-center justify-between px-8 py-5 shadow-sm">
          <h2 className="text-2xl font-extrabold text-orange-700 leading-tight tracking-tight drop-shadow-sm">Stock History - {ingredient.name}</h2>
          <button onClick={onClose} className="p-2 rounded-lg hover:bg-orange-100 active:bg-orange-200 transition-colors duration-150" aria-label="Close">
            <span className="text-gray-400 text-2xl">×</span>
          </button>
        </div>
        <div className="h-[2px] w-full bg-gradient-to-r from-orange-100 via-orange-200 to-orange-100" />
        
        {/* Toolbar */}
        <div className="flex items-center justify-between px-8 py-4 bg-white border-b border-orange-100">
          <div className="relative w-full max-w-xs">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400 w-4 h-4" />
            <input
              type="text"
              placeholder="Search stock history..."
              value={search}
              onChange={e => setSearch(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-100 focus:border-orange-500"
            />
          </div>
          
          {/* 4. Hide Add Stock Button for Baker (and others) */}
          {canAddStock && (
            <button
              onClick={() => setAddStockModalOpen(true)}
              className="ml-4 px-4 py-2 bg-orange-500 hover:bg-orange-600 text-white rounded-lg font-medium flex items-center gap-2 transition-colors"
            >
              <Plus className="w-4 h-4" />
              Add New Stock
            </button>
          )}
        </div>

        {/* Color label instruction */}
        <div className="flex gap-3 items-center text-xs px-8 pt-4 pb-2">
          <span className="px-2 py-1 rounded bg-green-100 text-green-700 font-semibold">In Stock &gt;= Low Stock Value</span>
          <span className="px-2 py-1 rounded bg-red-100 text-red-700 font-semibold">Low Stock &lt; Low Stock Value</span>
          <span className="px-2 py-1 rounded bg-red-100 text-red-700 font-semibold">Out of Stock = 0</span>
        </div>

        {/* Table */}
        <div className="flex-1 overflow-y-auto p-8 bg-orange-50/40">
          <table className="w-full text-sm rounded-xl overflow-hidden">
            <thead>
              <tr className="bg-orange-50/80">
                <th className="px-3 py-2 text-left font-bold uppercase text-orange-700 tracking-wide">Batch ID</th>
                <th className="px-3 py-2 text-left font-bold uppercase text-orange-700 tracking-wide">Stock Date</th>
                <th className="px-3 py-2 text-left font-bold uppercase text-orange-700 tracking-wide">Expire Date</th>
                <th className="px-3 py-2 text-right font-bold uppercase text-orange-700 tracking-wide">Cost</th>
                <th className="px-3 py-2 text-right font-bold uppercase text-orange-700 tracking-wide">Quantity</th>
                <th className="px-3 py-2 text-right font-bold uppercase text-orange-700 tracking-wide">Current Qty</th>
                <th className="px-3 py-2 text-left font-bold uppercase text-orange-700 tracking-wide">Note</th>
                <th className="px-3 py-2 text-center font-bold uppercase text-orange-700 tracking-wide">Action</th>
              </tr>
            </thead>
            <tbody>
              {filteredEntries.map((entry, idx) => (
                <tr key={idx} className="border-b last:border-b-0 bg-white hover:bg-orange-50/80 transition-colors duration-100">
                  <td className="px-3 py-2 text-gray-700">{entry.batchId}</td>
                  <td className="px-3 py-2 text-gray-700">{entry.stockDate}</td>
                  <td className="px-3 py-2 text-gray-700">{entry.expireDate}</td>
                  <td className="px-3 py-2 text-right text-gray-800">{entry.cost?.toLocaleString(undefined, { style: 'currency', currency: 'LKR' }) ?? '--'}</td>
                  <td className="px-3 py-2 text-right text-gray-800">
                    {ingredient && entry.quantity === 0 ? (
                      <span className="px-2 py-1 rounded bg-red-100 text-red-700 font-semibold text-xs">Out of Stock</span>
                    ) : (
                      <span className="px-2 py-1 rounded bg-green-100 text-green-700 font-semibold text-xs">{entry.quantity} {entry.unit}</span>
                    )}
                  </td>
                  <td className="px-3 py-2 text-right text-gray-800">
                    {ingredient && entry.currentQty === 0 ? (
                      <span className="px-2 py-1 rounded bg-red-100 text-red-700 font-semibold text-xs">Out of Stock</span>
                    ) : (
                      <span className="px-2 py-1 rounded bg-green-100 text-green-700 font-semibold text-xs">{entry.currentQty} {entry.unit}</span>
                    )}
                  </td>
                  <td className="px-3 py-2 text-gray-700">{entry.note}</td>
                  <td className="px-3 py-2 text-center">
                    {/* Waste Button: Allowed for everyone (including Baker) */}
                    <button
                      className="px-2 py-1 rounded bg-orange-100 text-orange-700 font-semibold text-xs hover:bg-orange-200 transition-colors"
                      style={{ minWidth: 0, fontSize: '0.85rem', padding: '0.25rem 0.5rem' }}
                      title="Mark as Waste"
                      onClick={() => {
                        setSelectedBatch(entry);
                        setWastageModalOpen(true);
                      }}
                    >
                      Waste
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Add New Stock Modal */}
        <AddNewIngredientStockModal
          open={addStockModalOpen}
          onClose={() => setAddStockModalOpen(false)}
          itemName={ingredient.name}
          ingredient={ingredient}
          onAddStock={(entry) => {
            setStockEntries([
              {
                ...entry,
                cost: 0, 
                currentQty: entry.quantity,
              },
              ...stockEntries,
            ]);
          }}
        />
        <AddWastageModal
          isOpen={wastageModalOpen}
          onClose={() => setWastageModalOpen(false)}
          batchData={selectedBatch ? {
            batchID: selectedBatch.batchId,
            ingredientName: ingredient.name,
            currentQty: selectedBatch.currentQty,
            unit: selectedBatch.unit,
            expiryDate: selectedBatch.expireDate,
          } : {
            batchID: '',
            ingredientName: '',
            currentQty: 0,
            unit: '',
            expiryDate: '',
          }}
          onConfirm={({ batchID, quantity, reason, note }) => {
            if (selectedBatch) {
              setStockEntries([
                {
                  ...selectedBatch,
                  quantity: selectedBatch.quantity - quantity,
                  currentQty: selectedBatch.currentQty - quantity,
                  note: `Wastage: ${reason}${note ? ' - ' + note : ''}`,
                },
                ...stockEntries.filter(e => e !== selectedBatch),
              ]);
            }
            setWastageModalOpen(false);
          }}
        />
      </div>
    </div>
  );
};