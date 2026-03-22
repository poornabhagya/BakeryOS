import React, { useState } from 'react';
import { createPortal } from 'react-dom';
import { X, Trash2, FileQuestion } from 'lucide-react';
import DeleteConfirmationModal from './DeleteConfirmationModal';
import { useAuth } from '../../context/AuthContext'; // 1. Auth Import

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

const DUMMY_REASONS: WastageReason[] = [
  { id: 'wastage_abc123', name: 'Expired', note: 'Product expired before sale.' },
  { id: 'wastage_def456', name: 'Damaged', note: 'Damaged during transport.' },
  { id: 'wastage_ghi789', name: 'Spoiled', note: 'Spoiled due to improper storage.' },
];

export const ViewWastageReasonsModal: React.FC<ViewWastageReasonsModalProps> = ({ open, onClose, reasons, onDelete }) => {
  const { user } = useAuth(); // 2. Get User
  // 3. Permission Check: Only Manager can delete
  const isManager = user?.role === 'Manager';

  const [deleteId, setDeleteId] = useState<string | null>(null);
  
  if (!open) return null;

  const displayReasons = reasons && reasons.length > 0 ? reasons : DUMMY_REASONS;

  const handleDelete = (id: string) => {
    setDeleteId(id);
  };

  const handleConfirmDelete = () => {
    if (deleteId) {
      onDelete(deleteId);
      setDeleteId(null);
    }
  };

  const handleCloseDelete = () => {
    setDeleteId(null);
  };

  const getDeleteName = () => {
    const found = displayReasons.find(r => r.id === deleteId);
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
          {displayReasons.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-gray-400">
              <FileQuestion className="w-12 h-12 mb-3 text-orange-300" />
              <div className="text-lg font-semibold mb-1">No wastage reasons defined yet.</div>
              <div className="text-sm text-gray-400">Add a new reason to get started.</div>
            </div>
          ) : (
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
                  {displayReasons.map((reason) => (
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
      />
    </>,
    document.body
  );
};