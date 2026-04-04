import React, { useState, useEffect } from "react";
import { AlertTriangle, X } from "lucide-react";
import apiClient from "../../services/api";

interface AddProductWastageModalProps {
  open: boolean;
  onClose: () => void;
  productData: {
    id: number;
    name: string;
    currentStock: number;
    unitCost: number | string;
    batchId?: string;
    batchIdNumeric?: number;  // Numeric batch ID
  } | null;
  onConfirm: (data: { productId: number; quantity: number; reason: string; note: string }) => Promise<void> | void;
}

interface WastageReason {
  id: number;
  reason: string;
  reason_id: string;
  description?: string;
}

export const AddProductWastageModal: React.FC<AddProductWastageModalProps> = ({
  open,
  onClose,
  productData,
  onConfirm,
}) => {
  const [quantity, setQuantity] = useState("");
  const [reason, setReason] = useState("");
  const [note, setNote] = useState("");
  const [touched, setTouched] = useState(false);
  
  // State for fetching wastage reasons
  const [wastageReasons, setWastageReasons] = useState<WastageReason[]>([]);
  const [loadingReasons, setLoadingReasons] = useState(false);
  const [errorReasons, setErrorReasons] = useState<string | null>(null);
  
  // State for form submission
  const [submitting, setSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);

  // Fetch wastage reasons when modal opens
  useEffect(() => {
    if (open && wastageReasons.length === 0) {
      fetchWastageReasons();
    }
  }, [open]);

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

  if (!open || !productData) return null;

  // Ensure currentStock is a valid number
  const currentStock = Number(productData.currentStock) || 0;
  const qtyNum = Number(quantity);
  const qtyInvalid =
    quantity === "" ||
    isNaN(qtyNum) ||
    qtyNum <= 0 ||
    !Number.isInteger(qtyNum) ||
    qtyNum > currentStock;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setTouched(true);
    setSubmitError(null);
    
    // Validate quantity
    if (qtyInvalid) {
      if (qtyNum > currentStock) {
        setSubmitError(`Wastage quantity cannot exceed current stock (${currentStock} available)`);
      } else if (quantity === "" || qtyNum <= 0) {
        setSubmitError("Please enter a valid wastage quantity");
      } else if (!Number.isInteger(qtyNum)) {
        setSubmitError("Wastage quantity must be a whole number");
      }
      return;
    }
    
    // Validate reason
    if (!reason) {
      setSubmitError("Please select a wastage reason");
      return;
    }
    
    try {
      setSubmitting(true);
      
      // Find the reason_id (database ID) from the selected reason text
      const selectedReason = wastageReasons.find(r => r.reason === reason);
      
      // Make API request to create wastage record
      const wastagePayload: any = {
        product_id: productData.id,
        quantity: qtyNum.toString(),
        unit_cost: productData.unitCost.toString(),
        reason_id: selectedReason?.id,
        notes: note.trim() || null,
        reported_by: null, // Backend will set this to current user
      };
      
      // Include batch_id if available
      if (productData.batchIdNumeric) {
        wastagePayload.batch_id = productData.batchIdNumeric;
      }
      
      const response = await apiClient.productWastages.create(wastagePayload);
      
      // Success - call onConfirm callback and close modal
      await onConfirm({
        productId: productData.id as number,
        quantity: qtyNum,
        reason,
        note,
      });
      
      // Reset form
      setQuantity("");
      setReason(wastageReasons.length > 0 ? wastageReasons[0].reason : "");
      setNote("");
      setTouched(false);
      setSubmitError(null);
      onClose();
    } catch (error: any) {
      console.error('Failed to submit wastage:', error);
      // Extract error message from response
      const errorMsg = error?.response?.data?.detail ||
                      error?.response?.data?.quantity?.[0] ||
                      error?.response?.data?.non_field_errors?.[0] ||
                      "Failed to submit wastage report. Please try again.";
      setSubmitError(errorMsg);
    } finally {
      setSubmitting(false);
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
            className="absolute right-4 top-3 text-gray-400 hover:text-red-500 transition-colors disabled:opacity-60"
            onClick={onClose}
            aria-label="Close"
            disabled={submitting}
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
              {currentStock} Nos
            </span>
          </div>
        </div>
        
        {/* Submit Error Message */}
        {submitError && (
          <div className="mx-6 mt-4 p-3 bg-red-50 border border-red-300 rounded-lg flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
            <div>
              <p className="font-medium text-red-900 text-sm">{submitError}</p>
            </div>
          </div>
        )}
        
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
                disabled={submitting}
              />
              <span className="px-3 py-2 text-gray-400 text-sm select-none bg-gray-50 rounded-r border-l border-gray-200">Nos</span>
            </div>
            {touched && qtyNum > currentStock && (
              <div className="flex items-center gap-1 text-xs text-red-600 mt-1">
                <AlertTriangle className="w-4 h-4" />
                Error: Cannot waste more than available stock ({currentStock})
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
                onChange={e => setReason(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-red-500 focus:border-red-500 text-gray-900 bg-white"
                required
                disabled={wastageReasons.length === 0 || submitting}
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
              onChange={e => setNote(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded focus:ring-2 focus:ring-red-500 focus:border-red-500 text-gray-900"
              rows={2}
              placeholder="E.g. Dropped during delivery"
              disabled={submitting}
            />
          </div>
          {/* Footer */}
          <div className="flex justify-end gap-2 pt-4 border-t border-gray-100 mt-6">
            <button
              type="button"
              className="px-4 py-2 rounded bg-white border border-gray-300 text-gray-700 font-semibold hover:bg-gray-50 transition-colors disabled:opacity-60"
              onClick={onClose}
              disabled={submitting}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 rounded bg-red-600 text-white font-semibold hover:bg-red-700 transition-colors disabled:opacity-60"
              disabled={qtyInvalid || submitting}
            >
              {submitting ? "Submitting..." : "Confirm Wastage"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default AddProductWastageModal;