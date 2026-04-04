import React, { useState } from 'react';
import { X, Save, Info, AlertCircle, CheckCircle } from 'lucide-react';
import apiClient from '../../../services/api';


interface Ingredient {
  id: string | number;
  name: string;
  trackingType: string;
}

interface AddNewIngredientStockModalProps {
  open: boolean;
  onClose: () => void;
  itemName: string;
  ingredient: Ingredient | null;
  onAddStock?: (entry: any) => void;
}


const UNIT_OPTIONS: Record<string, string[]> = {
  weight: ['kg', 'g'],
  volume: ['L', 'ml'],
  count: ['Nos', 'Tray'],
};

export const AddNewIngredientStockModal: React.FC<AddNewIngredientStockModalProps> = ({
  open,
  onClose,
  itemName,
  ingredient,
  onAddStock,
}) => {
  // Default to 'weight' if missing
  const trackingType = ingredient?.trackingType?.toLowerCase() || 'weight';
  const unitOptions = UNIT_OPTIONS[trackingType] || ['kg'];

  // Generate batchID when modal opens
  const [batchID, setBatchID] = useState<string>('');
  React.useEffect(() => {
    if (open) {
      // Example: BATCH-YYYYMMDD-HHMMSS-<random>
      const now = new Date();
      const pad = (n: number) => n.toString().padStart(2, '0');
      const dateStr = `${now.getFullYear()}${pad(now.getMonth() + 1)}${pad(now.getDate())}`;
      const timeStr = `${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}`;
      const rand = Math.floor(Math.random() * 1000).toString().padStart(3, '0');
      setBatchID(`BATCH-${dateStr}-${timeStr}-${rand}`);
    }
  }, [open]);

  const [quantity, setQuantity] = useState<number>(0);
  const [unit, setUnit] = useState(unitOptions[0]);
  const [cost, setCost] = useState<string>('');
  const [expireDate, setExpireDate] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);
  
  // Stock date (today)
  const todayStr = React.useMemo(() => {
    const now = new Date();
    const yyyy = now.getFullYear();
    const mm = String(now.getMonth() + 1).padStart(2, '0');
    const dd = String(now.getDate()).padStart(2, '0');
    return `${yyyy}-${mm}-${dd}`;
  }, []);
  const [note, setNote] = useState('');

  // Unit conversion utilities
  const convertToBaseUnit = (qty: number, selectedUnit: string, trackingType: string): number => {
    // Convert to base unit (grams for weight, ml for volume, nos for count)
    if (trackingType === 'weight') {
      return selectedUnit === 'kg' ? qty * 1000 : qty;
    }
    if (trackingType === 'volume') {
      return selectedUnit === 'L' ? qty * 1000 : qty;
    }
    return qty;
  };

  // Update unit if trackingType changes
  React.useEffect(() => {
    setUnit(unitOptions[0]);
  }, [trackingType]);

  const handleSave = async () => {
    setError(null);
    setSuccess(false);

    if (!ingredient) {
      setError('Ingredient is required');
      return;
    }

    if (!quantity || quantity <= 0) {
      setError('Quantity must be greater than 0');
      return;
    }

    if (!expireDate) {
      setError('Expire date is required');
      return;
    }

    if (!cost) {
      setError('Cost is required');
      return;
    }

    setLoading(true);

    try {
      const baseQuantity = convertToBaseUnit(quantity, unit, trackingType);

      const parsedIngredientId = typeof ingredient.id === 'number'
        ? ingredient.id
        : Number(String(ingredient.id).replace(/\D/g, ''));

      if (!parsedIngredientId || Number.isNaN(parsedIngredientId)) {
        setError('Invalid ingredient ID');
        return;
      }

      const payload = {
        ingredient_id: parsedIngredientId,
        quantity: String(baseQuantity),
        cost_price: cost,
        made_date: todayStr,
        expire_date: expireDate,
        notes: note || '',
      };

      const response = await apiClient.batches.createIngredientBatch(payload);
      setSuccess(true);

      if (onAddStock) {
        onAddStock(response);
      }

      setQuantity(0);
      setCost('');
      setExpireDate('');
      setNote('');

      setTimeout(() => {
        onClose();
      }, 1500);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to create stock batch';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-[110] bg-black/40 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white w-full max-w-md rounded-2xl shadow-2xl flex flex-col relative overflow-hidden border border-orange-100 animate-fade-in">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-orange-100 bg-orange-50/60">
          <h3 className="text-lg font-bold text-orange-700">Add New Stock - {itemName}</h3>
          <button onClick={onClose} className="p-2 rounded-lg hover:bg-orange-100 transition-colors" aria-label="Close" disabled={loading}>
            <X className="w-5 h-5 text-gray-400" />
          </button>
        </div>
        {/* Form */}
        <form className="flex-1 p-6 flex flex-col gap-4" onSubmit={e => { e.preventDefault(); handleSave(); }}>
          {error && (
            <div className="flex items-start gap-3 p-3 bg-red-50 border border-red-200 rounded-lg">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          {success && (
            <div className="flex items-start gap-3 p-3 bg-green-50 border border-green-200 rounded-lg">
              <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-green-700">Stock batch created successfully!</p>
            </div>
          )}
          {/* Batch ID (read-only) */}
          <div>
            <label className="block text-xs font-semibold text-gray-500 mb-1">Batch ID</label>
            <input
              type="text"
              value={batchID}
              readOnly
              disabled
              className="w-full px-3 py-2 border border-gray-300 rounded bg-gray-100 text-gray-700 font-mono cursor-not-allowed"
            />
          </div>
          {/* Ingredient Name (read-only) */}
          <div>
            <label className="block text-xs font-semibold text-gray-500 mb-1">Ingredient Name</label>
            <input
              type="text"
              value={ingredient?.name || ''}
              readOnly
              disabled
              className="w-full px-3 py-2 border border-gray-300 rounded bg-gray-100 text-gray-700 cursor-not-allowed"
            />
          </div>
          {/* Stock Date (read-only) */}
          <div>
            <label className="block text-xs font-semibold text-gray-500 mb-1">Stock Date</label>
            <input
              type="date"
              value={todayStr}
              readOnly
              disabled
              className="w-full px-3 py-2 border border-gray-300 rounded bg-gray-100 text-gray-700 cursor-not-allowed"
            />
          </div>
          {/* Cost input */}
          <div>
            <label className="block text-xs font-semibold text-gray-500 mb-1">Cost</label>
            <input
              type="number"
              min="0"
              step="0.01"
              value={cost}
              onChange={e => setCost(e.target.value)}
              placeholder="Enter cost for this batch"
              className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-orange-100 focus:border-orange-500"
              required
              disabled={loading}
            />
          </div>
          {/* Expire Date input */}
          <div>
            <label className="block text-xs font-semibold text-gray-500 mb-1">Expire Date</label>
            <input
              type="date"
              value={expireDate}
              onChange={e => setExpireDate(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-orange-100 focus:border-orange-500"
              required
              disabled={loading}
            />
          </div>
          {/* Action dropdown removed: action is always 'Added' */}
          <div>
            <label className="block text-xs font-bold uppercase text-gray-500 mb-1">Quantity</label>
            <input type="number" value={quantity} onChange={e => setQuantity(Number(e.target.value))} className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" min={0} step="0.01" required disabled={loading} />
          </div>
          <div>
            <label className="block text-xs font-bold uppercase text-gray-500 mb-1">Unit</label>
            <select value={unit} onChange={e => setUnit(e.target.value)} className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" disabled={loading}>
              {unitOptions.map(opt => (
                <option key={opt} value={opt}>{opt}</option>
              ))}
            </select>
            {/* Dynamic User Instruction Info Box */}
            <div className="flex items-start gap-2 p-3 mt-2 bg-blue-50 border border-blue-100 rounded-lg">
              <Info className="w-4 h-4 text-blue-500 mt-0.5" />
              <span className="text-sm text-blue-700">
                {trackingType === 'weight' && (
                  <>ℹ️ Selected unit will be automatically converted to <b>Grams (g)</b> for inventory tracking.</>
                )}
                {trackingType === 'volume' && (
                  <>ℹ️ Selected unit will be automatically converted to <b>Milliliters (ml)</b> for inventory tracking.</>
                )}
                {trackingType === 'count' && (
                  <>ℹ️ Stock will be tracked by <b>Count (Nos)</b>. (e.g., 1 Tray = 30 Nos).</>
                )}
              </span>
            </div>
          </div>
          <div>
            <label className="block text-xs font-bold uppercase text-gray-500 mb-1">Note</label>
            <textarea value={note} onChange={e => setNote(e.target.value)} className="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm" rows={2} placeholder="Optional note..." disabled={loading} />
          </div>
          <div className="flex items-center gap-2 bg-blue-50 border border-blue-200 rounded-lg p-3 mt-2">
            <Info className="w-4 h-4 text-blue-500" />
            <span className="text-sm text-blue-800">
              {trackingType === 'weight' && 'System tracks stock in Grams (g) or Kilograms (kg).'}
              {trackingType === 'volume' && 'System tracks stock in Milliliters (ml) or Liters (L).'}
              {trackingType === 'count' && 'System tracks stock by Count (Nos).'}
            </span>
          </div>
          <div className="flex justify-end gap-2 mt-4">
            <button
              type="button"
              onClick={onClose}
              disabled={loading}
              className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-orange-500 hover:bg-orange-600 disabled:bg-orange-300 text-white rounded-lg font-medium flex items-center gap-2 transition-colors disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="w-4 h-4" /> Save
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
