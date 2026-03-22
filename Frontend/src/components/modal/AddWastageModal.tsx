

import React, { useState } from "react";
import { AlertTriangle, X } from 'lucide-react';


interface AddWastageModalProps {
  isOpen: boolean;
  onClose: () => void;
  batchData: {
    batchID: string;
    ingredientName: string;
    currentQty: number;
    unit: string;
    expiryDate: string;
  };
  onConfirm: (wastage: {
    batchID: string;
    quantity: number;
    reason: string;
    note?: string;
  }) => void;
}

const REASONS = [
  "Expired",
  "Damaged / Broken",
  "Spoiled / Quality Issue",
  "Spillage",
  "Theft / Missing",
  "Other",
];

export const AddWastageModal: React.FC<AddWastageModalProps> = ({
  isOpen,
  onClose,
  batchData,
  onConfirm,
}) => {
  const [quantity, setQuantity] = useState<number | "">("");
  const [reason, setReason] = useState(REASONS[0]);
  const [note, setNote] = useState("");
  const [touched, setTouched] = useState(false);

  const qtyInvalid =
    quantity === "" ||
    quantity <= 0 ||
    (typeof quantity === "number" && quantity > batchData.currentQty);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setTouched(true);
    if (!qtyInvalid && typeof quantity === "number") {
      onConfirm({
        batchID: batchData.batchID,
        quantity,
        reason,
        note: note.trim() ? note : undefined,
      });
      setQuantity("");
      setReason(REASONS[0]);
      setNote("");
      setTouched(false);
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-md">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-3 bg-red-50 border-b border-red-100 rounded-t-xl relative">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-red-600" />
            <h2 className="text-base font-semibold text-red-900">Report Stock Wastage</h2>
          </div>
          <button
            className="absolute right-4 top-3 text-gray-400 hover:text-red-500 transition-colors"
            onClick={onClose}
            aria-label="Close"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
        {/* Info Board */}
        <div className="bg-gray-50 border border-gray-100 rounded-lg p-4 mx-6 mt-4 mb-2 grid grid-cols-1 gap-2">
          <div>
            <div className="text-xs text-gray-500 uppercase">Batch ID</div>
            <div className="font-mono text-gray-700 text-sm">{batchData.batchID}</div>
          </div>
          <div>
            <div className="text-xs text-gray-500">Ingredient</div>
            <div className="font-medium text-gray-900">{batchData.ingredientName}</div>
          </div>
          <div>
            <span className="text-xs text-gray-500">Current Availability</span>
            <span className="ml-2 text-sm font-bold text-green-700 bg-green-50 px-2 py-1 rounded-md inline-block">
              {batchData.currentQty} {batchData.unit}
            </span>
          </div>
        </div>
        {/* Form */}
        <form onSubmit={handleSubmit} className="px-6 pt-2 pb-0 space-y-4">
          {/* Quantity */}
          <div>
            <label className="block font-medium text-gray-700 mb-1">Wastage Quantity</label>
            <div className={
              `flex items-center rounded border ${qtyInvalid && touched ? 'border-red-500' : 'border-gray-300'} bg-white focus-within:ring-2 focus-within:ring-red-500`
            }>
              <input
                type="number"
                min={1}
                max={batchData.currentQty}
                value={quantity}
                onChange={(e) => setQuantity(e.target.value === "" ? "" : Number(e.target.value))}
                onBlur={() => setTouched(true)}
                className="w-24 px-3 py-2 rounded-l outline-none bg-transparent text-gray-900"
                required
              />
              <span className="px-3 py-2 text-gray-400 text-sm select-none bg-gray-50 rounded-r border-l border-gray-200">{batchData.unit}</span>
            </div>
            {touched && typeof quantity === "number" && quantity > batchData.currentQty && (
              <div className="flex items-center gap-1 text-xs text-red-600 mt-1">
                <AlertTriangle className="w-4 h-4" />
                Error: Cannot waste more than available stock
              </div>
            )}
            {touched && (quantity === "" || quantity <= 0) && (
              <div className="flex items-center gap-1 text-xs text-red-600 mt-1">
                <AlertTriangle className="w-4 h-4" />
                Error: Enter a valid quantity
              </div>
            )}
          </div>
          {/* Reason */}
          <div>
            <label className="block font-medium text-gray-700 mb-1">Reason</label>
            <select
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-red-500 focus:border-red-500 text-gray-900 bg-white"
              required
            >
              {REASONS.map((r) => (
                <option key={r} value={r}>{r}</option>
              ))}
            </select>
          </div>
          {/* Note */}
          <div>
            <label className="block font-medium text-gray-700 mb-1">Note <span className="text-xs text-gray-400">(optional)</span></label>
            <textarea
              value={note}
              onChange={(e) => setNote(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-red-500 focus:border-red-500 text-gray-900"
              rows={2}
              placeholder="E.g. Eaten by rats"
            />
          </div>
          {/* Footer */}
          <div className="flex justify-end gap-2 pt-4 border-t border-gray-100 mt-6">
            <button
              type="button"
              className="px-4 py-2 rounded bg-white border border-gray-300 text-gray-700 font-semibold hover:bg-gray-50 transition-colors"
              onClick={onClose}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 rounded bg-red-600 text-white font-semibold hover:bg-red-700 transition-colors disabled:opacity-60"
              disabled={qtyInvalid}
            >
              Confirm Wastage
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddWastageModal;
