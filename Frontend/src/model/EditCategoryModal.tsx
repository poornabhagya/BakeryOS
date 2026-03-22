import React, { useState, useEffect } from "react";
import { createPortal } from "react-dom";
import { X } from "lucide-react";

interface EditCategoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialData?: {
    id: string;
    name: string;
    lowStockThreshold: number;
  } | null;
  onSave: (data: { id: string; name: string; lowStockThreshold: number }) => void;
}

const EditCategoryModal: React.FC<EditCategoryModalProps> = ({ isOpen, onClose, initialData, onSave }) => {
  const [categoryName, setCategoryName] = useState("");
  const [lowStockThreshold, setLowStockThreshold] = useState(10);

  useEffect(() => {
    if (initialData) {
      setCategoryName(initialData.name);
      setLowStockThreshold(initialData.lowStockThreshold);
    } else {
      setCategoryName("");
      setLowStockThreshold(10);
    }
  }, [initialData, isOpen]);

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!initialData) return;
    onSave({
      id: initialData.id,
      name: categoryName,
      lowStockThreshold,
    });
  };

  return createPortal(
    <div className="fixed inset-0 z-[20000] flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 z-[20001]">
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h3 className="text-orange-900 font-extrabold text-2xl">Edit Category</h3>
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>
        <form onSubmit={handleSubmit} className="p-6 flex flex-col gap-5">
          <div>
            <label className="block text-xs font-semibold mb-1 text-orange-700">Category Name</label>
            <input
              type="text"
              value={categoryName}
              onChange={e => setCategoryName(e.target.value)}
              className="w-full px-3 py-2 border border-orange-200 rounded-lg focus:ring-2 focus:ring-orange-400 focus:border-orange-400"
              required
            />
          </div>
          <div>
            <label className="block text-xs font-semibold mb-1 text-orange-700">Low Stock Threshold</label>
            <input
              type="number"
              value={lowStockThreshold}
              onChange={e => setLowStockThreshold(Number(e.target.value))}
              min="0"
              className="w-full px-3 py-2 border border-orange-200 rounded-lg focus:ring-2 focus:ring-orange-400 focus:border-orange-400"
              required
            />
          </div>
          <div className="flex justify-end gap-3 pt-6 border-t border-gray-200">
            <button type="button" onClick={onClose} className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg font-medium">Cancel</button>
            <button type="submit" className="px-4 py-2 bg-orange-500 hover:bg-orange-600 text-white rounded-lg font-medium">Save Changes</button>
          </div>
        </form>
      </div>
    </div>,
    document.body
  );
};

export default EditCategoryModal;
