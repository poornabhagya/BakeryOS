import React, { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { X, Trash2, FileQuestion, Loader2, AlertCircle } from 'lucide-react';
import DeleteConfirmationModal from './DeleteConfirmationModal';
import { useAuth } from '../../context/AuthContext';
import apiClient from '../../services/api';

export interface WastageReason {
  id: string;
  name: string;
  note: string;
}

interface ViewWastageReasonsModalProps {
  open: boolean;
  onClose: () => void;
  reasons: WastageReason[];
  onDelete: (id: string) => void;
}

export const ViewWastageReasonsModal: React.FC<ViewWastageReasonsModalProps> = ({ open, onClose, reasons, onDelete }) => {
  const { user } = useAuth();
  // 3. Permission Check: Only Manager can delete
  const isManager = user?.role === 'Manager';

  const [displayedReasons, setDisplayedReasons] = useState<WastageReason[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [deleteId, setDeleteId] = useState<string | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);
  
  // Fetch wastage reasons from backend
  useEffect(() => {
    if (!open) return;

    const fetchReasons = async () => {
      setIsLoading(true);
      setError(null);
      try {
        const data = await apiClient.wastageReason.getAll();
        // Map backend response to frontend interface
        // Backend returns: {id, reason_id, reason, description}
        // Frontend needs: {id, name, note}
        const mappedReasons = (data || []).map((reason: any) => ({
          id: reason.id?.toString() || '',
          name: reason.reason || reason.name || '',
          note: reason.description || reason.note || '',
        }));
        setDisplayedReasons(mappedReasons);
      } catch (err) {
        const errorMessage = err instanceof Error ? err.message : 'Failed to fetch wastage reasons';
        setError(errorMessage);
        console.error('Error fetching wastage reasons:', err);
      } finally {
        setIsLoading(false);
      }
    };

    fetchReasons();
  }, [open]);
  
  if (!open) return null;

  const finalReasons = displayedReasons && displayedReasons.length > 0 ? displayedReasons : reasons;

  const handleDelete = (id: string) => {
    setDeleteId(id);
    setDeleteError(null);
  };

  const handleConfirmDelete = async () => {
    if (!deleteId) return;

    setIsDeleting(true);
    setDeleteError(null);

    try {
      // Make DELETE request to backend
      await apiClient.wastageReason.delete(deleteId);

      // Remove the deleted reason from the list
      setDisplayedReasons((prev) => prev.filter((reason) => reason.id !== deleteId));

      // Call the parent onDelete callback for any additional cleanup
      onDelete(deleteId);

      // Close the delete confirmation modal
      setDeleteId(null);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to delete wastage reason';
      setDeleteError(errorMessage);
      console.error('Error deleting wastage reason:', err);
    } finally {
      setIsDeleting(false);
    }
  };

  const handleCloseDelete = () => {
    setDeleteId(null);
  };

  const getDeleteName = () => {
    const found = finalReasons.find(r => r.id === deleteId);
    return found ? found.name : '';
  };

  const modalContent = (
    <div className="fixed inset-0 z-[110] bg-black/40 backdrop-blur-sm flex items-center justify-center p-4" aria-modal="true" role="dialog">
      <div className="bg-white w-full max-w-2xl rounded-2xl shadow-2xl flex flex-col relative overflow-hidden border border-orange-100 animate-fade-in">
        {/* Header */}
        <div className="flex items-center justify-between px-6 py-4 border-b border-orange-100 bg-orange-50/60">
          <h3 className="text-lg font-bold text-orange-800">Wastage Reasons List</h3>
          <button onClick={onClose} className="p-2 rounded-lg hover:bg-orange-100 transition-colors" aria-label="Close">
            <X className="w-5 h-5 text-gray-400" />
          </button>
        </div>
        {/* Body */}
        <div className="flex-1 p-6 overflow-y-auto">
          {/* Loading State */}
          {isLoading ? (
            <div className="flex flex-col items-center justify-center py-12 text-gray-400">
              <Loader2 className="w-12 h-12 mb-3 text-orange-400 animate-spin" />
              <div className="text-lg font-semibold mb-1">Loading wastage reasons...</div>
            </div>
          ) : error ? (
            // Error State
            <div className="flex flex-col items-center justify-center py-12 text-red-500">
              <AlertCircle className="w-12 h-12 mb-3 text-red-400" />
              <div className="text-lg font-semibold mb-1">Error loading wastage reasons</div>
              <div className="text-sm text-red-400">{error}</div>
            </div>
          ) : finalReasons.length === 0 ? (
            // Empty State
            <div className="flex flex-col items-center justify-center py-12 text-gray-400">
              <FileQuestion className="w-12 h-12 mb-3 text-orange-300" />
              <div className="text-lg font-semibold mb-1">No wastage reasons defined yet.</div>
              <div className="text-sm text-gray-400">Add a new reason to get started.</div>
            </div>
          ) : (
            // Data State
            <div className="overflow-x-auto">
              <table className="w-full border-collapse text-sm">
                <thead>
                  <tr className="bg-gray-50 text-gray-600 sticky top-0 z-10">
                    <th className="px-3 py-2 font-semibold text-xs text-gray-400 w-32 text-left">ID</th>
                    <th className="px-3 py-2 font-semibold text-xs text-gray-700 text-left">Reason Name</th>
                    <th className="px-3 py-2 font-semibold text-xs text-gray-500 text-left">Note</th>
                    {/* 4. Hide Action Header if not Manager */}
                    {isManager && <th className="px-3 py-2 font-semibold text-xs text-gray-400 w-16 text-center">Action</th>}
                  </tr>
                </thead>
                <tbody>
                  {finalReasons.map((reason) => (
                    <tr key={reason.id} className="border-b last:border-b-0 hover:bg-orange-50/30 group">
                      <td className="px-3 py-2 text-xs text-gray-400 font-mono truncate max-w-[100px]">{reason.id}</td>
                      <td className="px-3 py-2 font-semibold text-gray-800">{reason.name}</td>
                      <td className="px-3 py-2 text-gray-600 truncate max-w-[200px]">{reason.note || <span className='italic text-gray-300'>—</span>}</td>
                      
                      {/* 5. Hide Delete Button Cell if not Manager */}
                      {isManager && (
                        <td className="px-3 py-2 text-center">
                          <button
                            onClick={() => handleDelete(reason.id)}
                            className="p-2 rounded hover:bg-red-50 group-hover:bg-red-50 text-red-500 hover:text-red-700 transition-colors"
                            title="Delete Reason"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </td>
                      )}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );

  return createPortal(
    <>
      {modalContent}
      <DeleteConfirmationModal
        isOpen={!!deleteId}
        onClose={handleCloseDelete}
        onConfirm={handleConfirmDelete}
        itemName={getDeleteName()}
        isLoading={isDeleting}
        title="Delete Wastage Reason"
        error={deleteError}
      />
    </>,
    document.body
  );
};