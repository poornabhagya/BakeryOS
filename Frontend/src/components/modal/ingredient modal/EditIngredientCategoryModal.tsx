import React, { useState, useEffect } from "react";
import { createPortal } from "react-dom";
import { X, Loader } from "lucide-react";
import apiClient from "../../../services/api";

interface EditIngredientCategoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialData?: {
    id: number;
    name: string;
    description?: string;
  } | null;
  onSave?: (data: { id: number; name: string; description?: string }) => void;
  onCategoryUpdated?: () => void;
}

export const EditIngredientCategoryModal: React.FC<EditIngredientCategoryModalProps> = ({ 
  isOpen, 
  onClose, 
  initialData, 
  onSave,
  onCategoryUpdated 
}) => {
  const [categoryName, setCategoryName] = useState("");
  const [description, setDescription] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (initialData) {
      setCategoryName(initialData.name);
      setDescription(initialData.description || "");
      setError(null);
    } else {
      setCategoryName("");
      setDescription("");
      setError(null);
    }
  }, [initialData, isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!initialData) return;

    setError(null);
    setIsLoading(true);

    try {
      // Explicit payload mapping: Frontend state → Backend snake_case field names
      // categoryName (state) → name (backend field)
      // description (state) → description (backend field - already matches)
      const payload = {
        name: categoryName,            // Maps: categoryName (React state) → name (Django model field)
        description: description,      // Maps: description (React state) → description (Django model field)
      };

      await apiClient.categories.update(initialData.id, payload);

      // Call callback as backup for UI update
      if (onSave) {
        onSave({
          id: initialData.id,
          name: categoryName,
          description,
        });
      }

      // Trigger parent refresh
      if (onCategoryUpdated) {
        onCategoryUpdated();
      }

      onClose();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to update category';
      setError(errorMessage);
      console.error('[Category Update Error]', err);
    } finally {
      setIsLoading(false);
    }
  };

  return createPortal(
    <div className="fixed inset-0 z-[20000] flex items-center justify-center bg-black/60 backdrop-blur-sm">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-md mx-4 z-[20001]">
        {/* Modal Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h3 className="text-orange-900 font-extrabold text-2xl">Edit Category</h3>
          <button
            onClick={onClose}
            disabled={isLoading}
            className="p-1 hover:bg-gray-100 rounded-lg transition-colors disabled:opacity-50"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>
        {/* Modal Body */}
        <form onSubmit={handleSubmit} className="p-6 flex flex-col gap-5">
          {/* Error Message */}
          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          <div>
            <label className="block text-xs font-semibold mb-1 text-orange-700">Category Name</label>
            <input
              type="text"
              value={categoryName}
              onChange={e => setCategoryName(e.target.value)}
              disabled={isLoading}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 disabled:opacity-50 disabled:cursor-not-allowed"
              required
              placeholder="Enter category name"
            />
          </div>
          <div>
            <label className="block text-xs font-semibold mb-1 text-orange-700">Description</label>
            <textarea
              value={description}
              onChange={e => setDescription(e.target.value)}
              disabled={isLoading}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 disabled:opacity-50 disabled:cursor-not-allowed"
              placeholder="Enter description"
              rows={3}
            />
          </div>
          <div className="flex gap-3 mt-2">
            <button
              type="button"
              onClick={onClose}
              disabled={isLoading}
              className="flex-1 py-2 rounded-lg bg-gray-100 text-gray-700 font-bold shadow hover:bg-gray-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading}
              className="flex-1 py-2 rounded-lg bg-orange-500 text-white font-bold shadow hover:bg-orange-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isLoading && <Loader className="w-4 h-4 animate-spin" />}
              {isLoading ? "Saving..." : "Save Changes"}
            </button>
          </div>
        </form>
      </div>
    </div>,
    document.body
  );
};

export default EditIngredientCategoryModal;
