import React from 'react';
import { createPortal } from 'react-dom';
import { AlertTriangle, X } from 'lucide-react';

export interface DeleteUserModalProps {
  open: boolean;
  onClose: () => void;
  onConfirm: () => void;
  userName: string;
}

const DeleteUserModal: React.FC<DeleteUserModalProps> = ({ open, onClose, onConfirm, userName }) => {
  if (!open) return null;

  return createPortal(
    <div 
      className="fixed inset-0 z-[120] bg-black/40 backdrop-blur-sm flex items-center justify-center p-4" 
      aria-modal="true" 
      role="dialog"
    >
      {/* Changes made:
        1. Removed 'w-full' and 'max-w-xs'
        2. Added 'w-[300px]' (Fixed width) to force it to be small.
      */}
      <div className="bg-white w-[300px] rounded-2xl shadow-2xl flex flex-col items-center relative overflow-hidden border border-red-100 animate-in fade-in zoom-in-95 duration-200">
        
        {/* Close Button */}
        <button
          onClick={onClose}
          className="absolute top-3 right-3 p-2 rounded-lg hover:bg-gray-100 text-gray-400 transition-colors"
          aria-label="Close"
        >
          <X className="w-5 h-5" />
        </button>

        {/* Icon */}
        <div className="mt-8 mb-4 flex items-center justify-center">
          <div className="rounded-full bg-red-100 p-4 flex items-center justify-center shadow-inner">
            <AlertTriangle className="w-10 h-10 text-red-600" />
          </div>
        </div>

        {/* Title */}
        <h2 className="text-xl font-bold text-red-700 mb-2 text-center">Delete User?</h2>

        {/* Message */}
        <p className="text-center text-gray-600 mb-8 px-6 text-sm leading-relaxed">
          Are you sure you want to remove <br/>
          <span className="font-bold text-gray-900 text-base">{userName}</span>?
        </p>

        {/* Buttons */}
        <div className="flex w-full justify-center gap-3 mb-6 px-6">
          <button
            onClick={onClose}
            className="flex-1 py-2 rounded-lg border border-gray-300 text-gray-700 bg-white hover:bg-gray-50 font-medium transition-colors text-sm"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            className="flex-1 py-2 rounded-lg bg-red-600 text-white font-bold hover:bg-red-700 transition-colors shadow-lg shadow-red-200 text-sm"
          >
            Delete
          </button>
        </div>
      </div>
    </div>,
    document.body
  );
};

export default DeleteUserModal;