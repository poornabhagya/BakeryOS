import React, { useState, useEffect } from "react";
import { createPortal } from "react-dom"; // 1. IMPORT THIS
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

export const EditCategoryModal: React.FC<EditCategoryModalProps> = ({ isOpen, onClose, initialData, onSave }) => {
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

  // 2. WRAP EVERYTHING IN createPortal(..., document.body)
  return createPortal(
    <div className="fixed inset-0 z-[20000] flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 z-[20001]">
        {/* Modal Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h3 className="text-orange-900 font-extrabold text-2xl">Edit Category</h3>
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>
        {/* Modal Body */}
        <form onSubmit={handleSubmit} className="p-6 flex flex-col gap-5">
          <div>
            <label className="block text-xs font-semibold mb-1 text-orange-700">Category Name</label>
            <input
              type="text"
              value={categoryName}
              onChange={e => setCategoryName(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
              required
              placeholder="Enter category name"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold mb-1 text-orange-700">Low Stock Threshold</label>
            <input
              type="number"
              min={1}
              value={lowStockThreshold}
              onChange={e => setLowStockThreshold(Number(e.target.value))}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
              required
              placeholder="Enter low stock threshold"
            />
          </div>
          <div className="flex gap-3 mt-2">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-2 rounded-lg bg-gray-100 text-gray-700 font-bold shadow hover:bg-gray-200 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="flex-1 py-2 rounded-lg bg-orange-500 text-white font-bold shadow hover:bg-orange-600 transition-colors"
            >
              Save Changes
            </button>
          </div>
        </form>
      </div>
    </div>,
    document.body // This forces the modal to render at the end of the <body> tag
  );
};

export default EditCategoryModal;