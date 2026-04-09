import React, { useState, useEffect } from 'react';
import { X, Search, Plus, LoaderCircle } from 'lucide-react';
import { AddNewIngredientStockModal } from './AddNewIngredientStockModal';
import { AddWastageModal } from '../../modal/AddWastageModal'; // Check Path
import { useAuth } from '../../../context/AuthContext'; // 1. Auth Import
import apiClient from '../../../services/api'; // API Client
import { formatQuantityForDisplay } from '../../../utils/conversions';

interface StockHistoryEntry {
  id?: number;
  batchId: string;
  stockDate: string;
  expireDate: string;
  cost: number;
  quantity: number; 
  currentQty: number; 
  unit: string;
  status?: string;
  createdAt?: string;
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
  onStockUpdated?: () => void | Promise<void>;
}

const dummyHistory: StockHistoryEntry[] = [
  { batchId: 'BID-001', stockDate: '2026-01-27', expireDate: '2026-02-10', cost: 1200, quantity: 20, currentQty: 20, unit: 'kg', note: 'Restocked from supplier' },
  { batchId: 'BID-002', stockDate: '2026-01-27', expireDate: '2026-02-05', cost: 300, quantity: 5, currentQty: 5, unit: 'kg', note: 'Used in production' },
  { batchId: 'BID-003', stockDate: '2026-01-27', expireDate: '2026-02-01', cost: 150, quantity: -2, currentQty: -2, unit: 'kg', note: 'Inventory correction' },
];

