
import React from "react";
import { Trash2, CheckCircle2 } from "lucide-react";

interface DeleteConfirmationModalProps {
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  itemName: string;
  onConfirmOnly?: () => void; // Optional, for confirm only
}



export const DeleteConfirmationModal: React.FC<DeleteConfirmationModalProps> = ({ isOpen, onClose, onConfirm, itemName, onConfirmOnly }) => {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 backdrop-blur-sm">
      {/* Overlay animation */}
      <div className="absolute inset-0" aria-hidden="true"></div>
      <div
        className="relative z-10 w-full max-w-md mx-auto p-0"
        style={{ pointerEvents: 'auto' }}
      >
        <div
          className="animate-fade-in-scale bg-white rounded-2xl shadow-xl border border-red-100 px-8 py-8 flex flex-col items-center justify-center min-w-[340px]"
        >
          {/* Icon in a soft circle */}
          <div className="mb-3 flex justify-center w-full">
            <span className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-red-100 border-2 border-red-200 shadow">
              <Trash2 className="w-8 h-8 text-red-500" />
            </span>
          </div>
          {/* Title */}
          <h2 className="text-xl font-extrabold text-gray-900 mb-1 tracking-tight text-center w-full">Delete Product</h2>
          {/* Subtle divider */}
          <div className="w-10 h-[3px] bg-red-200 rounded-full mx-auto mb-4"></div>
          {/* Message */}
          <p className="text-gray-700 mb-5 text-base leading-relaxed text-center w-full">
            Are you sure you want to delete <span className="font-bold text-red-600">{itemName}</span>?
          </p>
          <p className="text-xs text-gray-400 font-medium text-center mb-6">This action cannot be undone.</p>
          {/* Buttons */}
          <div className="flex flex-row gap-3 w-full items-center justify-center mt-2">
            <button
              onClick={onClose}
              className="flex-1 max-w-[120px] px-4 py-2 rounded-lg border border-gray-300 text-gray-700 bg-white hover:bg-gray-100 font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-gray-300"
              type="button"
            >
              Cancel
            </button>
            <button
              onClick={onConfirm}
              className="flex-1 max-w-[120px] px-4 py-2 rounded-lg bg-red-500 text-white font-bold shadow hover:bg-red-600 transition-colors focus:outline-none focus:ring-2 focus:ring-red-300"
              type="button"
            >
              Delete
            </button>
            <button
              onClick={onConfirmOnly ? onConfirmOnly : onConfirm}
              className="flex-1 max-w-[120px] px-4 py-2 rounded-lg bg-green-500 text-white font-bold shadow hover:bg-green-600 transition-colors flex items-center justify-center gap-2 focus:outline-none focus:ring-2 focus:ring-green-300"
              type="button"
            >
              <CheckCircle2 className="w-5 h-5" /> Confirm
            </button>
          </div>
        </div>
      </div>
      {/* Animations */}
      <style>{`
        @keyframes fade-in-scale {
          0% { opacity: 0; transform: scale(0.95); }
          100% { opacity: 1; transform: scale(1); }
        }
        .animate-fade-in-scale {
          animation: fade-in-scale 0.25s cubic-bezier(0.4,0,0.2,1);
        }
        @keyframes pop {
          0% { transform: scale(0.7); opacity: 0; }
          80% { transform: scale(1.1); opacity: 1; }
          100% { transform: scale(1); opacity: 1; }
        }
        .animate-pop {
          animation: pop 0.35s cubic-bezier(0.4,0,0.2,1);
        }
      `}</style>
    </div>
  );
};

export default DeleteConfirmationModal;
