import React, { useState } from "react";
import { AlertTriangle, X } from "lucide-react";

interface AddProductWastageModalProps {
  open: boolean;
  onClose: () => void;
  productData: {
    id: string;
    name: string;
    currentStock: number;
    batchId?: string;
  } | null;
  onConfirm: (data: { productId: string; quantity: number; reason: string; note: string }) => void;
}

const REASONS = [
  "Expired",
  "Damaged / Broken",
  "Spoiled / Quality Issue",
  "Spillage",
  "Theft / Missing",
  "Other",
];

export const AddProductWastageModal: React.FC<AddProductWastageModalProps> = ({
  open,
  onClose,
  productData,
  onConfirm,
}) => {
  const [quantity, setQuantity] = useState("");
  const [reason, setReason] = useState(REASONS[0]);
  const [note, setNote] = useState("");
  const [touched, setTouched] = useState(false);

  if (!open || !productData) return null;

  const qtyNum = Number(quantity);
  const qtyInvalid =
    quantity === "" ||
    isNaN(qtyNum) ||
    qtyNum <= 0 ||
    !Number.isInteger(qtyNum) ||
    qtyNum > productData.currentStock;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setTouched(true);
    if (!qtyInvalid) {
      onConfirm({
        productId: productData.id,
        quantity: qtyNum,
        reason,
        note,
      });
      setQuantity("");
      setReason(REASONS[0]);
      setNote("");
      setTouched(false);
      onClose();
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-md">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-3 bg-red-50 border-b border-red-100 rounded-t-xl relative">
          <div className="flex items-center gap-2">
            <AlertTriangle className="w-5 h-5 text-red-600" />
            <h2 className="text-base font-semibold text-red-900">Report Product Wastage</h2>
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
          {productData.batchId && (
            <div>
              <div className="text-xs text-gray-500 uppercase">Batch ID</div>
              <div className="font-mono text-gray-700 text-sm">{productData.batchId}</div>
            </div>
          )}
          <div>
            <div className="text-xs text-gray-500">Product</div>
            <div className="font-medium text-gray-900">{productData.name}</div>
          </div>
          <div>
            <span className="text-xs text-gray-500">Current Stock</span>
            <span className="ml-2 text-sm font-bold text-green-700 bg-green-50 px-2 py-1 rounded-md inline-block">
              {productData.currentStock} Nos
            </span>
          </div>
        </div>
        {/* Form */}
        <form onSubmit={handleSubmit} className="px-6 pt-2 pb-0 space-y-4">
          {/* Quantity */}
          <div>
            <label className="block font-medium text-gray-700 mb-1">Wastage Quantity</label>
            <div className={`flex items-center rounded border ${qtyInvalid && touched ? 'border-red-500' : 'border-gray-300'} bg-white focus-within:ring-2 focus-within:ring-red-500`}>
              <input
                type="number"
                min={1}
                step={1}
                value={quantity}
                onChange={e => setQuantity(e.target.value.replace(/[^\d]/g, ''))}
                onBlur={() => setTouched(true)}
                className="w-24 px-3 py-2 rounded-l outline-none bg-transparent text-gray-900"
                required
              />
              <span className="px-3 py-2 text-gray-400 text-sm select-none bg-gray-50 rounded-r border-l border-gray-200">Nos</span>
            </div>
            {touched && qtyNum > productData.currentStock && (
              <div className="flex items-center gap-1 text-xs text-red-600 mt-1">
                <AlertTriangle className="w-4 h-4" />
                Error: Cannot waste more than available stock
              </div>
            )}
            {touched && (!quantity || qtyNum <= 0) && (
              <div className="flex items-center gap-1 text-xs text-red-600 mt-1">
                <AlertTriangle className="w-4 h-4" />
                Error: Enter a valid quantity
              </div>
            )}
            {touched && quantity && !isNaN(qtyNum) && !Number.isInteger(qtyNum) && (
              <div className="flex items-center gap-1 text-xs text-red-600 mt-1">
                <AlertTriangle className="w-4 h-4" />
                Error: Quantity must be a whole number
              </div>
            )}
          </div>
          {/* Reason */}
          <div>
            <label className="block font-medium text-gray-700 mb-1">Reason</label>
            <select
              value={reason}
              onChange={e => setReason(e.target.value)}
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
              onChange={e => setNote(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-red-500 focus:border-red-500 text-gray-900"
              rows={2}
              placeholder="E.g. Dropped during delivery"
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

export default AddProductWastageModal;
