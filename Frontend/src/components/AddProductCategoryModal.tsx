import { X, Info } from 'lucide-react';
import { useState, useEffect } from 'react';

interface CategoryData {
  id?: string;
  name: string;
  lowStockThreshold: number;
}

interface AddProductCategoryModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialData?: CategoryData | null;
  onSave?: (data: { name: string; lowStockThreshold: number }) => void;
}

export function AddProductCategoryModal({ isOpen, onClose, initialData, onSave }: AddProductCategoryModalProps) {
  const [categoryName, setCategoryName] = useState('');
  const [lowStockThreshold, setLowStockThreshold] = useState(10);

  useEffect(() => {
    if (initialData) {
      setCategoryName(initialData.name);
      setLowStockThreshold(initialData.lowStockThreshold);
    } else {
      setCategoryName('');
      setLowStockThreshold(10);
    }
  }, [initialData, isOpen]);

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const data = { name: categoryName, lowStockThreshold };
    if (onSave) {
      onSave(data);
    } else {
      console.log('Category added:', data);
      onClose();
    }
  };

  const categoryId = initialData?.id || '#CAT-2024'; // Mock auto-generated ID

  const isEditing = !!initialData;

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-[100]">
      <div className="bg-white rounded-xl shadow-2xl w-full max-w-md mx-4">
        {/* Modal Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div className="flex items-center gap-3">
            <h3 className="text-gray-900 font-semibold">Add New Product Category</h3>
            <span className="px-2 py-1 bg-orange-100 text-orange-700 text-xs font-medium rounded-full">
              Product
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
          {/* Category ID */}
          <div>
            <label className="block text-sm text-gray-700 mb-2">
              Category ID
            </label>
            <input
              type="text"
              value={categoryId}
              disabled
              className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-100 text-gray-500 cursor-not-allowed"
            />
          </div>

          {/* Category Name */}
          <div>
            <label className="block text-sm text-gray-700 mb-2">
              Category Name
            </label>
            <input
              type="text"
              value={categoryName}
              onChange={(e) => setCategoryName(e.target.value)}
              placeholder="e.g., Buns, Pastries"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
              required
            />
          </div>

          {/* Stock Settings Section */}
          <div className="border-t border-gray-200 pt-6">
            <h4 className="text-lg font-medium text-gray-900 mb-2">Stock Status Thresholds</h4>
            <p className="text-sm text-gray-600 mb-4">
              Define when items in this category should be marked as Low Stock.
            </p>

            {/* Low Stock Threshold */}
            <div>
              <label className="block text-sm text-gray-700 mb-2">
                Alert when quantity drops below or equals:
              </label>
              <input
                type="number"
                value={lowStockThreshold}
                onChange={(e) => setLowStockThreshold(Number(e.target.value))}
                min="0"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
              />
            </div>

            {/* Logic Summary Box */}
            <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="flex items-start gap-3">
                <Info className="w-5 h-5 text-blue-600 mt-0.5" />
                <div className="text-sm text-blue-800">
                  <p className="font-medium mb-2">Based on your setting (Qty ≤ {lowStockThreshold}):</p>
                  <ul className="space-y-1">
                    <li>• <strong>Out of Stock:</strong> 0 qty</li>
                    <li>• <strong>Low Stock:</strong> 1 to {lowStockThreshold} qty (Alert Triggered)</li>
                    <li>• <strong>In Stock:</strong> More than {lowStockThreshold} qty</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          {/* Modal Footer */}
          <div className="flex justify-end gap-3 pt-6 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg font-medium transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-orange-500 hover:bg-orange-600 text-white rounded-lg font-medium transition-colors"
            >
              {isEditing ? 'Update Category' : 'Save Category'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}