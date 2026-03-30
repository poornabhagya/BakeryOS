import { X, Info, Loader } from 'lucide-react';
import { useState } from 'react';
import { createPortal } from 'react-dom';
import apiClient from '../../services/api';

export interface AddProductCategoryModalProps {
    isOpen: boolean;
    onClose: () => void;
    onCategoryAdded?: () => void;
}

export function AddProductCategoryModal({ isOpen, onClose, onCategoryAdded }: AddProductCategoryModalProps) {
    const [categoryName, setCategoryName] = useState('');
    const [lowStockThreshold, setLowStockThreshold] = useState(10);
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    if (!isOpen) return null;

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setError(null);
        setIsLoading(true);

        try {
            const payload = {
                name: categoryName,
                type: 'Product' as const,
                low_stock_alert: lowStockThreshold,
                description: null,
            };

            const response = await apiClient.categories.create(payload);
            console.log('[Category Created]', response);

            // Reset form
            setCategoryName('');
            setLowStockThreshold(10);

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

    const newCategoryId = `#CAT-NEW`;

    // 2. WRAP IN createPortal
    return createPortal(
        <div className="fixed inset-0 z-[11000] bg-black/60 backdrop-blur-sm flex items-center justify-center">
            <div className="bg-white rounded-xl shadow-2xl w-full max-w-md mx-4 z-[11001]">
                {/* Header */}
                <div className="flex items-center justify-between p-6 border-b border-gray-200">
                    <div className="flex items-center gap-3">
                        <h3 className="text-gray-900 font-semibold">Add New Product Category</h3>
                        <span className="px-2 py-1 bg-orange-100 text-orange-700 text-xs font-medium rounded-full">
                            New
                        </span>
                    </div>
                    <button onClick={onClose} className="p-1 hover:bg-gray-100 rounded-lg transition-colors">
                        <X className="w-5 h-5 text-gray-500" />
                    </button>
                </div>

                {/* Body */}
                <form onSubmit={handleSubmit} className="p-6 space-y-6">
                    {/* Error Message */}
                    {error && (
                        <div className="p-4 bg-red-50 border border-red-200 rounded-lg">
                            <p className="text-sm text-red-700">{error}</p>
                        </div>
                    )}
                    <div>
                        <label className="block text-sm text-gray-700 mb-2">Category ID</label>
                        <input type="text" value={newCategoryId} disabled className="w-full px-3 py-2 border border-gray-300 rounded-lg bg-gray-100 text-gray-500" />
                    </div>

                    <div>
                        <label className="block text-sm text-gray-700 mb-2">Category Name</label>
                        <input
                            type="text"
                            value={categoryName}
                            onChange={(e) => setCategoryName(e.target.value)}
                            placeholder="e.g., Buns, Pastries"
                            disabled={isLoading}
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 disabled:opacity-50 disabled:cursor-not-allowed"
                            required
                        />
                    </div>

                    <div>
                        <label className="block text-sm text-gray-700 mb-2">Alert when quantity drops below:</label>
                        <input
                            type="number"
                            value={lowStockThreshold}
                            onChange={(e) => setLowStockThreshold(Number(e.target.value))}
                            disabled={isLoading}
                            min="0"
                            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-orange-500 disabled:opacity-50 disabled:cursor-not-allowed"
                        />
                    </div>

                    <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg flex items-start gap-3">
                        <Info className="w-5 h-5 text-blue-600 mt-0.5" />
                        <div className="text-sm text-blue-800">
                            <p>Low Stock Alert will trigger at <strong>{lowStockThreshold} qty</strong>.</p>
                        </div>
                    </div>

                    <div className="flex justify-end gap-3 pt-6 border-t border-gray-200">
                        <button type="button" onClick={onClose} disabled={isLoading} className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg font-medium disabled:opacity-50">Cancel</button>
                        <button 
                            type="submit" 
                            disabled={isLoading || !categoryName.trim()} 
                            className="px-4 py-2 bg-orange-500 hover:bg-orange-600 text-white rounded-lg font-medium disabled:opacity-50 flex items-center gap-2"
                        >
                            {isLoading && <Loader className="w-4 h-4 animate-spin" />}
                            {isLoading ? 'Saving...' : 'Save Category'}
                        </button>
                    </div>
                </form>
            </div>
        </div>,
        document.body // Force render to body
    );
}