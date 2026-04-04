
import React, { useEffect, useState } from 'react';
import { X, Save, AlertCircle, Loader2 } from 'lucide-react';
import { createPortal } from 'react-dom';
import apiClient from '../../services/api';

export const AddWastageReasonModal: React.FC<{
  open: boolean;
  onClose: () => void;
  onSuccess: (reason: { id: string; name: string; note: string }) => void;
}> = ({ open, onClose, onSuccess }) => {
  const [name, setName] = useState('');
  const [note, setNote] = useState('');
  const [touched, setTouched] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Reset form when modal opens/closes
  useEffect(() => {
    if (open) {
      setName('');
      setNote('');
      setTouched(false);
      setError(null);
    }
  }, [open]);

  if (!open) return null;

  const isSaveDisabled = !name.trim() || isLoading;
  const saveButtonStyle = isSaveDisabled
    ? "bg-gray-200 text-gray-400 cursor-not-allowed"
    : "bg-orange-600 text-white hover:bg-orange-700 shadow-md";

  const handleSave = async () => {
    setTouched(true);
    setError(null);

    if (!name.trim()) {
      return;
    }

    setIsLoading(true);

    try {
      // Send POST request to backend
      const response = await apiClient.wastageReason.create({
        reason: name.trim(),
        description: note.trim(),
      });

      // Map backend response to frontend interface
      const newReason = {
        id: response.id?.toString() || '',
        name: response.reason || response.name || '',
        note: response.description || response.note || '',
      };

      // Call parent callback with new reason
      onSuccess(newReason);

      // Clear form
      setName('');
      setNote('');
      setTouched(false);

      // Close modal
      onClose();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to add wastage reason. Please try again.';
      setError(errorMessage);
      console.error('Error adding wastage reason:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const modalContent = (
    <>
      <div
        className="fixed inset-0 z-[110] bg-black/40 backdrop-blur-sm flex items-center justify-center p-4"
        aria-modal="true"
        role="dialog"
      >
        <div className="bg-white w-full max-w-md rounded-2xl shadow-2xl flex flex-col relative overflow-hidden border border-orange-100 animate-fade-in">
          {/* Header */}
          <div className="flex items-center justify-between px-6 py-4 border-b border-orange-100 bg-orange-50/60">
            <h3 className="text-lg font-bold text-orange-800">Add Wastage Reason</h3>
            <button
              onClick={onClose}
              disabled={isLoading}
              className="p-2 rounded-lg hover:bg-orange-100 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              aria-label="Close"
            >
              <X className="w-5 h-5 text-gray-400" />
            </button>
          </div>

          {/* Body */}
          <div className="flex-1 p-6 flex flex-col gap-4 max-h-[calc(100vh-300px)] overflow-y-auto">
            {/* Error Message */}
            {error && (
              <div className="p-3 bg-red-50 border border-red-200 rounded-lg flex items-start gap-2">
                <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                <p className="text-sm text-red-700">{error}</p>
              </div>
            )}

            {/* Reason Name */}
            <div>
              <label className="block text-sm font-medium mb-1 text-gray-700" htmlFor="reason-name">
                Reason Name <span className="text-red-500">*</span>
              </label>
              <input
                id="reason-name"
                type="text"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all disabled:bg-gray-100 disabled:cursor-not-allowed"
                placeholder="e.g. Expired"
                value={name}
                onChange={(e) => setName(e.target.value)}
                disabled={isLoading}
                autoFocus
              />
              {!name.trim() && touched && (
                <p className="text-red-500 text-xs mt-1">Reason name is required.</p>
              )}
            </div>

            {/* Note */}
            <div>
              <label className="block text-sm font-medium mb-1 text-gray-700" htmlFor="reason-note">
                Note <span className="text-gray-400">(optional)</span>
              </label>
              <textarea
                id="reason-note"
                className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent transition-all disabled:bg-gray-100 disabled:cursor-not-allowed"
                placeholder="Add any details..."
                value={note}
                onChange={(e) => setNote(e.target.value)}
                disabled={isLoading}
                rows={2}
              />
            </div>
          </div>

          {/* Footer */}
          <div className="p-4 bg-gray-50 border-t border-orange-100 flex items-center justify-end gap-2">
            <button
              type="button"
              onClick={onClose}
              disabled={isLoading}
              className="px-4 py-2 text-gray-700 bg-white border border-gray-200 hover:bg-gray-50 rounded-lg font-medium transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Cancel
            </button>

            {/* Save Button */}
            <button
              type="button"
              onClick={handleSave}
              disabled={isSaveDisabled}
              className={`px-4 py-2 rounded-lg font-medium flex items-center gap-2 transition-all ${saveButtonStyle}`}
            >
              {isLoading ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="w-4 h-4" />
                  Save Reason
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </>
  );

  return createPortal(modalContent, document.body);
};