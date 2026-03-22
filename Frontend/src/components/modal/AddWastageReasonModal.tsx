
import React, { useEffect, useState } from 'react';
import { X, Save } from 'lucide-react';
import { createPortal } from 'react-dom';

// Generate a unique ID for wastage reason
function generateId() {
  return (
    "wastage_" +
    Date.now().toString(36) +
    Math.random().toString(36).substring(2, 8)
  );
}

export const AddWastageReasonModal: React.FC<{
  open: boolean;
  onClose: () => void;
  onSave: (reason: { id: string; name: string; note: string }) => void;
}> = ({ open, onClose, onSave }) => {

  if (!open) return null;

  const [id, setId] = useState('');
  const [name, setName] = useState('');
  const [note, setNote] = useState('');
  const [touched, setTouched] = useState(false);

  const isSaveDisabled = !name.trim();
  const saveButtonStyle = isSaveDisabled
    ? "bg-gray-200 text-gray-400 cursor-not-allowed"
    : "bg-orange-600 text-white hover:bg-orange-700 shadow-md";

  useEffect(() => {
    if (open) {
      setId(generateId());
      setName('');
      setNote('');
      setTouched(false);
    }
  }, [open]);

  const handleSave = () => {
    setTouched(true);
    if (!name.trim()) return;
    onSave({ id, name: name.trim(), note: note.trim() });
  };

  const modalContent = (
    <div
      className="fixed inset-0 z-[110] bg-black/40 backdrop-blur-sm flex items-center justify-center p-4"
      aria-modal="true"
      role="dialog"
    >
      <div className="bg-white w-full max-w-md rounded-2xl shadow-2xl flex flex-col relative overflow-hidden border border-orange-100 animate-fade-in">
        
        {/* Header - Changed to Orange Theme */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-orange-100 bg-orange-50/60">
          <h3 className="text-lg font-bold text-orange-800">Add Wastage Reason</h3>
          <button onClick={onClose} className="p-2 rounded-lg hover:bg-orange-100 transition-colors" aria-label="Close">
            <X className="w-5 h-5 text-gray-400" />
          </button>
        </div>

        {/* Body */}
        <div className="flex-1 p-6 flex flex-col gap-4">
          {/* Wastage Reason ID (read-only) */}
          <div>
            <label className="block text-sm font-medium mb-1 text-gray-700" htmlFor="wastage-id">
              Wastage Reason ID
            </label>
            <input
              id="wastage-id"
              type="text"
              className="w-full border border-gray-200 rounded-lg px-3 py-2 bg-gray-100 text-gray-500 cursor-not-allowed"
              value={id}
              readOnly
              disabled
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1 text-gray-700" htmlFor="reason-name">
              Reason Name <span className="text-red-500">*</span>
            </label>
            <input
              id="reason-name"
              type="text"
              // Changed focus ring to Orange
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all"
              placeholder="e.g. Expired"
              value={name}
              onChange={(e) => setName(e.target.value)}
              autoFocus
            />
            {!name.trim() && touched && (
              <p className="text-red-500 text-xs mt-1">Reason name is required.</p>
            )}
          </div>
          <div>
            <label className="block text-sm font-medium mb-1 text-gray-700" htmlFor="reason-note">
              Note <span className="text-gray-400">(optional)</span>
            </label>
            <textarea
              id="reason-note"
              // Changed focus ring to Orange
              className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all"
              placeholder="Add any details..."
              value={note}
              onChange={(e) => setNote(e.target.value)}
              rows={2}
            />
          </div>
        </div>

        {/* Footer */}
        <div className="p-4 bg-gray-50 border-t border-orange-100 flex items-center justify-end gap-2">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2 text-gray-700 bg-white border border-gray-200 hover:bg-gray-50 rounded-lg font-medium transition-colors"
          >
            Cancel
          </button>
          
          {/* Save Button with Orange Style */}
          <button
            type="button"
            onClick={handleSave}
            disabled={isSaveDisabled}
            className={`px-4 py-2 rounded-lg font-medium flex items-center gap-2 transition-all ${saveButtonStyle}`}
          >
            <Save className="w-4 h-4" /> Save Reason
          </button>
        </div>
      </div>
    </div>
  );

  return createPortal(modalContent, document.body);
};