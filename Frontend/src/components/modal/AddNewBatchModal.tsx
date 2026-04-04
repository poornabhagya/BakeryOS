import React, { useState } from 'react';
import { Save, AlertCircle, CheckCircle } from 'lucide-react';
import apiClient from '../../services/api';

interface AddNewBatchModalProps {
  open: boolean;
  onClose: () => void;
  itemName?: string;
  productId?: number;
  onAddBatch?: (batch: any) => void;
}

export const AddNewBatchModal: React.FC<AddNewBatchModalProps> = ({ open, onClose, itemName, productId, onAddBatch }) => {
  const [newBatch, setNewBatch] = useState({
    madeDate: '',
    expireDate: '',
    quantity: 0,
    notes: '',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState(false);

  const handleSaveBatch = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setSuccess(false);

    if (!productId) {
      setError('Product ID is required');
      return;
    }

    if (!newBatch.madeDate || !newBatch.expireDate || newBatch.quantity <= 0) {
      setError('Please fill in all required fields');
      return;
    }

    setLoading(true);

    try {
      const payload = {
        product_id: productId,
        quantity: String(newBatch.quantity),
        made_date: newBatch.madeDate.split('T')[0],
        expire_date: newBatch.expireDate.split('T')[0],
        notes: newBatch.notes || '',
      };

      const response = await apiClient.batches.createProductBatch(payload);
      setSuccess(true);

      if (onAddBatch) {
        onAddBatch(response);
      }

      setNewBatch({
        madeDate: '',
        expireDate: '',
        quantity: 0,
        notes: '',
      });

      setTimeout(() => {
        onClose();
      }, 1500);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to create batch';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-[101] bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white w-full max-w-lg max-h-[90vh] rounded-xl shadow-2xl flex flex-col relative overflow-hidden">
        <div className="sticky top-0 z-10 bg-white border-b border-gray-200 flex items-center justify-between px-6 py-4">
          <h3 className="text-lg font-bold text-gray-900 tracking-tight">Add New Batch</h3>
          <button onClick={onClose} className="p-2 rounded-lg hover:bg-orange-50 transition-colors" aria-label="Close" disabled={loading}>
            <span className="text-gray-400">×</span>
          </button>
        </div>
        <form className="max-w-2xl mx-auto p-6 flex flex-col gap-4" onSubmit={handleSaveBatch}>
          {error && (
            <div className="flex items-start gap-3 p-4 bg-red-50 border border-red-200 rounded-lg">
              <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          {success && (
            <div className="flex items-start gap-3 p-4 bg-green-50 border border-green-200 rounded-lg">
              <CheckCircle className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
              <p className="text-sm text-green-700">Batch created successfully!</p>
            </div>
          )}

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-xs font-bold uppercase text-gray-500 mb-1">Item Name</label>
              <input value={itemName || ''} readOnly className="w-full px-3 py-2 border border-gray-200 rounded-lg bg-gray-100 text-orange-600 font-semibold cursor-not-allowed text-sm" />
            </div>
            <div>
              <label className="block text-xs font-bold uppercase text-gray-500 mb-1">Bulk Quantity</label>
              <input type="number" min="0" step="0.01" value={newBatch.quantity} onChange={e => setNewBatch({ ...newBatch, quantity: Number(e.target.value) })} placeholder="e.g. 100" className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-orange-100 focus:border-orange-500 text-lg font-bold" required disabled={loading} />
            </div>
            <div>
              <label className="block text-xs font-bold uppercase text-gray-500 mb-1">Made Date</label>
              <input type="datetime-local" value={newBatch.madeDate} onChange={e => setNewBatch({ ...newBatch, madeDate: e.target.value })} className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-orange-100 focus:border-orange-500" required disabled={loading} />
            </div>
            <div>
              <label className="block text-xs font-bold uppercase text-orange-600 mb-1">Expire Date</label>
              <input type="datetime-local" value={newBatch.expireDate} onChange={e => setNewBatch({ ...newBatch, expireDate: e.target.value })} className="w-full px-3 py-2 border border-orange-200 rounded-lg focus:ring-2 focus:ring-orange-100 focus:border-orange-500 font-semibold text-orange-600" required disabled={loading} />
            </div>
            <div className="col-span-2">
              <label className="block text-xs font-bold uppercase text-gray-500 mb-1">Description / Notes</label>
              <textarea value={newBatch.notes} onChange={e => setNewBatch({ ...newBatch, notes: e.target.value })} placeholder="e.g. Fresh morning batch" className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-orange-100 focus:border-orange-500 min-h-[60px] resize-none" disabled={loading} />
            </div>
          </div>

          <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
            <button type="button" onClick={onClose} disabled={loading} className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed">Cancel</button>
            <button type="submit" disabled={loading} className="px-4 py-2 bg-orange-500 hover:bg-orange-600 disabled:bg-orange-300 text-white rounded-lg font-medium flex items-center gap-2 transition-colors disabled:cursor-not-allowed">
              {loading ? (
                <>
                  <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="w-4 h-4" /> Save Batch
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
