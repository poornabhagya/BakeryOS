import { X, Info, Loader } from 'lucide-react';
import { useState, useEffect } from 'react';
import { createPortal } from 'react-dom';
import apiClient from '../../../services/api';

interface IngredientCategoryData {
  id?: string;
  name: string;
  description?: string;
}

interface AddIngredientCategoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialData?: IngredientCategoryData | null;
  onCategoryAdded?: () => void;
}

export function AddIngredientCategoryModal({ isOpen, onClose, initialData, onCategoryAdded }: AddIngredientCategoryModalProps) {
  const [categoryName, setCategoryName] = useState('');
  const [description, setDescription] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (initialData) {
      setCategoryName(initialData.name);
      setDescription(initialData.description || '');
    } else {
      setCategoryName('');
      setDescription('');
      setError(null);
    }
  }, [initialData, isOpen]);

  if (!isOpen) return null;

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      const payload = {
        name: categoryName,
        type: 'Ingredient' as const,
        description: description,
        low_stock_alert: null,
      };

      const response = await apiClient.categories.create(payload);
      console.log('[Category Created]', response);

      // Reset form
      setCategoryName('');
      setDescription('');

      // Trigger parent callback to refresh categories list
      if (onCategoryAdded) {
        onCategoryAdded();
      }

      // Close modal
      onClose();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to create category';
      setError(errorMessage);
      console.error('[Category Creation Error]', err);
    } finally {
      setIsLoading(false);
    }
  };

  return createPortal(
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-[100]">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-md mx-4">
        {/* Modal Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <h3 className="text-gray-900 font-semibold">Add New Ingredient Category</h3>
            <span className="px-2 py-1 bg-orange-100 text-orange-700 text-xs font-medium rounded-full">
              Ingredient
            </span>
          </div>
          <button
            onClick={onClose}
            className="p-1 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Modal Body */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Error Message */}
          {error && (
            <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}
          {/* Category Name */}
          <div>
            <label className="block text-sm text-gray-700 mb-2">
              Category Name
            </label>
            <input
              type="text"
              value={categoryName}
              onChange={(e) => setCategoryName(e.target.value)}
              placeholder="e.g., Flours, Dairy"
              disabled={isLoading}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 disabled:opacity-50 disabled:cursor-not-allowed"
              required
            />
          </div>

          {/* Description Field */}
          <div>
            <label className="block text-sm text-gray-700 mb-2">
              Description
            </label>
            <textarea
              value={description}
              onChange={e => setDescription(e.target.value)}
              placeholder="Enter a description for this category"
              disabled={isLoading}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 disabled:opacity-50 disabled:cursor-not-allowed"
              rows={3}
            />
          </div>

          {/* Modal Footer */}
          <div className="flex justify-end gap-3 pt-6 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              disabled={isLoading}
              className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg font-medium transition-colors disabled:opacity-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={isLoading || !categoryName.trim()}
              className="px-4 py-2 bg-orange-500 hover:bg-orange-600 text-white rounded-lg font-medium transition-colors disabled:opacity-50 flex items-center gap-2"
            >
              {isLoading && <Loader className="w-4 h-4 animate-spin" />}
              {isLoading ? 'Saving...' : 'Save Category'}
            </button>
          </div>
        </form>
      </div>
    </div>,
    document.body
  );
}