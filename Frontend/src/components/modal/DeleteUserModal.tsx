import React, { useState } from 'react';
import { createPortal } from 'react-dom';
import { AlertTriangle, X } from 'lucide-react';
import apiClient from '../../services/api';

export interface DeleteUserModalProps {
  open: boolean;
  onClose: () => void;
  onConfirm: (userId: number) => Promise<void>;
  userName: string;
  userId?: number;
}

const DeleteUserModal: React.FC<DeleteUserModalProps> = ({ open, onClose, onConfirm, userName, userId }) => {
  const [isDeleting, setIsDeleting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!open) return null;

  const handleDeleteClick = async () => {
    if (!userId) {
      setError('User ID not available');
      return;
    }

    setIsDeleting(true);
    setError(null);

    try {
      console.log(`[DeleteUserModal] Deactivating user ${userId} (${userName})`);
      
      // Use PATCH request instead of DELETE to avoid Content-Length header mismatch
      // Backend performs soft delete by setting is_active = false
      await apiClient.users.update(userId, { is_active: false });

      console.log(`[DeleteUserModal] User ${userId} deactivated successfully`);

      // Call parent callback to remove from UI and close modal
      await onConfirm(userId);

      onClose();
    } catch (err) {
      console.error('[DeleteUserModal] Error deactivating user:', err);
      const errorMsg = err instanceof Error ? err.message : 'Failed to delete user. Please try again.';
      setError(errorMsg);
    } finally {
      setIsDeleting(false);
    }
  };

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
          disabled={isDeleting}
          className="absolute top-3 right-3 p-2 rounded-lg hover:bg-gray-100 text-gray-400 transition-colors disabled:opacity-50"
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
        <p className="text-center text-gray-600 mb-4 px-6 text-sm leading-relaxed">
          Are you sure you want to remove <br/>
          <span className="font-bold text-gray-900 text-base">{userName}</span>?
        </p>

        {/* Error Message */}
        {error && (
          <div className="mx-6 mb-4 p-3 rounded-lg border border-red-300 bg-red-50 w-full">
            <p className="text-xs text-red-700">{error}</p>
          </div>
        )}

        {/* Buttons */}
        <div className="flex w-full justify-center gap-3 mb-6 px-6">
          <button
            onClick={onClose}
            disabled={isDeleting}
            className="flex-1 py-2 rounded-lg border border-gray-300 text-gray-700 bg-white hover:bg-gray-50 font-medium transition-colors text-sm disabled:opacity-60"
          >
            Cancel
          </button>
          <button
            onClick={handleDeleteClick}
            disabled={isDeleting}
            className="flex-1 py-2 rounded-lg bg-red-600 text-white font-bold hover:bg-red-700 transition-colors shadow-lg shadow-red-200 text-sm disabled:opacity-60 flex items-center justify-center gap-2"
          >
            {isDeleting ? (
              <>
                <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Deleting...
              </>
            ) : (
              'Delete'
            )}
          </button>
        </div>
      </div>
    </div>,
    document.body
  );
};

export default DeleteUserModal;