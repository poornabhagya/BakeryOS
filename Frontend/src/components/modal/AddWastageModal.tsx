

import React, { useState, useEffect } from "react";
import { AlertTriangle, X } from 'lucide-react';
import apiClient from '../../services/api';
import { formatQuantityForDisplay } from '../../utils/conversions';


interface AddWastageModalProps {
  isOpen: boolean;
  onClose: () => void;
  batchData: {
    batchID: string;
    ingredientName: string;
    currentQty: number;
    unit: string;
    trackingType?: string;
    expiryDate: string;
  };
  onConfirm: (wastage: {
    batchID: string;
    quantity: number;
    reason: string;
    note?: string;
  }) => Promise<void> | void;
}

interface WastageReason {
  id: number;
  reason: string;
  reason_id: string;
  description?: string;
}

export const AddWastageModal: React.FC<AddWastageModalProps> = ({
  isOpen,
  onClose,
  batchData,
  onConfirm,
}) => {
  const [quantity, setQuantity] = useState<number | "">("");
  const [selectedUnit, setSelectedUnit] = useState('kg');
  const [reason, setReason] = useState("");
  const [note, setNote] = useState("");
  const [touched, setTouched] = useState(false);
  
  // State for fetching wastage reasons
  const [wastageReasons, setWastageReasons] = useState<WastageReason[]>([]);
  const [loadingReasons, setLoadingReasons] = useState(false);
  const [errorReasons, setErrorReasons] = useState<string | null>(null);

  // Fetch wastage reasons when modal opens
  useEffect(() => {
    if (isOpen && wastageReasons.length === 0) {
      fetchWastageReasons();
    }
  }, [isOpen]);

  const fetchWastageReasons = async () => {
    try {
      setLoadingReasons(true);
      setErrorReasons(null);
      const reasons = await apiClient.wastageReason.getAll();
      const manualReasons = (reasons || []).filter(
        (r: WastageReason) => String(r.reason || '').trim().toLowerCase() !== 'expired'
      );
      
      if (manualReasons.length > 0) {
        setWastageReasons(manualReasons);
        // Set the first reason as default
        setReason(manualReasons[0].reason);
      } else {
        setWastageReasons([]);
        setErrorReasons("No manual wastage reasons available");
      }
    } catch (error) {
      console.error('Failed to fetch wastage reasons:', error);
      setErrorReasons("Failed to load wastage reasons");
    } finally {
      setLoadingReasons(false);
    }
  };

  const trackingType = batchData.trackingType || 'Weight';

  const getUnitOptions = (type: string) => {
    if (type === 'Volume') return ['L', 'ml'];
    if (type === 'Count') return ['nos'];
    return ['kg', 'g'];
  };

  const convertToBaseUnit = (qty: number, unit: string, type: string): number => {
    if (type === 'Weight') return unit === 'kg' ? qty * 1000 : qty;
    if (type === 'Volume') return unit === 'L' ? qty * 1000 : qty;
    return qty;
  };

  const convertFromBaseUnit = (qty: number, unit: string, type: string): number => {
    if (type === 'Weight') return unit === 'kg' ? qty / 1000 : qty;
    if (type === 'Volume') return unit === 'L' ? qty / 1000 : qty;
    return qty;
  };

  useEffect(() => {
    const defaultUnit = getUnitOptions(trackingType)[0];
    setSelectedUnit(defaultUnit);
  }, [trackingType, isOpen]);

  const normalizedQuantity = typeof quantity === 'number' ? quantity : 0;
  const quantityInBaseUnit = convertToBaseUnit(normalizedQuantity, selectedUnit, trackingType);
  const maxInSelectedUnit = convertFromBaseUnit(batchData.currentQty || 0, selectedUnit, trackingType);

  const qtyInvalid =
    quantity === "" ||
    quantity <= 0 ||
    (typeof quantity === "number" && quantityInBaseUnit > batchData.currentQty);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setTouched(true);
    if (!qtyInvalid && typeof quantity === "number") {
      try {
        await onConfirm({
          batchID: batchData.batchID,
          quantity: quantityInBaseUnit,
          reason,
          note: note.trim() ? note : undefined,
        });

        setQuantity("");
        setReason(wastageReasons.length > 0 ? wastageReasons[0].reason : "");
        setNote("");
        setTouched(false);
        onClose();
      } catch (error) {
        // Parent handles user-facing error message; keep modal open for correction/retry.
        console.error('Failed to confirm wastage:', error);
      }
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
              {formatQuantityForDisplay(batchData.currentQty, trackingType)}
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
                min={0}
                max={maxInSelectedUnit}
                step={selectedUnit === 'nos' ? 1 : 0.01}
                value={quantity}
                onChange={(e) => setQuantity(e.target.value === "" ? "" : Number(e.target.value))}
                onBlur={() => setTouched(true)}
                className="w-24 px-3 py-2 rounded-l outline-none bg-transparent text-gray-900"
                required
              />
              <select
                value={selectedUnit}
                onChange={(e) => setSelectedUnit(e.target.value)}
                className="px-3 py-2 text-gray-600 text-sm select-none bg-gray-50 rounded-r border-l border-gray-200 outline-none"
              >
                {getUnitOptions(trackingType).map((unit) => (
                  <option key={unit} value={unit}>{unit}</option>
                ))}
              </select>
            </div>
            {touched && typeof quantity === "number" && quantityInBaseUnit > batchData.currentQty && (
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
            
            {loadingReasons ? (
              <div className="w-full px-3 py-2 border border-gray-300 rounded text-gray-500 bg-gray-50">
                Loading reasons...
              </div>
            ) : errorReasons ? (
              <div className="flex items-center gap-2 w-full px-3 py-2 border border-red-300 rounded bg-red-50 text-red-600 text-sm">
                <AlertTriangle className="w-4 h-4 flex-shrink-0" />
                {errorReasons}
              </div>
            ) : (
              <select
                value={reason}
                onChange={(e) => setReason(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-red-500 focus:border-red-500 text-gray-900 bg-white"
                required
                disabled={wastageReasons.length === 0}
              >
                {wastageReasons.length === 0 ? (
                  <option>No reasons available</option>
                ) : (
                  wastageReasons.map((r) => (
                    <option key={r.id} value={r.reason}>
                      {r.reason}
                    </option>
                  ))
                )}
              </select>
            )}
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
