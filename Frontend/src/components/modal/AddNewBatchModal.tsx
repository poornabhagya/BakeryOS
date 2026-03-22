import React, { useState } from 'react';
import { Save } from 'lucide-react';

interface AddNewBatchModalProps {
  open: boolean;
  onClose: () => void;
  itemName?: string;
  onAddBatch: (batch: {
    batchId: string;
    madeDate: string;
    expireDate: string;
    quantity: number;
    notes: string;
  }) => void;
}

function generateBatchId() {
  return `#BATCH-${Math.floor(1000 + Math.random() * 9000)}`;
}

export const AddNewBatchModal: React.FC<AddNewBatchModalProps> = ({ open, onClose, itemName, onAddBatch }) => {
  const [newBatch, setNewBatch] = useState({
    batchId: generateBatchId(),
    madeDate: '',
    expireDate: '',
    quantity: 0,
    notes: '',
  });

  const handleSaveBatch = (e: React.FormEvent) => {
    e.preventDefault();
    onAddBatch({ ...newBatch });
    setNewBatch({
      batchId: generateBatchId(),
      madeDate: '',
      expireDate: '',
      quantity: 0,
      notes: '',
    });
    onClose();
  };

  if (!open) return null;

  return (
    <div className="fixed inset-0 z-[101] bg-black/50 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white w-full max-w-lg max-h-[90vh] rounded-xl shadow-2xl flex flex-col relative overflow-hidden">
        <div className="sticky top-0 z-10 bg-white border-b border-gray-200 flex items-center justify-between px-6 py-4">
          <h3 className="text-lg font-bold text-gray-900 tracking-tight">Add New Batch</h3>
          <button onClick={onClose} className="p-2 rounded-lg hover:bg-orange-50 transition-colors" aria-label="Close">
            <span className="text-gray-400">×</span>
          </button>
        </div>
        <form className="max-w-2xl mx-auto p-6" onSubmit={handleSaveBatch}>
          <div className="grid grid-cols-2 gap-6 mb-6">
            <div>
              <label className="block text-xs font-bold uppercase text-gray-500 mb-1">Batch ID</label>
              <input value={newBatch.batchId} readOnly className="w-full px-3 py-2 border border-gray-200 rounded-lg bg-gray-100 text-gray-400 cursor-not-allowed text-sm" />
            </div>
            <div>
              <label className="block text-xs font-bold uppercase text-gray-500 mb-1">Item Name</label>
              <input value={itemName} readOnly className="w-full px-3 py-2 border border-gray-200 rounded-lg bg-gray-100 text-orange-600 font-semibold cursor-not-allowed text-sm" />
            </div>
            <div>
              <label className="block text-xs font-bold uppercase text-gray-500 mb-1">Bulk Quantity</label>
              <input type="number" min="0" value={newBatch.quantity} onChange={e => setNewBatch({ ...newBatch, quantity: Number(e.target.value) })} placeholder="e.g. 100" className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-orange-100 focus:border-orange-500 text-lg font-bold" />
            </div>
            <div>
              <label className="block text-xs font-bold uppercase text-gray-500 mb-1">Made Date</label>
              <input type="datetime-local" value={newBatch.madeDate} onChange={e => setNewBatch({ ...newBatch, madeDate: e.target.value })} className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-orange-100 focus:border-orange-500" />
            </div>
            <div>
              <label className="block text-xs font-bold uppercase text-orange-600 mb-1">Expire Date</label>
              <input type="datetime-local" value={newBatch.expireDate} onChange={e => setNewBatch({ ...newBatch, expireDate: e.target.value })} className="w-full px-3 py-2 border border-orange-200 rounded-lg focus:ring-2 focus:ring-orange-100 focus:border-orange-500 font-semibold text-orange-600" />
            </div>
            <div>
              <label className="block text-xs font-bold uppercase text-gray-500 mb-1">Description / Notes</label>
              <textarea value={newBatch.notes} onChange={e => setNewBatch({ ...newBatch, notes: e.target.value })} placeholder="e.g. Fresh morning batch" className="w-full px-3 py-2 border border-gray-200 rounded-lg focus:ring-2 focus:ring-orange-100 focus:border-orange-500 min-h-[40px] resize-none" />
            </div>
          </div>
          <div className="flex justify-end gap-3 pt-4 border-t border-gray-200">
            <button type="button" onClick={onClose} className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg font-medium transition-colors">Cancel</button>
            <button type="submit" className="px-4 py-2 bg-orange-500 hover:bg-orange-600 text-white rounded-lg font-medium flex items-center gap-2 transition-colors">
              <Save className="w-4 h-4" /> Save Batch
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