export const IngredientStockHistoryModal: React.FC<IngredientStockHistoryModalProps> = ({ isOpen, onClose, ingredient, history, onStockUpdated }) => {
  const { user } = useAuth(); // 2. Get User
  // 3. Define Permissions: Only Manager & Storekeeper can ADD Stock
  const canAddStock = user?.role === 'Manager' || user?.role === 'Storekeeper';

  const [searchTerm, setSearchTerm] = useState('');
  const [addStockModalOpen, setAddStockModalOpen] = useState(false);
  const [stockEntries, setStockEntries] = useState<StockHistoryEntry[]>(history || []);
  const [wastageModalOpen, setWastageModalOpen] = useState(false);
  const [selectedBatch, setSelectedBatch] = useState<StockHistoryEntry | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchBatches = async () => {
    if (!ingredient || !isOpen) return;

    const ingredientIdStr = String(ingredient.id).replace('#I', '');
    const ingredientApiId = parseInt(ingredientIdStr, 10);

    try {
      setIsLoading(true);
      setError(null);

      console.log('[IngredientStockHistoryModal] Fetching batches for ingredient ID:', ingredientApiId);
      const response = await apiClient.batches.getIngredientBatchesById(ingredientApiId);
      console.log('[IngredientStockHistoryModal] API Response:', response);

      const batchesArray = Array.isArray(response)
        ? response
        : ((response as any)?.results || (response as any)?.data || []);

      const mappedBatches: StockHistoryEntry[] = (batchesArray || []).map((batch: any) => {
        const qty = parseFloat(batch.quantity) || 0;
        const curQty = batch.current_qty !== undefined ? parseFloat(batch.current_qty) : qty;

        return {
          id: batch.id,
          batchId: String(batch.batch_id || `BATCH-${Date.now()}`),
          stockDate: String(batch.made_date || new Date().toISOString().split('T')[0]),
          expireDate: String(batch.expire_date || new Date().toISOString().split('T')[0]),
          cost: parseFloat(batch.cost_price || 0),
          quantity: qty,
          currentQty: !isNaN(curQty) ? curQty : qty,
          unit: batch.unit || 'units',
          note: String(batch.notes || 'No notes'),
          status: String(batch.status || 'Active'),
          createdAt: batch.created_at ? String(batch.created_at) : undefined,
        };
      });

      const sortedBatches = mappedBatches.sort((a, b) => {
        if (typeof a.id === 'number' && typeof b.id === 'number') {
          return b.id - a.id;
        }
        const aTime = new Date(a.createdAt || a.stockDate).getTime();
        const bTime = new Date(b.createdAt || b.stockDate).getTime();
        return bTime - aTime;
      });

      setStockEntries(sortedBatches);
    } catch (err) {
      console.error('[IngredientStockHistoryModal] Error fetching batches:', err);
      setError('Failed to load ingredient history');
      setStockEntries(history || dummyHistory);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchBatches();
  }, [isOpen, ingredient]);

  const normalizedSearch = searchTerm.trim().toLowerCase();
  const filteredBatches = stockEntries.filter((batch: StockHistoryEntry) => {
    if (!normalizedSearch) return true;

    return (
      (batch.batchId ?? '').toLowerCase().includes(normalizedSearch) ||
      (batch.status ?? '').toLowerCase().includes(normalizedSearch) ||
      (batch.note ?? '').toLowerCase().includes(normalizedSearch) ||
      (batch.stockDate ?? '').toLowerCase().includes(normalizedSearch) ||
      (batch.expireDate ?? '').toLowerCase().includes(normalizedSearch) ||
      (batch.createdAt ?? '').toLowerCase().includes(normalizedSearch)
    );
  });

  const handleAddStock = async () => {
    await fetchBatches();
    if (onStockUpdated) {
      await onStockUpdated();
    }
    setAddStockModalOpen(false);
  };

  const parseIngredientApiId = (rawId: string): number | null => {
    const numericId = parseInt(String(rawId).replace('#I', ''), 10);
    return Number.isFinite(numericId) ? numericId : null;
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
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
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
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-12">
              <LoaderCircle className="w-8 h-8 text-orange-500 animate-spin mb-4" />
              <p className="text-gray-500 font-medium">Loading batch history...</p>
            </div>
          ) : error ? (
            <div className="flex flex-col items-center justify-center py-12">
              <p className="text-red-500 font-medium">{error}</p>
              <button 
                onClick={() => setStockEntries(history || dummyHistory)} 
                className="mt-4 text-orange-600 hover:underline"
              >
                Reload Mock Data
              </button>
            </div>
          ) : filteredBatches.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <div className="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mb-4">
                <Search className="w-8 h-8 text-orange-400" />
              </div>
              <h3 className="text-lg font-bold text-gray-800 mb-1">No Batches Found</h3>
              <p className="text-gray-500">There are no stock entries matching your current search.</p>
            </div>
          ) : (
            <table className="w-full text-sm rounded-xl overflow-hidden">
              <thead>
                <tr className="bg-orange-50/80">
                  <th className="px-3 py-2 text-left font-bold uppercase text-orange-700 tracking-wide">Batch ID</th>
                  <th className="px-3 py-2 text-left font-bold uppercase text-orange-700 tracking-wide">Stock Date</th>
                  <th className="px-3 py-2 text-left font-bold uppercase text-orange-700 tracking-wide">Expire Date</th>
                  <th className="px-3 py-2 text-right font-bold uppercase text-orange-700 tracking-wide">Cost</th>
                  <th className="px-3 py-2 text-right font-bold uppercase text-orange-700 tracking-wide">Quantity</th>
                  <th className="px-3 py-2 text-right font-bold uppercase text-orange-700 tracking-wide">Current Qty</th>
                  <th className="px-3 py-2 text-center font-bold uppercase text-orange-700 tracking-wide">Status</th>
                  <th className="px-3 py-2 text-left font-bold uppercase text-orange-700 tracking-wide">Note</th>
                  <th className="px-3 py-2 text-center font-bold uppercase text-orange-700 tracking-wide">Action</th>
                </tr>
              </thead>
              <tbody>
                {filteredBatches.map((entry, idx) => (
                  <tr key={idx} className="border-b last:border-b-0 bg-white hover:bg-orange-50/80 transition-colors duration-100">
                    <td className="px-3 py-2 text-gray-700">{entry.batchId}</td>
                    <td className="px-3 py-2 text-gray-700">{entry.stockDate}</td>
                    <td className="px-3 py-2 text-gray-700">{entry.expireDate}</td>
                    <td className="px-3 py-2 text-right text-gray-800">LKR {Number(entry.cost).toFixed(2)}</td>
                    <td className="px-3 py-2 text-right text-gray-800">
                      {ingredient && entry.quantity === 0 ? (
                        <span className="px-2 py-1 rounded bg-red-100 text-red-700 font-semibold text-xs">Out of Stock</span>
                      ) : (
                        <span className="px-2 py-1 rounded bg-green-100 text-green-700 font-semibold text-xs">
                          {formatQuantityForDisplay(entry.quantity, ingredient?.trackingType || 'Weight')}
                        </span>
                      )}
                    </td>
                    <td className="px-3 py-2 text-right text-gray-800">
                      {ingredient && entry.currentQty === 0 ? (
                        <span className="px-2 py-1 rounded bg-red-100 text-red-700 font-semibold text-xs">Out of Stock</span>
                      ) : (
                        <span className="px-2 py-1 rounded bg-green-100 text-green-700 font-semibold text-xs">
                          {formatQuantityForDisplay(entry.currentQty, ingredient?.trackingType || 'Weight')}
                        </span>
                      )}
                    </td>
                    <td className="px-3 py-2 text-center text-gray-800">
                      <span className={`px-2 py-1 rounded font-semibold text-xs ${
                        entry.status === 'Expired' 
                          ? 'bg-red-100 text-red-700' 
                          : entry.status === 'Active' 
                            ? 'bg-green-100 text-green-700' 
                            : 'bg-gray-100 text-gray-700'
                      }`}>
                        {entry.status || 'Active'}
                      </span>
                    </td>
                    <td className="px-3 py-2 text-gray-700">{entry.note}</td>
                    <td className="px-3 py-2 text-center">
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
          )}
        </div>

        {/* Add New Stock Modal */}
        <AddNewIngredientStockModal
          open={addStockModalOpen}
          onClose={() => setAddStockModalOpen(false)}
          itemName={ingredient.name}
          ingredient={ingredient}
          onAddStock={handleAddStock}
        />
        <AddWastageModal
          isOpen={wastageModalOpen}
          onClose={() => setWastageModalOpen(false)}
          batchData={selectedBatch ? {
            batchID: selectedBatch.batchId,
            ingredientName: ingredient.name,
            currentQty: selectedBatch.currentQty,
            unit: selectedBatch.unit,
            trackingType: ingredient.trackingType,
            expiryDate: selectedBatch.expireDate,
          } : {
            batchID: '',
            ingredientName: '',
            currentQty: 0,
            unit: '',
            trackingType: ingredient.trackingType,
            expiryDate: '',
          }}
          onConfirm={async ({ quantity, reason, note }) => {
            if (!ingredient || !selectedBatch) {
              alert('Unable to save wastage: missing ingredient or batch selection.');
              throw new Error('Missing ingredient or batch context');
            }

            const ingredientApiId = parseIngredientApiId(ingredient.id);
            if (!ingredientApiId) {
              alert('Unable to save wastage: invalid ingredient id.');
              throw new Error('Invalid ingredient id');
            }

            if (typeof selectedBatch.id !== 'number') {
              alert('Unable to save wastage: invalid batch id.');
              throw new Error('Invalid batch id');
            }

            try {
              const allReasons = await apiClient.wastageReason.getAll();
              const matchedReason = (allReasons || []).find(
                (r: any) => String(r.reason || '').toLowerCase() === String(reason || '').toLowerCase()
              );

              if (!matchedReason?.id) {
                alert(`Unable to save wastage: reason "${reason}" was not found.`);
                throw new Error('Wastage reason not found');
              }

              const payload = {
                ingredient_id: ingredientApiId,
                batch_id: selectedBatch.id,
                quantity,
                reason_id: matchedReason.id,
                unit_cost: selectedBatch.cost ?? 0,
                notes: note || '',
              };

              await apiClient.ingredientWastages.create(payload);

              await fetchBatches();
              if (onStockUpdated) {
                await onStockUpdated();
              }
              setWastageModalOpen(false);
              setSelectedBatch(null);
            } catch (err: any) {
              console.error('[IngredientStockHistoryModal] Failed to create ingredient wastage:', err);
              const message = err?.message || 'Failed to save wastage record.';
              alert(message);
              throw err;
            }
          }}
        />
      </div>
    </div>
  );
};